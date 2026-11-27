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
from sqlalchemy.dialects.postgresql import insert
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
    VisitorStartAttempt,
)
from app.modules.admin_auth import LOOPBACK, TOKEN, digest

PATH = "/api/v1/visitor"
COOKIE = "airc_visitor"
INTENT_COOKIE = "airc_visitor_intent"
LIFETIME = timedelta(hours=8)
MAX_BODY = 8192
MAX_EVENTS = 500
router = APIRouter(prefix=PATH)


class VisitorBody(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class OptIn(VisitorBody):
    consent: Literal["synthetic_opt_in_v1"]
    attempt_id: UUID4 | None = None
    previous_id: UUID4 | None = None


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


def lock_session(db: Session, **filters) -> VisitorSession | None:
    return db.scalar(select(VisitorSession).filter_by(**filters).with_for_update())


def current_proof(request: Request, db: Session) -> VisitorSession | None:
    token = request.cookies.get(COOKIE)
    if not token or not TOKEN.fullmatch(token):
        return None
    session = lock_session(db, token_digest=digest(token))
    return session if session and session.token_expires_at > datetime.now(UTC) else None


def authorized(request: Request, db: Session, session_id: UUID) -> VisitorSession:
    session = current_proof(request, db)
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


def remaining_events(session: VisitorSession) -> int:
    # Ordinal 501 is available only to the terminal event of an otherwise full session.
    return max(0, MAX_EVENTS - session.event_count)


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
        "remaining_events": remaining_events(session),
    }


@router.get("/status")
def status(_: Local):
    return {"scope": SCOPE, "objects": OBJECT_IDS}


async def opt_in(request: Request) -> OptIn:
    return await json_body(request, OptIn)


async def event_batch(request: Request) -> Batch:
    return await json_body(request, Batch)


def cookie_options(request: Request):
    return dict(path=PATH, httponly=True, secure=request.url.scheme == "https", samesite="strict")


def intent_proof(request: Request, attempt_id: UUID) -> str | None:
    prefix, _, proof = request.cookies.get(INTENT_COOKIE, "").partition(".")
    return proof if prefix == str(attempt_id) and TOKEN.fullmatch(proof) else None


def attempt_or_error(db: Session, attempt_id: UUID, *, lock=False) -> VisitorStartAttempt:
    attempt = db.get(VisitorStartAttempt, attempt_id, with_for_update=lock, populate_existing=True)
    if attempt is None or attempt.expires_at <= datetime.now(UTC):
        raise HTTPException(401)
    return attempt


@router.post("/sessions/intent")
def prepare_start(
    request: Request, response: Response, _: Local, body: Annotated[OptIn, Depends(opt_in)], db: DB
):
    attempt_id = body.attempt_id
    if attempt_id is None:
        raise HTTPException(422)
    candidate = secrets.token_urlsafe(32)
    db.execute(
        insert(VisitorStartAttempt)
        .values(
            id=attempt_id, expires_at=datetime.now(UTC) + LIFETIME, pending_digest=digest(candidate)
        )
        .on_conflict_do_nothing(index_elements=[VisitorStartAttempt.id])
    )
    attempt = attempt_or_error(db, attempt_id, lock=True)
    if attempt.pending_digest is None:
        raise HTTPException(409)
    old_candidate = intent_proof(request, attempt_id)
    if old_candidate is None or digest(old_candidate) != attempt.pending_digest:
        # A lost preparation reply may be retried before commit, without creating a visit.
        attempt.pending_digest = digest(candidate)
        response.set_cookie(
            INTENT_COOKIE,
            f"{attempt_id}.{candidate}",
            max_age=max(1, int((attempt.expires_at - datetime.now(UTC)).total_seconds())),
            **cookie_options(request),
        )
    return {"prepared": True}


def create_session(
    request: Request, db: Session, body: OptIn, attempt: VisitorStartAttempt, token: str
):
    if attempt.pending_digest != digest(token):
        raise HTTPException(401)
    previous = current_proof(request, db)
    if body.previous_id:
        if previous is None or previous.id != body.previous_id:
            raise HTTPException(401)
        if previous.ended_at is None:
            raise HTTPException(409)
        previous.token_expires_at = datetime.now(UTC)
    elif previous is not None:
        raise HTTPException(409)

    now = datetime.now(UTC)
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
    attempt.session_id = session.id
    attempt.pending_digest = None
    db.add(
        new_event(
            session,
            now=now,
            id=uuid4(),
            event_type="session_start",
            room_id=ROOM,
            occurred_at=now,
        )
    )
    return session


@router.post("/sessions", status_code=201)
def start(
    request: Request, response: Response, _: Local, body: Annotated[OptIn, Depends(opt_in)], db: DB
):
    if body.attempt_id is None:
        # Preserve active-session reuse for older clients. Creating requires an intent.
        previous = current_proof(request, db)
        if previous is None or previous.ended_at is not None or body.previous_id is not None:
            raise HTTPException(409)
        return view(db, previous)

    token = intent_proof(request, body.attempt_id)
    if token is None:
        raise HTTPException(401)
    attempt = attempt_or_error(db, body.attempt_id)
    if attempt.pending_digest is not None:
        # Only a new commit takes the attempt row lock. Recheck after a racing commit.
        attempt = attempt_or_error(db, body.attempt_id, lock=True)
    if attempt.pending_digest is not None:
        session = create_session(request, db, body, attempt, token)
    else:
        # Read-only duplicate. An expired proof or a deleted visit cannot be resurrected.
        session = db.get(VisitorSession, attempt.session_id) if attempt.session_id else None
        if (
            session is None
            or session.token_digest != digest(token)
            or session.token_expires_at <= datetime.now(UTC)
        ):
            raise HTTPException(401)

    response.set_cookie(
        COOKIE,
        token,
        max_age=max(1, int((session.token_expires_at - datetime.now(UTC)).total_seconds())),
        **cookie_options(request),
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
    response.delete_cookie(INTENT_COOKIE, **cookie_options(request))
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
            if item.event_type != "session_end" and session.event_count >= MAX_EVENTS:
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
    return {"receipts": receipts, "remaining_events": remaining_events(session)}
