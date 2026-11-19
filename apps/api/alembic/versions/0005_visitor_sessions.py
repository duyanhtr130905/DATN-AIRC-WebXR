import sqlalchemy as sa

from alembic import op
from app.database.visitor_guard import (
    database_identity,
    verified_local_server,
    visitor_database_name,
)

revision = "0005_visitor_sessions"
down_revision = "0004_admin_provenance"
branch_labels = None
depends_on = None


def upgrade():
    if not op.get_context().as_sql:
        bind = op.get_bind()
        if bind.dialect.name != "postgresql":
            raise RuntimeError("M4 migration requires PostgreSQL")
        name, host = database_identity(bind)
        if not verified_local_server(bind.engine.url, name, host) or not (
            name == "airc_foundation" or visitor_database_name(name)
        ):
            raise RuntimeError("M4 migration requires a verified loopback project database")
    op.create_table(
        "visitor_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("token_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("source_kind", sa.String(16), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False),
        sa.Column("consent_marker", sa.String(24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "schema_version = 1 AND source_kind = 'synthetic' "
            "AND scope = 'synthetic_local' AND consent_marker = 'synthetic_opt_in_v1'",
            name="ck_visitor_sessions_scope",
        ),
    )
    op.create_index("ix_visitor_sessions_started_id", "visitor_sessions", ["started_at", "id"])
    op.create_table(
        "visitor_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("visitor_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(16), nullable=False),
        sa.Column("room_id", sa.String(32), nullable=False),
        sa.Column("object_id", sa.String(32)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "schema_version = 1 AND room_id = 'demo-room-foundation' AND ordinal BETWEEN 1 AND 500 "
            "AND ((event_type IN ('session_start', 'room_enter', 'session_end')"
            " AND object_id IS NULL) "
            "OR (event_type IN ('object_select', 'info_open', 'info_close')"
            " AND object_id IS NOT NULL "
            "AND object_id IN ('demo-object-cube', 'demo-object-column')))",
            name="ck_visitor_events_contract",
        ),
        sa.UniqueConstraint("session_id", "ordinal", name="uq_visitor_events_session_ordinal"),
    )
    op.create_index(
        "ix_visitor_events_session_occurred_id",
        "visitor_events",
        ["session_id", "occurred_at", "id"],
    )


def downgrade():
    raise RuntimeError("Forward-only migration preserves local synthetic visitor evidence")
