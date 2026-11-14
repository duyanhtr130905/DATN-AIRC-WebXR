"""Synthetic current state, immutable history and durable realtime outbox."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from alembic import op

revision = "0002_state_realtime"
down_revision = "0001_catalog"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_object_id_room", "objects", ["id", "room_id"])
    op.create_table(
        "room_state_cursors",
        sa.Column(
            "room_id", sa.UUID(), sa.ForeignKey("rooms.id", ondelete="RESTRICT"), primary_key=True
        ),
        sa.Column("sequence", sa.BigInteger(), nullable=False, server_default="0"),
        sa.CheckConstraint("sequence >= 0", name="ck_cursor_sequence"),
    )
    op.create_table(
        "current_states",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "room_id", sa.UUID(), sa.ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("target_room_id", sa.UUID(), sa.ForeignKey("rooms.id", ondelete="RESTRICT")),
        sa.Column("object_id", sa.UUID()),
        sa.Column("state_type", sa.String(32), nullable=False),
        sa.Column("value", pg.JSONB(), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.Column("source_kind", sa.String(16), nullable=False),
        sa.Column("source_observed_at", sa.DateTime(timezone=True)),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id", "room_id"], ["objects.id", "objects.room_id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("target_room_id", "state_type", name="uq_state_room_type"),
        sa.UniqueConstraint("object_id", "state_type", name="uq_state_object_type"),
        sa.CheckConstraint("version >= 1", name="ck_state_version"),
        sa.CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name="ck_state_source"
        ),
        sa.CheckConstraint(
            "(state_type = 'room_schedule' AND target_room_id = room_id "
            "AND target_room_id IS NOT NULL AND object_id IS NULL) OR "
            "(state_type IN ('equipment_status','exhibit_info') "
            "AND target_room_id IS NULL AND object_id IS NOT NULL)",
            name="ck_state_target",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(value) = 'object' AND octet_length(value::text) <= 4096",
            name="ck_state_value",
        ),
    )
    op.create_index("ix_state_room_id", "current_states", ["room_id", "id"])
    op.create_table(
        "state_history",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "state_id",
            sa.UUID(),
            sa.ForeignKey("current_states.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.Column("value", pg.JSONB(), nullable=False),
        sa.Column("source_kind", sa.String(16), nullable=False),
        sa.Column("source_observed_at", sa.DateTime(timezone=True)),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("state_id", "version", name="uq_history_state_version"),
        sa.CheckConstraint("version >= 1", name="ck_history_version"),
        sa.CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name="ck_history_source"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(value) = 'object' AND octet_length(value::text) <= 4096",
            name="ck_history_value",
        ),
    )
    op.execute("""CREATE FUNCTION reject_history_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'state_history is append-only'; END; $$""")
    op.execute(
        "CREATE TRIGGER history_append_only BEFORE UPDATE OR DELETE ON state_history "
        "FOR EACH ROW EXECUTE FUNCTION reject_history_mutation()"
    )
    op.create_table(
        "outbox",
        sa.Column("message_id", sa.UUID(), primary_key=True),
        sa.Column(
            "room_id", sa.UUID(), sa.ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("sequence", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False, server_default="state.updated"),
        sa.Column("payload", pg.JSONB(), nullable=False),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("lease_owner", sa.UUID()),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("exhausted", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint("room_id", "sequence", name="uq_outbox_room_sequence"),
        sa.CheckConstraint(
            "sequence >= 1 AND attempts >= 0 AND attempts <= 5", name="ck_outbox_counters"
        ),
        sa.CheckConstraint("event_type = 'state.updated'", name="ck_outbox_type"),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND octet_length(payload::text) <= 8192",
            name="ck_outbox_payload",
        ),
    )
    op.create_index("ix_outbox_pending", "outbox", ["exhausted", "published_at", "next_attempt_at"])


def downgrade():
    raise RuntimeError("Destructive downgrade disabled; separate disposable-only review required")
