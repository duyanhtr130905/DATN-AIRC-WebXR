"""Reserve ordinal 501 for a terminal event on a full synthetic visit."""

from alembic import op
from app.database.visitor_guard import (
    database_identity,
    verified_local_server,
    visitor_database_name,
)

revision = "0007_visitor_terminal_capacity"
down_revision = "0006_visitor_start_attempts"
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
    op.drop_constraint("ck_visitor_events_contract", "visitor_events", type_="check")
    op.create_check_constraint(
        "ck_visitor_events_contract",
        "visitor_events",
        "schema_version = 1 AND room_id = 'demo-room-foundation' "
        "AND (ordinal BETWEEN 1 AND 500 OR (ordinal = 501 AND event_type = 'session_end')) "
        "AND ((event_type IN ('session_start', 'room_enter', 'session_end')"
        " AND object_id IS NULL) "
        "OR (event_type IN ('object_select', 'info_open', 'info_close')"
        " AND object_id IS NOT NULL "
        "AND object_id IN ('demo-object-cube', 'demo-object-column')))",
    )


def downgrade():
    raise RuntimeError("Forward-only migration preserves terminal visitor evidence")
