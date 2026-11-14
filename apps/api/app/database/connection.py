from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings


class Database:
    """Lazy PostgreSQL pool; no DDL, seed or business writes."""

    def __init__(self, settings: Settings):
        self.engine = None
        if settings.database_url is not None:
            self.engine = create_engine(
                settings.database_url.get_secret_value(),
                pool_pre_ping=True,
                pool_size=2,
                max_overflow=0,
                pool_timeout=3,
                connect_args={"connect_timeout": 3, "options": "-c statement_timeout=3000"},
                hide_parameters=True,
            )

    def probe(self) -> str:
        if self.engine is None:
            return "not_configured"
        try:
            with self.engine.connect() as connection:
                return (
                    "ready"
                    if connection.execute(text("SELECT 1")).scalar_one() == 1
                    else "unavailable"
                )
        except SQLAlchemyError:
            # Never return credentials, server addresses or raw driver messages to clients.
            return "unavailable"

    def close(self) -> None:
        if self.engine is not None:
            self.engine.dispose()
