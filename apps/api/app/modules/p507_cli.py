"""Run M3 fixture operations only on a confirmed disposable local database."""

import argparse
import json
import time
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.connection import Database
from app.modules.p507 import (
    REVISION,
    ROOM_ID,
    evidence,
    ingest,
    parse_observation,
    validate_mapping,
    verify_manifest,
)


def main():
    parser = argparse.ArgumentParser(description="P507 provisional synthetic fixture")
    parser.add_argument("--confirm-database", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--seed-manifest", type=Path)
    mode.add_argument("--observation", type=Path)
    parser.add_argument("--authorize-synthetic", choices=[REVISION], required=True)
    args = parser.parse_args()
    settings = Settings()
    if settings.database_url is None:
        parser.error("DATABASE_URL required")
    url = make_url(settings.database_url.get_secret_value())
    name = url.database or ""
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in {"localhost", "127.0.0.1"}
        or url.query
        or name != args.confirm_database
        or not (
            name.startswith("airc_test_catalog_")
            or (name == "airc_foundation" and args.seed_manifest is not None)
        )
    ):
        parser.error(
            "Use a confirmed project database for seed or a disposable database for observations"
        )
    if args.seed_manifest:
        lock, ids = evidence()
        with args.seed_manifest.open("rb") as stream:
            verify_manifest(stream.read(200000), lock, ids)
    else:
        with args.observation.open("rb") as stream:
            observation = parse_observation(stream.read(8193))
    database = Database(settings)
    try:
        started = time.time_ns()
        with Session(database.engine) as session, session.begin():
            if session.scalar(text("SELECT current_database()")) != name:
                raise RuntimeError("Database identity mismatch")
            if args.seed_manifest:
                mapping = validate_mapping(session, seed=True)
                result = {
                    "room_id": str(ROOM_ID),
                    "matched": len(mapping),
                    "unmatched": 0,
                    "duplicates": 0,
                    "revision": REVISION,
                }
            else:
                result = ingest(session, observation, authorization=args.authorize_synthetic)
        print(json.dumps({**result, "ingest_started_ns": started, "commit_ack_ns": time.time_ns()}))
    finally:
        database.close()


if __name__ == "__main__":
    main()
