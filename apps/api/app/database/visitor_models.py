from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base

ROOM = "demo-room-foundation"
OBJECT_IDS = ("demo-object-cube", "demo-object-column")
SCOPE = "synthetic_local"
CONSENT = "synthetic_opt_in_v1"


class VisitorSession(Base):
    __tablename__ = "visitor_sessions"
    __table_args__ = (
        CheckConstraint(
            "schema_version = 1 AND source_kind = 'synthetic' "
            "AND scope = 'synthetic_local' AND consent_marker = 'synthetic_opt_in_v1'",
            name="ck_visitor_sessions_scope",
        ),
        Index("ix_visitor_sessions_started_id", "started_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    token_digest: Mapped[str] = mapped_column(String(64), unique=True)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    schema_version: Mapped[int] = mapped_column(default=1)
    source_kind: Mapped[str] = mapped_column(String(16), default="synthetic")
    scope: Mapped[str] = mapped_column(String(20), default=SCOPE)
    consent_marker: Mapped[str] = mapped_column(String(24), default=CONSENT)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_count: Mapped[int] = mapped_column(default=0)


class VisitorEvent(Base):
    __tablename__ = "visitor_events"
    __table_args__ = (
        CheckConstraint(
            "schema_version = 1 AND room_id = 'demo-room-foundation' AND ordinal BETWEEN 1 AND 500 "
            "AND ((event_type IN ('session_start', 'room_enter', 'session_end')"
            " AND object_id IS NULL) "
            "OR (event_type IN ('object_select', 'info_open', 'info_close')"
            " AND object_id IS NOT NULL "
            "AND object_id IN ('demo-object-cube', 'demo-object-column')))",
            name="ck_visitor_events_contract",
        ),
        UniqueConstraint("session_id", "ordinal", name="uq_visitor_events_session_ordinal"),
        Index("ix_visitor_events_session_occurred_id", "session_id", "occurred_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("visitor_sessions.id", ondelete="CASCADE"))
    ordinal: Mapped[int]
    schema_version: Mapped[int] = mapped_column(default=1)
    event_type: Mapped[str] = mapped_column(String(16))
    room_id: Mapped[str] = mapped_column(String(32))
    object_id: Mapped[str | None] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
