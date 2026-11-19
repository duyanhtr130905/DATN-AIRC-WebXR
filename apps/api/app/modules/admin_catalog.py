"""Private P507 Catalog and manual observations."""

import asyncio
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.admin_models import AdminAccount, AdminAudit, AdminCatalog
from app.database.models import Object
from app.database.state_models import CurrentState, Outbox, StateHistory
from app.modules.admin_auth import COOKIE, DB, Operator, allowed, auth
from app.modules.p507 import ROOM_ID, object_id
from app.modules.state.schemas import StateType
from app.modules.state.service import (
    StateConflict,
    StateUnavailable,
    change_state,
    state_payload,
    visible_room,
)

router = APIRouter(prefix="/api/v1/admin/p507")
stream_router = APIRouter()
PROVENANCE = "OWNER_SURVEYED / PENDING_VERIFICATION"
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]
Kind = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class CatalogInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    kind: Kind
    group_name: Kind
    description: str = Field(max_length=512)
    location: str = Field(max_length=256)
    modeling: Literal["MODELED", "NOT_MODELED", "INFO_ONLY"]
    archived: bool
    expected_version: int = Field(strict=True, ge=0, le=2**53 - 2)


class StateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_id: UUID
    state_type: StateType
    value: dict
    observed_at: AwareDatetime
    source_note: str = Field(default="", max_length=256)
    expected_version: int = Field(strict=True, ge=0, le=2**53 - 2)


def logical_id(obj: Object) -> str | None:
    key = obj.external_reference
    if obj.source_kind == "synthetic" and key and object_id(key) == obj.id:
        return key
    return None


def catalog_row(obj: Object, details: AdminCatalog | None):
    return {
        "id": obj.id,
        "logical_id": logical_id(obj),
        "version": details.revision if details else 0,
        "name": details.name if details else obj.name,
        "kind": details.kind if details else obj.type,
        "group_name": details.group_name if details else "R4",
        "description": details.description if details else "",
        "location": details.location if details else "",
        "archived": details.archived if details else False,
        "modeling": details.modeling
        if details
        else "MODELED"
        if logical_id(obj)
        else "NOT_MODELED",
        "provenance": PROVENANCE if details else "PROVISIONAL / SYNTHETIC",
    }


@router.get("")
def snapshot(db: DB, account: Operator):
    objects = db.execute(
        select(Object, AdminCatalog)
        .outerjoin(AdminCatalog)
        .where(Object.room_id == ROOM_ID, Object.source_kind.in_(("synthetic", "unknown")))
        .order_by(Object.id)
        .limit(513)
    ).all()
    states = db.execute(
        select(CurrentState, AdminAccount.username, StateHistory.source_note)
        .join(
            AdminAudit,
            and_(
                AdminAudit.target_id == CurrentState.id,
                AdminAudit.revision == CurrentState.version,
                AdminAudit.operation == CurrentState.state_type,
                AdminAudit.outcome == "success",
            ),
        )
        .join(AdminAccount, AdminAccount.id == AdminAudit.account_id)
        .join(
            StateHistory,
            and_(
                StateHistory.state_id == CurrentState.id,
                StateHistory.version == CurrentState.version,
            ),
        )
        .where(CurrentState.room_id == ROOM_ID, CurrentState.audience == "admin")
        .limit(1537)
    ).all()
    if len(objects) > 512 or len(states) > 1536:
        raise HTTPException(409)
    return {
        "objects": [catalog_row(obj, details) for obj, details in objects],
        "states": [
            {
                **state_payload(state),
                "operator": username,
                "source_note": note,
                "provenance": PROVENANCE,
            }
            for state, username, note in states
        ],
    }


def save_catalog(
    db: Session, account: AdminAccount, body: CatalogInput, obj: Object, creating: bool
):
    existing = db.get(AdminCatalog, obj.id)
    version = existing.revision if existing else 0
    if version != body.expected_version:
        raise HTTPException(409)
    if (body.modeling == "MODELED") != bool(logical_id(obj)):
        raise HTTPException(422)
    row = existing or AdminCatalog(object_id=obj.id)
    for key, value in body.model_dump(exclude={"expected_version"}).items():
        setattr(row, key, value)
    row.revision = version + 1
    db.add(row)
    db.add(
        AdminAudit(
            account_id=account.id,
            target_id=obj.id,
            operation="catalog.create" if creating else "catalog.update",
            outcome="success",
            previous_revision=version,
            revision=row.revision,
        )
    )
    return catalog_row(obj, row)


