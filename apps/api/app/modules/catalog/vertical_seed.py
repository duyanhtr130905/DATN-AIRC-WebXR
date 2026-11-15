"""Explicit M1-C fixture; no AIRC data and never called during startup."""

import argparse
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.connection import Database
from app.database.models import Object, Room
from app.database.state_models import CurrentState
from app.modules.catalog.seed import LABEL
from app.modules.state.service import change_state, public_state, visible_states

ROOM_IDS = [uuid5(NAMESPACE_URL, f"airc-synthetic-m1-c/room/{i}") for i in range(2)]
OBJECT_IDS = [uuid5(NAMESPACE_URL, f"airc-synthetic-m1-c/object/{i}") for i in range(21)]


def seed_vertical_slice(session: Session):
    session.execute(text("SELECT pg_advisory_xact_lock(817405121)"))
    for index, identity in enumerate(ROOM_IDS):
        expected = dict(
            id=identity,
            code=f"DEMO-VERTICAL-{index + 1}",
            name=f"Synthetic vertical room {index + 1}",
            source_kind="synthetic",
            metadata_json={"label": LABEL},
        )
        existing = session.get(Room, identity)
        if existing is None:
            session.add(Room(**expected))
        elif any(getattr(existing, key) != value for key, value in expected.items()):
            raise RuntimeError("Fixture room collision; refusing overwrite")
    session.flush()
    for index, identity in enumerate(OBJECT_IDS):
        expected = dict(
            id=identity,
            room_id=ROOM_IDS[0 if index < 20 else 1],
            name=f"Synthetic primitive {index + 1:02d}",
            type="demo_primitive",
            source_kind="synthetic",
            metadata_json={
                "label": LABEL,
                "description": "Synthetic primitive; layout is not room507",
            },
            transform=None,
        )
        existing = session.get(Object, identity)
        if existing is None:
            session.add(Object(**expected))
        elif any(getattr(existing, key) != value for key, value in expected.items()):
            raise RuntimeError("Fixture object collision; refusing overwrite")
    session.flush()
    specifications = [
        (room, "room", room, "room_schedule", {"status": "free", "activity": "SYNTHETIC demo"})
        for room in ROOM_IDS
    ]
    for index, identity in enumerate(OBJECT_IDS):
        room = ROOM_IDS[0 if index < 20 else 1]
        specifications.extend(
            [
                (room, "object", identity, "equipment_status", {"status": "available"}),
                (
                    room,
                    "object",
                    identity,
                    "exhibit_info",
                    {"title": "SYNTHETIC", "text": "NOT AIRC REAL DATA"},
                ),
            ]
        )
    for room, kind, target, state_type, value in specifications:
        query = visible_states(room).where(CurrentState.state_type == state_type)
        query = (
            query.where(CurrentState.target_room_id == target)
            if kind == "room"
            else query.where(CurrentState.object_id == target)
        )
        existing = session.scalar(query)
        if existing is not None:
            public_state(existing)  # Validate; preserve subsequent explicit dev updates.
            continue
        change_state(
            session,
            room_id=room,
            target_kind=kind,
            target_id=target,
            state_type=state_type,
            value=value,
            expected_version=0,
        )


def main():
    parser = argparse.ArgumentParser(description=LABEL)
    parser.add_argument("--confirm-database", required=True)
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
        or args.confirm_database != name
        or not (name == "airc_foundation" or name.startswith("airc_test_catalog_"))
    ):
        parser.error("Refusing database outside confirmed project loopback dev/test scope")
    database = Database(settings)
    try:
        with Session(database.engine) as session, session.begin():
            if session.scalar(text("SELECT current_database()")) != name:
                raise RuntimeError("Database identity mismatch")
            seed_vertical_slice(session)
        print(
            "Committed synthetic fixture:20objects/41states in firstroom; "
            "1object/3states in second; "
            + LABEL
        )
    finally:
        database.close()


if __name__ == "__main__":
    main()
