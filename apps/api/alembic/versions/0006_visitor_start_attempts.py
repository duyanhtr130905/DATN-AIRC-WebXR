"""Keep start attempt identities independent of the lifetime of a visit."""

import sqlalchemy as sa

from alembic import op
from app.database.visitor_guard import (
    database_identity,
    verified_local_server,
    visitor_database_name,
)

revision = "0006_visitor_start_attempts"
down_revision = "0005_visitor_sessions"
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
        "visitor_start_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("pending_digest", sa.String(64)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("visitor_sessions.id", ondelete="SET NULL"),
            unique=True,
        ),
    )


def downgrade():
    raise RuntimeError("Forward-only migration preserves visitor start idempotency")