def lock_room(db: Session):
    try:
        visible_room(db, ROOM_ID, lock=True)
    except StateUnavailable:
        raise HTTPException(404) from None


@router.post("/objects", status_code=201)
def create_object(body: CatalogInput, db: DB, account: Operator):
    lock_room(db)
    count = db.scalar(select(func.count()).select_from(Object).where(Object.room_id == ROOM_ID))
    if count >= 512:
        raise HTTPException(409)
    obj = Object(
        room_id=ROOM_ID,
        name="Private Catalog object",
        type="private",
        source_kind="unknown",
        evidence_ref=PROVENANCE,
    )
    db.add(obj)
    db.flush()
    return save_catalog(db, account, body, obj, True)


@router.put("/objects/{identity}")
def edit_object(identity: UUID, body: CatalogInput, db: DB, account: Operator):
    lock_room(db)
    obj = db.scalar(
        select(Object)
        .where(
            Object.id == identity,
            Object.room_id == ROOM_ID,
            Object.source_kind.in_(("synthetic", "unknown")),
        )
        .with_for_update()
    )
    if obj is None:
        raise HTTPException(404)
    return save_catalog(db, account, body, obj, False)


@router.put("/state")
def update_state(body: StateInput, db: DB, account: Operator):
    lock_room(db)
    details = db.get(AdminCatalog, body.target_id)
    if details and details.archived:
        raise HTTPException(409)
    try:
        result = change_state(
            db,
            room_id=ROOM_ID,
            target_id=body.target_id,
            target_kind="room" if body.state_type == "room_schedule" else "object",
            state_type=body.state_type,
            value=body.value,
            expected_version=body.expected_version,
            source_observed_at=body.observed_at,
            audience="admin",
            source_note=body.source_note,
        )
    except StateConflict:
        raise HTTPException(409) from None
    except StateUnavailable:
        raise HTTPException(404) from None
    except ValueError:
        raise HTTPException(422) from None
    state = result["state"]
    db.add(
        AdminAudit(
            account_id=account.id,
            target_id=UUID(state["id"]),
            operation=body.state_type,
            outcome="success",
            previous_revision=body.expected_version,
            revision=state["version"],
        )
    )
    return result


def published(socket: WebSocket):
    engine = socket.app.state.database.engine
    if engine is None:
        return None
    with Session(engine) as db:
        if auth(db, socket.cookies.get(COOKIE)) is None:
            return None
        return db.scalar(
            select(func.coalesce(func.max(Outbox.sequence), 0)).where(
                Outbox.room_id == ROOM_ID,
                Outbox.audience == "admin",
                Outbox.published_at.is_not(None),
            )
        )


@stream_router.websocket("/ws/v1/admin/p507")
async def stream(socket: WebSocket):
    if not allowed(socket, check_origin=True) or await asyncio.to_thread(published, socket) is None:
        await socket.close(code=1008)
        return
    broker = socket.app.state.broker
    try:
        sub = broker.subscribe((ROOM_ID, "admin"), coalesce=True)
    except ValueError:
        await socket.close(code=1013)
        return
    disconnect = None
    try:
        await socket.accept()
        disconnect = asyncio.create_task(socket.receive())
        previous = None
        while not disconnect.done():
            cursor = await asyncio.to_thread(published, socket)
            if cursor is None:
                await socket.close(code=1008)
                return
            if cursor != previous:
                await socket.send_json({"type": "admin.invalidate", "sequence": cursor})
                previous = cursor
            try:
                await asyncio.wait_for(sub.queue.get(), timeout=1)
            except TimeoutError:
                pass
    except (RuntimeError, WebSocketDisconnect, SQLAlchemyError):
        return
    finally:
        if disconnect is not None:
            disconnect.cancel()
            await asyncio.gather(disconnect, return_exceptions=True)
        broker.subscribers.discard(sub)
