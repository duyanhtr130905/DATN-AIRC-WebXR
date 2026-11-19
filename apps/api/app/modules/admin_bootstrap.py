"""Offline provisioning for the confirmed loopback project database."""

import argparse
import getpass

from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.admin_models import AdminAccount
from app.database.connection import Database
from app.database.visitor_guard import (
    LOCAL_VISITOR_DATABASE,
    database_identity,
    verified_local_server,
)
from app.modules.admin_auth import USERNAME, hash_password


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-database", required=True)
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    settings = Settings()
    username = args.username.strip().lower()
    if settings.database_url is None or not USERNAME.fullmatch(username):
        parser.error("Configure DATABASE_URL and use a 3–64 character account name")
    url = make_url(settings.database_url.get_secret_value())
    name = url.database or ""
    if (
        name != args.confirm_database
        or url.host not in {"localhost", "127.0.0.1"}
        or url.query
        or not (
            name == "airc_foundation"
            or name.startswith("airc_test_catalog_")
            or (name == LOCAL_VISITOR_DATABASE and settings.visitor_synthetic_enabled)
        )
    ):
        parser.error("Confirmed loopback project database required")
    import sys

    if not sys.stdin.isatty():
        parser.error("Interactive terminal required")
    password = getpass.getpass("New Admin password: ")
    if not 14 <= len(password) <= 256 or password != getpass.getpass("Confirm password: "):
        parser.error("Use a matching password of 14–256 characters")
    database = Database(settings)
    try:
        with Session(database.engine) as db, db.begin():
            if db.scalar(text("SELECT current_database()")) != name:
                raise RuntimeError("Database identity mismatch")
            if name == LOCAL_VISITOR_DATABASE:
                actual, host = database_identity(db)
                if not verified_local_server(url, actual, host):
                    raise RuntimeError("M4 Admin provisioning requires local PostgreSQL")
            db.execute(text("SELECT pg_advisory_xact_lock(817405508)"))
            if db.scalar(select(AdminAccount.id).where(AdminAccount.username == username)):
                parser.error("Account already exists")
            db.add(AdminAccount(username=username, password_hash=hash_password(password)))
        print("Admin account created")
    finally:
        database.close()


if __name__ == "__main__":
    main()
