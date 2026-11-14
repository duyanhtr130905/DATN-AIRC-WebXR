"""Explicit synthetic writer; never imported as a public mutation route."""

import argparse
import json
from pathlib import Path
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
    values = parser.add_mutually_exclusive_group(required=True)
    values.add_argument("--value", help="Bounded JSON value")
    values.add_argument("--value-file", type=Path, help="JSON file within project workspace")
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
    raw_value = args.value
    if args.value_file is not None:
        value_path = args.value_file.resolve()
        project_root = Path(__file__).resolve().parents[5]
        if (
            not value_path.is_relative_to(project_root)
            or not value_path.is_file()
            or value_path.stat().st_size > 4096
        ):
            parser.error("Value file must be a bounded project-local file")
        raw_value = value_path.read_text(encoding="utf-8")
    if len(raw_value.encode()) > 4096:
        parser.error("Value too large")
    value = json.loads(raw_value)
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
