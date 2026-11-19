from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class AdminAccount(Base):
    __tablename__ = "admin_accounts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    active: Mapped[bool] = mapped_column(Boolean, server_default="true")


class AdminSession(Base):
    __tablename__ = "admin_sessions"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("admin_accounts.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AdminCatalog(Base):
    __tablename__ = "admin_catalog"
    object_id: Mapped[UUID] = mapped_column(ForeignKey("objects.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    kind: Mapped[str] = mapped_column(String(64))
    group_name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(512))
    location: Mapped[str] = mapped_column(String(256))
    modeling: Mapped[str] = mapped_column(String(16))
    archived: Mapped[bool] = mapped_column(Boolean)
    revision: Mapped[int] = mapped_column(BigInteger)


class AdminAudit(Base):
    __tablename__ = "admin_audit"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID | None] = mapped_column(ForeignKey("admin_accounts.id"))
    target_id: Mapped[UUID | None]
    operation: Mapped[str] = mapped_column(String(40))
    outcome: Mapped[str] = mapped_column(String(16))
    previous_revision: Mapped[int | None] = mapped_column(BigInteger)
    revision: Mapped[int | None] = mapped_column(BigInteger)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
