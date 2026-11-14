from sqlalchemy import create_engine, pool, text

from alembic import context
from app.core.config import Settings
from app.database.models import Base

config = context.config
target_metadata = Base.metadata


def run_migrations():
    # Test runner supplies its own already verified connection; CLI uses explicit config.
    connection = config.attributes.get("connection")
    if connection is not None:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
        return
    settings = Settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is required for explicit migration commands")
    url = settings.database_url.get_secret_value()
    from sqlalchemy.engine import make_url

    parsed = make_url(url)
    name = parsed.database
    confirmation = context.get_x_argument(as_dictionary=True).get("confirm_catalog_database")
    if (
        not (name == "airc_foundation" or name.startswith("airc_test_catalog_"))
        or confirmation != name
        or parsed.host not in {"127.0.0.1", "localhost"}
        or parsed.query
    ):
        raise RuntimeError(
            "Explicit project dev/test database confirmation required "
            "(-x confirm_catalog_database=NAME)"
        )
    if context.is_offline_mode():
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_engine(
        url, poolclass=pool.NullPool, hide_parameters=True, connect_args={"connect_timeout": 3}
    )
    try:
        with engine.begin() as connection:
            if connection.scalar(text("SELECT current_database()")) != confirmation:
                raise RuntimeError("Database identity mismatch")
            context.configure(
                connection=connection, target_metadata=target_metadata, compare_type=True
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


run_migrations()
