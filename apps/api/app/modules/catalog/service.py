import base64
import binascii
import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Object, Room
from app.modules.catalog.schemas import ObjectResponse, RoomResponse, public_metadata


def encode_cursor(scope: str, identity: UUID) -> str:
    data = json.dumps({"v": 1, "scope": scope, "after": str(identity)}, separators=(",", ":"))
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def decode_cursor(cursor: str | None, scope: str) -> UUID | None:
    if cursor is None:
        return None
    try:
        raw = base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True)
        data = json.loads(raw)
        if (
            not isinstance(data, dict)
            or set(data) != {"v", "scope", "after"}
            or type(data["v"]) is not int
            or data["v"] != 1
            or data["scope"] != scope
            or not isinstance(data["after"], str)
        ):
            raise ValueError
        return UUID(data["after"])
    except (ValueError, TypeError, KeyError, binascii.Error, UnicodeDecodeError):
        raise HTTPException(422, detail="INVALID_CURSOR") from None


def room_response(room: Room) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        code=room.code,
        name=room.name,
        source_kind=room.source_kind,
        metadata=public_metadata(room.metadata_json),
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


def object_response(obj: Object) -> ObjectResponse:
    return ObjectResponse(
        id=obj.id,
        room_id=obj.room_id,
        name=obj.name,
        type=obj.type,
        source_kind=obj.source_kind,
        metadata=public_metadata(obj.metadata_json),
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def rooms_page(session: Session, limit: int, cursor: str | None):
    after = decode_cursor(cursor, "rooms")
    query = select(Room).where(Room.source_kind == "synthetic")
    if after is not None:
        query = query.where(Room.id > after)
    rows = list(session.scalars(query.order_by(Room.id).limit(limit + 1)))
    next_cursor = encode_cursor("rooms", rows[limit - 1].id) if len(rows) > limit else None
    return rows[:limit], next_cursor


def objects_page(session: Session, room_id: UUID, limit: int, cursor: str | None):
    after = decode_cursor(cursor, f"room:{room_id}")
    room = session.scalar(
        select(Room.id).where(Room.id == room_id, Room.source_kind == "synthetic")
    )
    if room is None:
        raise HTTPException(404, detail="CATALOG_NOT_FOUND")
    query = (
        select(Object)
        .join(Room)
        .where(
            Object.room_id == room_id,
            Object.source_kind == "synthetic",
            Room.source_kind == "synthetic",
        )
    )
    if after is not None:
        query = query.where(Object.id > after)
    rows = list(session.scalars(query.order_by(Object.id).limit(limit + 1)))
    next_cursor = (
        encode_cursor(f"room:{room_id}", rows[limit - 1].id) if len(rows) > limit else None
    )
    return rows[:limit], next_cursor


def object_detail(session: Session, object_id: UUID) -> Object:
    obj = session.scalar(
        select(Object)
        .join(Room)
        .where(
            Object.id == object_id,
            Object.source_kind == "synthetic",
            Room.source_kind == "synthetic",
        )
    )
    if obj is None:
        raise HTTPException(404, detail="CATALOG_NOT_FOUND")
    return obj
