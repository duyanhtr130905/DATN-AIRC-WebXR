import sqlalchemy as sa

from alembic import op

revision = "0004_admin_provenance"
down_revision = "0003_admin_manual"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("admin_audit", sa.Column("provenance", sa.String(16)))
    op.add_column("admin_audit", sa.Column("observed_at", sa.DateTime(timezone=True)))
    op.add_column("admin_audit", sa.Column("source_note", sa.String(256)))


def downgrade():
    raise RuntimeError("Forward-only migration preserves provenance evidence")
