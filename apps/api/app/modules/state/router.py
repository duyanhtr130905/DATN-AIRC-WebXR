from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.database.models import Object
from app.database.state_models import CurrentState
from app.modules.catalog.router import Cursor, DatabaseSession, Limit
from app.modules.catalog.schemas import ErrorEnvelope
from app.modules.catalog.service import decode_cursor, encode_cursor
from app.modules.state.read import history_rows
from app.modules.state.schemas import HistoryPage, StatesPage, StateType
from app.modules.state.service import StateUnavailable, public_state, visible_room, visible_states

router = APIRouter(
    prefix="/api/v1",
    tags=["synthetic-state"],
    responses={code: {"model": ErrorEnvelope} for code in [404, 422, 503, 500]},
)


def check_room(session, room_id):
    try:
        visible_room(session, room_id)
    except StateUnavailable:
        raise HTTPException(404, "CATALOG_NOT_FOUND") from None


def object_room(session, object_id):
    room_id = session.scalar(
        select(Object.room_id).where(Object.id == object_id, Object.source_kind == "synthetic")
    )
    if room_id is None:
        raise HTTPException(404, "CATALOG_NOT_FOUND")
    check_room(session, room_id)
    return room_id


def page(session, room_id, limit, cursor, object_id=None):
    check_room(session, room_id)
    scope = f"states:{object_id or room_id}"
    after = decode_cursor(cursor, scope)
    query = visible_states(room_id)
    if object_id:
        query = query.where(CurrentState.object_id == object_id)
    if after:
        query = query.where(CurrentState.id > after)
    rows = list(session.scalars(query.order_by(CurrentState.id).limit(limit + 1)))
    return {
        "data": [public_state(row) for row in rows[:limit]],
        "meta": {
            "schema_version": 1,
            "next_cursor": encode_cursor(scope, rows[limit - 1].id) if len(rows) > limit else None,
        },
    }


@router.get("/rooms/{room_id}/states", response_model=StatesPage)
def room_states(room_id: UUID, session: DatabaseSession, limit: Limit = 25, cursor: Cursor = None):
    return page(session, room_id, limit, cursor)


@router.get("/objects/{object_id}/states", response_model=StatesPage)
def object_states(
    object_id: UUID, session: DatabaseSession, limit: Limit = 25, cursor: Cursor = None
):
    return page(session, object_room(session, object_id), limit, cursor, object_id)


@router.get("/objects/{object_id}/states/{state_type}/history", response_model=HistoryPage)
def object_history(
    object_id: UUID,
    state_type: StateType,
    session: DatabaseSession,
    after_version: Annotated[int, Query(ge=0)] = 0,
    limit: Limit = 25,
):
    room_id = object_room(session, object_id)
    state = session.scalar(
        visible_states(room_id).where(
            CurrentState.object_id == object_id, CurrentState.state_type == state_type
        )
    )
    if state is None:
        raise HTTPException(404, "CATALOG_NOT_FOUND")
    rows = history_rows(session, room_id, state, after_version, limit)
    return {
        "data": [public_state(state, row) for row in rows[:limit]],
        "meta": {
            "schema_version": 1,
            "next_after_version": rows[limit - 1].version if len(rows) > limit else None,
        },
    }
