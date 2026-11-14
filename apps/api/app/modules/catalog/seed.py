"""Explicit synthetic seed. Never invoked by application startup or migration."""

import argparse
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.connection import Database
from app.database.models import Object, Room

LABEL = "SYNTHETIC — NOT AIRC REAL DATA"
ROOM_ID = UUID("10000000-0000-4000-8000-000000000001")
OBJECT_IDS = [UUID(f"20000000-0000-4000-8000-{i:012d}") for i in range(1, 5)]


def seed_demo(session: Session) -> None:
    # Serialize this fixture command; collisions never overwrite unrelated data.

    session.execute(text("SELECT pg_advisory_xact_lock(817405120)"))
    rooms = [
        {
            "id": ROOM_ID,
            "code": "DEMO-CATALOG",
            "name": "Generic DEMO room",
            "source_kind": "synthetic",
            "metadata": {"label": LABEL},
        }
    ]
    objects = [
        {
            "id": identity,
            "room_id": ROOM_ID,
            "name": f"Synthetic object {i}",
            "type": "demo_primitive",
            "source_kind": "synthetic",
            "metadata": {"label": LABEL, "description": "Generic test fixture"},
            "transform": None,
        }
        for i, identity in enumerate(OBJECT_IDS, 1)
    ]
    for model, rows in [(Room, rooms), (Object, objects)]:
        for row in rows:
            existing = session.get(model, row["id"])
            if existing is not None:
                matches = all(
                    getattr(existing, "metadata_json" if key == "metadata" else key) == value
                    for key, value in row.items()
                )
                if not matches:
                    raise RuntimeError("Fixture ID collision; no existing data overwritten")
                continue
            session.execute(insert(model.__table__).values(**row))


def main():
    parser = argparse.ArgumentParser(description=LABEL)
    parser.add_argument(
        "--confirm-database", required=True, help="Exact isolated project dev/test database name"
    )
    args = parser.parse_args()
    settings = Settings()
    if settings.database_url is None:
        parser.error("DATABASE_URL required")
    from sqlalchemy.engine import make_url

    url = make_url(settings.database_url.get_secret_value())
    name = url.database
    allowed = name == "airc_foundation" or name.startswith("airc_test_catalog_")
    if (
        not allowed
        or args.confirm_database != name
        or url.host not in {"127.0.0.1", "localhost"}
        or url.query
    ):
        parser.error("Refusing database outside explicit project dev/test allowlist")
    database = Database(settings)
    try:
        with Session(database.engine) as session, session.begin():
            actual = session.scalar(text("SELECT current_database()"))
            if actual != args.confirm_database:
                raise RuntimeError("Database identity mismatch")
            seed_demo(session)
        print("Synthetic Catalog fixture committed; " + LABEL)
    finally:
        database.close()


if __name__ == "__main__":
    main()
