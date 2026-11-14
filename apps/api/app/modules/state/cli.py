"""Explicit synthetic writer; never imported as a public mutation route."""

import argparse
import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.connection import Database
from app.modules.state.service import change_state


def main():
    parser = argparse.ArgumentParser(description="SYNTHETIC — NOT AIRC REAL DATA")
    parser.add_argument("--confirm-database", required=True)
    parser.add_argument("--room-id", type=UUID, required=True)
    parser.add_argument("--target-kind", choices=["room", "object"], required=True)
    parser.add_argument("--target-id", type=UUID, required=True)
    parser.add_argument(
        "--state-type", choices=["room_schedule", "equipment_status", "exhibit_info"], required=True
    )
    parser.add_argument("--expected-version", type=int, required=True)
    parser.add_argument("--value", required=True, help="Bounded JSON value")
    args = parser.parse_args()
    settings = Settings()
    if settings.database_url is None:
        parser.error("DATABASE_URL required")
    url = make_url(settings.database_url.get_secret_value())
    if (
        url.host not in {"localhost", "127.0.0.1"}
        or url.query
        or args.confirm_database != url.database
        or not (url.database == "airc_foundation" or url.database.startswith("airc_test_catalog_"))
    ):
        parser.error("Refusing database outside confirmed project loopback dev/test scope")
    if len(args.value.encode()) > 4096:
        parser.error("Value too large")
    value = json.loads(args.value)
    database = Database(settings)
    try:
        with Session(database.engine) as session, session.begin():
            if session.scalar(text("SELECT current_database()")) != args.confirm_database:
                raise RuntimeError("Database identity mismatch")
            result = change_state(
                session,
                room_id=args.room_id,
                target_kind=args.target_kind,
                target_id=args.target_id,
                state_type=args.state_type,
                value=value,
                expected_version=args.expected_version,
            )
        print(json.dumps(result))
    finally:
        database.close()


if __name__ == "__main__":
    main()
