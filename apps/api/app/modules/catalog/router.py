from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_session
from app.modules.catalog import service
from app.modules.catalog.schemas import (
    ErrorEnvelope,
    ObjectDetail,
    ObjectsPage,
    PageMeta,
    RoomsPage,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["synthetic-catalog"],
    responses={code: {"model": ErrorEnvelope} for code in [404, 422, 503, 500]},
)
DatabaseSession = Annotated[Session, Depends(get_session)]
Limit = Annotated[int, Query(ge=1, le=100)]
Cursor = Annotated[str | None, Query(max_length=400)]


@router.get("/rooms", response_model=RoomsPage)
def rooms(session: DatabaseSession, limit: Limit = 25, cursor: Cursor = None):
    rows, next_cursor = service.rooms_page(session, limit, cursor)
    return RoomsPage(
        data=[service.room_response(row) for row in rows], meta=PageMeta(next_cursor=next_cursor)
    )


@router.get("/rooms/{room_id}/objects", response_model=ObjectsPage)
def objects(room_id: UUID, session: DatabaseSession, limit: Limit = 25, cursor: Cursor = None):
    rows, next_cursor = service.objects_page(session, room_id, limit, cursor)
    return ObjectsPage(
        data=[service.object_response(row) for row in rows], meta=PageMeta(next_cursor=next_cursor)
    )


@router.get("/objects/{object_id}", response_model=ObjectDetail)
def object_by_id(object_id: UUID, session: DatabaseSession):
    return ObjectDetail(
        data=service.object_response(service.object_detail(session, object_id)), meta=PageMeta()
    )
