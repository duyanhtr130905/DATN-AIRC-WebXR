from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class RoomStateCursor(Base):
    __tablename__ = "room_state_cursors"
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"), primary_key=True
    )
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    __table_args__ = (CheckConstraint("sequence >= 0", name="ck_cursor_sequence"),)


class CurrentState(Base):
    __tablename__ = "current_states"
    audience: Mapped[str] = mapped_column(String(8), nullable=False, server_default="public")
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    target_room_id: Mapped[UUID | None] = mapped_column(ForeignKey("rooms.id", ondelete="RESTRICT"))
    object_id: Mapped[UUID | None] = mapped_column(nullable=True)
    state_type: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["object_id", "room_id"], ["objects.id", "objects.room_id"], ondelete="RESTRICT"
        ),
        CheckConstraint("audience IN ('public','admin')", name="ck_current_states_audience"),
        UniqueConstraint("target_room_id", "state_type", "audience", name="uq_state_room_type"),
        UniqueConstraint("object_id", "state_type", "audience", name="uq_state_object_type"),
        CheckConstraint("version >= 1", name="ck_state_version"),
        CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name="ck_state_source"
        ),
        CheckConstraint(
            "(state_type = 'room_schedule' AND target_room_id = room_id "
            "AND target_room_id IS NOT NULL AND object_id IS NULL) OR "
            "(state_type IN ('equipment_status','exhibit_info') "
            "AND target_room_id IS NULL AND object_id IS NOT NULL)",
            name="ck_state_target",
        ),
        CheckConstraint(
            "jsonb_typeof(value) = 'object' AND octet_length(value::text) <= 4096",
            name="ck_state_value",
        ),
        Index("ix_state_room_id", "room_id", "id"),
    )


class StateHistory(Base):
    __tablename__ = "state_history"
    source_note: Mapped[str | None] = mapped_column(String(256))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    state_id: Mapped[UUID] = mapped_column(
        ForeignKey("current_states.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        UniqueConstraint("state_id", "version", name="uq_history_state_version"),
        CheckConstraint("version >= 1", name="ck_history_version"),
        CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name="ck_history_source"
        ),
        CheckConstraint(
            "jsonb_typeof(value) = 'object' AND octet_length(value::text) <= 4096",
            name="ck_history_value",
        ),
    )


class Outbox(Base):
    __tablename__ = "outbox"
    audience: Mapped[str] = mapped_column(String(8), nullable=False, server_default="public")
    message_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="state.updated"
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    next_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    lease_owner: Mapped[UUID | None] = mapped_column(nullable=True)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    exhausted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    __table_args__ = (
        CheckConstraint("audience IN ('public','admin')", name="ck_outbox_audience"),
        UniqueConstraint("room_id", "sequence", "audience", name="uq_outbox_room_sequence"),
        CheckConstraint(
            "sequence >= 1 AND attempts >= 0 AND attempts <= 5", name="ck_outbox_counters"
        ),
        CheckConstraint("event_type = 'state.updated'", name="ck_outbox_type"),
        CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND octet_length(payload::text) <= 8192",
            name="ck_outbox_payload",
        ),
        Index("ix_outbox_pending", "exhausted", "published_at", "next_attempt_at"),
    )
