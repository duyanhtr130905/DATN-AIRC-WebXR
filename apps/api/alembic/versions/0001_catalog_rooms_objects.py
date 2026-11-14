"""Create Catalog rooms/objects only; no seed or state/session tables."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_catalog"
down_revision = None
branch_labels = None
depends_on = None


def common_columns():
    return [
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("source_kind", sa.String(16), nullable=False, server_default="unknown"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("evidence_ref", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    ]


def checks(table):
    return [
        sa.CheckConstraint(
            "source_kind IN ('synthetic','unknown','real_verified')", name=f"ck_{table}_source_kind"
        ),
        sa.CheckConstraint(
            "source_kind != 'real_verified' OR "
            "(evidence_ref IS NOT NULL AND length(trim(evidence_ref)) > 0)",
            name=f"ck_{table}_verified_evidence",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(metadata) = 'object' AND octet_length(metadata::text) <= 8192",
            name=f"ck_{table}_metadata",
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name=f"ck_{table}_name"),
    ]


def upgrade():
    op.create_table(
        "rooms",
        *common_columns(),
        sa.Column("code", sa.String(64), nullable=False),
        sa.UniqueConstraint("code", name="rooms_code_key"),
        sa.CheckConstraint("length(trim(code)) > 0", name="ck_rooms_code"),
        *checks("rooms"),
    )
    op.create_index("ix_rooms_source_id", "rooms", ["source_kind", "id"])
    op.create_table(
        "objects",
        *common_columns(),
        sa.Column("room_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("transform", postgresql.JSONB(), nullable=True),
        sa.Column("external_reference", sa.String(256), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("length(trim(type)) > 0", name="ck_objects_type"),
        sa.CheckConstraint(
            "transform IS NULL OR (jsonb_typeof(transform) = 'object' "
            "AND octet_length(transform::text) <= 8192)",
            name="ck_objects_transform",
        ),
        *checks("objects"),
    )
    op.create_index("ix_objects_room_source_id", "objects", ["room_id", "source_kind", "id"])


def downgrade():
    raise RuntimeError("Destructive downgrade is disabled; review a separate disposable-only plan.")
