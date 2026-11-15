"""CI fault injection only: reversible connectivity change on the guarded disposable DB."""

import os
import re
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"block", "restore"}:
        raise RuntimeError("Explicit fault operation + database confirmation required")
    target = make_url(os.environ["DATABASE_URL"])
    base = make_url(os.environ["TEST_DATABASE_URL"])
    name = target.database or ""
    if (
        os.environ.get("AIRC_ALLOW_TEST_DATABASES") != "1"
        or not re.fullmatch(r"airc_test_catalog_[0-9a-f]{32}", name)
        or sys.argv[2] != name
        or target.query
        or base.query
        or target.drivername != "postgresql+psycopg"
        or base.database != "airc_foundation_test"
        or target.host not in {"localhost", "127.0.0.1"}
        or (target.host, target.port, target.username) != (base.host, base.port, base.username)
    ):
        raise RuntimeError("Refusing fault outside disposable project PostgreSQL")
    engine = create_engine(base, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT current_database()")) == "airc_foundation_test"
            mode = "false" if sys.argv[1] == "block" else "true"
            try:
                connection.exec_driver_sql(f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS {mode}')
                if mode == "false":
                    connection.execute(
                        text(
                            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                            "WHERE datname=:name AND pid<>pg_backend_pid()"
                        ),
                        {"name": name},
                    )
            except Exception:
                if mode == "false":
                    connection.exec_driver_sql(f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS true')
                raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
