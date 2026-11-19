import sqlalchemy as sa

from alembic import op

revision = "0003_admin_manual"
down_revision = "0002_state_realtime"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_table(
        "admin_sessions",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("admin_accounts.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "admin_catalog",
        sa.Column("object_id", sa.Uuid(), sa.ForeignKey("objects.id"), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("group_name", sa.String(64), nullable=False),
        sa.Column("description", sa.String(512), nullable=False),
        sa.Column("location", sa.String(256), nullable=False),
        sa.Column("modeling", sa.String(16), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "admin_audit",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("admin_accounts.id")),
        sa.Column("target_id", sa.Uuid()),
        sa.Column("operation", sa.String(40), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("previous_revision", sa.BigInteger()),
        sa.Column("revision", sa.BigInteger()),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.add_column("state_history", sa.Column("source_note", sa.String(256)))
    for table in ("current_states", "outbox"):
        op.add_column(
            table, sa.Column("audience", sa.String(8), nullable=False, server_default="public")
        )
        op.create_check_constraint(f"ck_{table}_audience", table, "audience IN ('public','admin')")
    for table, name, columns in (
        ("current_states", "uq_state_room_type", ["target_room_id", "state_type"]),
        ("current_states", "uq_state_object_type", ["object_id", "state_type"]),
        ("outbox", "uq_outbox_room_sequence", ["room_id", "sequence"]),
    ):
        op.drop_constraint(name, table, type_="unique")
        op.create_unique_constraint(name, table, [*columns, "audience"])


def downgrade():
    raise RuntimeError("Forward-only migration preserves Admin and state history")
