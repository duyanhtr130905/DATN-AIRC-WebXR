"""Opt-in sessions for the local synthetic scene."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.visitor_guard import (
    LOOPBACK_DATABASE_HOSTS,
    database_identity,
    verified_local_server,
    visitor_database_name,
)
from app.database.visitor_models import (
    CONSENT,
    OBJECT_IDS,
    ROOM,
    SCOPE,
    VisitorEvent,
    VisitorSession,
)
from app.modules.admin_auth import LOOPBACK, TOKEN, digest

PATH = "/api/v1/visitor"
COOKIE = "airc_visitor"
LIFETIME = timedelta(hours=8)
MAX_BODY = 8192
MAX_EVENTS = 500
router = APIRouter(prefix=PATH)


class VisitorBody(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class OptIn(VisitorBody):
    consent: Literal["synthetic_opt_in_v1"]


class Event(VisitorBody):
    id: UUID4
    schema_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    event_type: Literal["room_enter", "object_select", "info_open", "info_close", "session_end"]
    room_id: Literal["demo-room-foundation"]
    object_id: Literal["demo-object-cube", "demo-object-column"] | None = None
    occurred_at: AwareDatetime

    @field_validator("occurred_at", mode="before")
    @classmethod
    def require_timestamp(cls, value):
        if not isinstance(value, str) or len(value) > 40 or "T" not in value:
            raise ValueError("Timestamp must be a timezone-aware ISO date-time")
        return value

    @model_validator(mode="after")
    def check_scope(self):
        needs_object = self.event_type in {"object_select", "info_open", "info_close"}
        if needs_object != (self.object_id is not None):
            raise ValueError("Event has incorrect object scope")
        self.occurred_at = self.occurred_at.astimezone(UTC)
        return self


class Batch(VisitorBody):
    events: list[Event] = Field(min_length=1, max_length=32)


async def json_body(request: Request, schema: type[VisitorBody]):
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise HTTPException(415)
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_BODY:
            raise HTTPException(413)
        data.extend(chunk)
    try:
        return schema.model_validate_json(data)
    except ValidationError:
        raise HTTPException(422) from None


def enabled(request: Request, response: Response) -> None:
    config = request.app.state.admin_config
    engine = request.app.state.database.engine
    if (
        not config.visitor_synthetic_enabled
        or engine is None
        or engine.url.host not in LOOPBACK_DATABASE_HOSTS
        or engine.url.query
        or not visitor_database_name(engine.url.database)
    ):
        raise HTTPException(404)
    origin = request.headers.get("origin")
    expected = urlsplit(config.admin_origin)
    if (
        not request.client
        or request.client.host not in LOOPBACK
        or request.url.netloc != expected.netloc
        or request.url.scheme != expected.scheme
        or (origin is not None and origin != config.admin_origin)
        or (request.method != "GET" and origin != config.admin_origin)
        or request.headers.get("sec-fetch-site", "same-origin") != "same-origin"
        or any(
            name in request.headers
            for name in ("forwarded", "x-forwarded-host", "x-forwarded-for", "x-forwarded-proto")
        )
    ):
        raise HTTPException(403)
    response.headers["Cache-Control"] = "no-store"


Local = Annotated[None, Depends(enabled)]


def verify_database(db: Session):
    name, host = database_identity(db)
    if not visitor_database_name(name) or not verified_local_server(db.bind.url, name, host):
        raise HTTPException(503)


def local_db(request: Request, _: Local):
    if request.headers.get("x-airc-visitor") != "1":
        raise HTTPException(403)
    try:
        with Session(request.app.state.database.engine, expire_on_commit=False) as db, db.begin():
            verify_database(db)
            yield db
    except IntegrityError:
        # An event ID can win a concurrent insert in another session.
        raise HTTPException(409) from None
    except SQLAlchemyError:
        raise HTTPException(503) from None


DB = Annotated[Session, Depends(local_db, scope="function")]


def session_by_proof(request: Request, db: Session) -> VisitorSession | None:
    token = request.cookies.get(COOKIE)
    if not token or not TOKEN.fullmatch(token):
        return None
    return db.scalar(
        select(VisitorSession)
        .where(
            VisitorSession.token_digest == digest(token),
            VisitorSession.token_expires_at > func.now(),
        )
        .with_for_update()
    )


def authorized(request: Request, db: Session, session_id: UUID) -> VisitorSession:
    session = session_by_proof(request, db)
    if session is None or session.id != session_id:
        raise HTTPException(401)
    return session


def new_event(session: VisitorSession, *, now: datetime, **fields) -> VisitorEvent:
    session.event_count += 1
    return VisitorEvent(
        session_id=session.id,
        ordinal=session.event_count,
        received_at=now,
        **fields,
    )


def view(db: Session, session: VisitorSession):
    latest = db.scalars(
        select(VisitorEvent)
        .where(
            VisitorEvent.session_id == session.id,
            VisitorEvent.event_type.in_(("object_select", "info_open", "info_close")),
        )
        .order_by(VisitorEvent.occurred_at.desc(), VisitorEvent.id.desc())
        .limit(1)
    ).first()
    return {
        "id": session.id,
        "scope": SCOPE,
        "room_id": ROOM,
        "selected_id": latest.object_id if latest else None,
        "info_open": latest is not None and latest.event_type in {"object_select", "info_open"},
        "ended": session.ended_at is not None,
    }


@router.get("/status")
def status(_: Local):
    return {"scope": SCOPE, "objects": OBJECT_IDS}


async def opt_in(request: Request) -> OptIn:
    return await json_body(request, OptIn)


async def event_batch(request: Request) -> Batch:
    return await json_body(request, Batch)


@router.post("/sessions", status_code=201)
def start(
    request: Request, response: Response, _: Local, body: Annotated[OptIn, Depends(opt_in)], db: DB
):
    # Explicit opt-in can safely recover a previously committed start for the same cookie.
    previous = session_by_proof(request, db)
    if previous is not None:
        return view(db, previous)
    now = datetime.now(UTC)
    token = secrets.token_urlsafe(32)
    session = VisitorSession(
        id=uuid4(),
        token_digest=digest(token),
        token_expires_at=now + LIFETIME,
        consent_marker=CONSENT,
        started_at=now,
        last_seen_at=now,
        event_count=0,
    )
    db.add(session)
    db.flush()
    db.add(
        new_event(
            session, now=now, id=uuid4(), event_type="session_start", room_id=ROOM, occurred_at=now
        )
    )
    response.set_cookie(
        COOKIE,
        token,
        path=PATH,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        max_age=int(LIFETIME.total_seconds()),
    )
    return view(db, session)


@router.get("/sessions/{session_id}")
def resume(session_id: UUID, request: Request, db: DB):
    return view(db, authorized(request, db, session_id))


@router.delete("/sessions/{session_id}")
def clear(session_id: UUID, request: Request, response: Response, db: DB):
    db.delete(authorized(request, db, session_id))
    response.delete_cookie(
        COOKIE, path=PATH, httponly=True, secure=request.url.scheme == "https", samesite="strict"
    )
    return {"cleared": True}


def signature(event: Event | VisitorEvent):
    return event.schema_version, event.event_type, event.room_id, event.object_id, event.occurred_at


@router.post("/sessions/{session_id}/events")
def ingest(
    session_id: UUID,
    request: Request,
    _: Local,
    batch: Annotated[Batch, Depends(event_batch)],
    db: DB,
):
    session = authorized(request, db, session_id)
    now = datetime.now(UTC)
    stored = {
        event.id: event
        for event in db.scalars(
            select(VisitorEvent).where(VisitorEvent.id.in_({e.id for e in batch.events}))
        )
    }
    receipts = []
    pending_end = session.ended_at
    for item in batch.events:
        event = stored.get(item.id)
        outcome = "duplicate"
        if event is not None:
            if event.session_id != session.id or signature(item) != signature(event):
                raise HTTPException(409)
        else:
            if (
                not session.started_at - timedelta(seconds=1)
                <= item.occurred_at
                <= now + timedelta(seconds=5)
            ):
                raise HTTPException(422)
            if pending_end is not None and (
                item.event_type == "session_end" or item.occurred_at > pending_end
            ):
                raise HTTPException(409)
            if session.event_count >= MAX_EVENTS:
                raise HTTPException(413)
            if item.event_type == "session_end":
                pending_end = item.occurred_at
                # Reject a close timestamp earlier than already accepted interactions.
                latest = db.scalar(
                    select(func.max(VisitorEvent.occurred_at)).where(
                        VisitorEvent.session_id == session.id
                    )
                )
                if latest and latest > pending_end:
                    raise HTTPException(409)
            event = new_event(session, now=now, **item.model_dump())
            stored[item.id] = event
            db.add(event)
            outcome = "accepted"
        receipts.append(
            {
                "id": event.id,
                "status": outcome,
                "ordinal": event.ordinal,
                "received_at": event.received_at,
            }
        )
    if any(receipt["status"] == "accepted" for receipt in receipts):
        session.last_seen_at = now
        session.ended_at = pending_end
    # The function-scoped transaction exits (and commits) before response transmission.
    return {"receipts": receipts}
