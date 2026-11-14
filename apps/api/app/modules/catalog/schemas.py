from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class PublicMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=512)


def public_metadata(value: dict) -> PublicMetadata:
    # Unknown, nested or oversized values are never echoed from unrestricted JSONB.
    limits = {"label": 256, "description": 512}
    return PublicMetadata(
        **{
            key: value[key]
            for key, limit in limits.items()
            if isinstance(value.get(key), str) and len(value[key]) <= limit
        }
    )


class RoomResponse(BaseModel):
    id: UUID
    code: str
    name: str
    source_kind: Literal["synthetic"]
    metadata: PublicMetadata
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ObjectResponse(BaseModel):
    id: UUID
    room_id: UUID
    name: str
    type: str
    source_kind: Literal["synthetic"]
    metadata: PublicMetadata
    created_at: AwareDatetime
    updated_at: AwareDatetime


class PageMeta(BaseModel):
    schema_version: Literal[1] = 1
    next_cursor: str | None = None


class RoomsPage(BaseModel):
    data: list[RoomResponse]
    meta: PageMeta


class ObjectsPage(BaseModel):
    data: list[ObjectResponse]
    meta: PageMeta


class ObjectDetail(BaseModel):
    data: ObjectResponse
    meta: PageMeta


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorBody
