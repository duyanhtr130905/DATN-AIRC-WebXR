from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def catalog_checks(table: str):
    return (
        CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name=f"ck_{table}_source_kind"
        ),
        CheckConstraint(
            "source_kind != 'real_verified' OR "
            "(evidence_ref IS NOT NULL AND length(trim(evidence_ref)) > 0)",
            name=f"ck_{table}_verified_evidence",
        ),
        CheckConstraint(
            "jsonb_typeof(metadata) = 'object' AND octet_length(metadata::text) <= 8192",
            name=f"ck_{table}_metadata",
        ),
        CheckConstraint("length(trim(name)) > 0", name=f"ck_{table}_name"),
    )


class CatalogFields:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(16), nullable=False, server_default="unknown")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )
    evidence_ref: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Room(CatalogFields, Base):
    __tablename__ = "rooms"
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    __table_args__ = (
        *catalog_checks("rooms"),
        UniqueConstraint("code", name="rooms_code_key"),
        CheckConstraint("length(trim(code)) > 0", name="ck_rooms_code"),
        Index("ix_rooms_source_id", "source_kind", "id"),
    )


class Object(CatalogFields, Base):
    __tablename__ = "objects"
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    transform: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))
    external_reference: Mapped[str | None] = mapped_column(String(256))
    __table_args__ = (
        *catalog_checks("objects"),
        UniqueConstraint("id", "room_id", name="uq_object_id_room"),
        CheckConstraint("length(trim(type)) > 0", name="ck_objects_type"),
        CheckConstraint(
            "transform IS NULL OR (jsonb_typeof(transform) = 'object' AND "
            "octet_length(transform::text) <= 8192)",
            name="ck_objects_transform",
        ),
        Index("ix_objects_room_source_id", "room_id", "source_kind", "id"),
    )


# Register the additional M1-B tables in the same Modular Monolith metadata.
from app.database import admin_models as admin_models  # noqa: E402
from app.database import state_models as state_models  # noqa: E402
