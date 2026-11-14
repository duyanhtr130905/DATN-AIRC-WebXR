import os
import subprocess
import sys
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, func, insert, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from starlette.requests import Request

from alembic import command
from app.core.config import Settings
from app.database.connection import Database
from app.database.models import Object, Room
from app.database.session import get_session
from app.main import create_app
from app.modules.catalog.seed import LABEL, OBJECT_IDS, ROOM_ID, seed_demo

pytestmark = pytest.mark.postgres
API_ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def isolated_catalog_database(migrate=True):
    raw = os.environ.get("TEST_DATABASE_URL")
    if not raw or os.environ.get("AIRC_ALLOW_TEST_DATABASES") != "1":
        pytest.fail("Requires explicit TEST_DATABASE_URL + AIRC_ALLOW_TEST_DATABASES=1")
    url = make_url(raw)
    if (
        url.drivername != "postgresql+psycopg"
        or url.database != "airc_foundation_test"
        or url.host not in {"127.0.0.1", "localhost"}
        or url.query
    ):
        pytest.fail("Refusing non-loopback or non-project disposable test database")
    # New database per test. Never DROP/reset a pre-existing database; CI destroys its own service.
    name = "airc_test_catalog_" + uuid4().hex
    administrator = create_engine(url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        with administrator.connect() as connection:
            assert connection.scalar(text("SELECT current_database()")) == "airc_foundation_test"
            connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
    finally:
        administrator.dispose()
    target = url.set(database=name).render_as_string(hide_password=False)
    database = Database(Settings(_env_file=None, database_url=target))
    try:
        with database.engine.begin() as connection:
            assert connection.scalar(text("SELECT current_database()")) == name
            assert inspect(connection).get_table_names() == []
            if migrate:
                config = Config(str(API_ROOT / "alembic.ini"))
                config.attributes["connection"] = connection
                command.upgrade(config, "head")
        yield database, SecretStr(target)
    finally:
        database.close()


@pytest.fixture
def catalog_database():
    with isolated_catalog_database() as result:
        yield result


def seed(database):
    with Session(database.engine) as session, session.begin():
        seed_demo(session)


def test_migration_empty_database_head_repeat_and_model_drift(catalog_database):
    database, _ = catalog_database
    with database.engine.begin() as connection:
        output = StringIO()
        config = Config(str(API_ROOT / "alembic.ini"), stdout=output)
        config.attributes["connection"] = connection
        assert set(inspect(connection).get_table_names()) == {"rooms", "objects", "alembic_version"}
        assert connection.scalar(select(func.count()).select_from(Room)) == 0
        assert connection.scalar(select(func.count()).select_from(Object)) == 0
        command.current(config)
        assert "0001_catalog" in output.getvalue()
        command.upgrade(config, "head")
        command.check(config)
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001_catalog"
        inspector = inspect(connection)
        assert inspector.get_foreign_keys("objects")[0]["options"]["ondelete"] == "RESTRICT"
        assert any(
            index["name"] == "ix_objects_room_source_id"
            for index in inspector.get_indexes("objects")
        )
        assert any(
            unique["column_names"] == ["code"]
            for unique in inspector.get_unique_constraints("rooms")
        )
        for table in ["rooms", "objects"]:
            assert {"id"} == set(inspector.get_pk_constraint(table)["constrained_columns"])
            columns = {column["name"]: column for column in inspector.get_columns(table)}
            assert columns["created_at"]["type"].timezone is True
            assert columns["name"]["nullable"] is False
            assert len(inspector.get_check_constraints(table)) >= 4


@pytest.mark.parametrize(
    "kind",
    [
        "duplicate_id",
        "duplicate_code",
        "null_source",
        "duplicate_object_id",
        "invalid_source",
        "null_name",
        "empty_code",
        "bad_metadata",
        "huge_metadata",
        "unproven_verified",
        "invalid_fk",
        "null_room",
        "bad_transform",
        "empty_type",
        "restrict",
    ],
)
def test_database_constraints(catalog_database, kind):
    database, _ = catalog_database
    seed(database)
    room = {"id": uuid4(), "code": "NEW", "name": "Test", "source_kind": "synthetic"}
    obj = {
        "id": uuid4(),
        "room_id": ROOM_ID,
        "name": "Test",
        "type": "demo",
        "source_kind": "synthetic",
    }
    with pytest.raises(DBAPIError), database.engine.begin() as connection:
        if kind == "restrict":
            connection.execute(text("DELETE FROM rooms WHERE id=:id"), {"id": ROOM_ID})
        elif kind in {
            "invalid_fk",
            "null_room",
            "bad_transform",
            "empty_type",
            "duplicate_object_id",
        }:
            obj.update(
                {
                    "invalid_fk": {"room_id": uuid4()},
                    "duplicate_object_id": {"id": OBJECT_IDS[0]},
                    "null_room": {"room_id": None},
                    "bad_transform": {"transform": []},
                    "empty_type": {"type": " "},
                }[kind]
            )
            connection.execute(insert(Object.__table__).values(**obj))
        else:
            room.update(
                {
                    "duplicate_id": {"id": ROOM_ID},
                    "duplicate_code": {"code": "DEMO-CATALOG"},
                    "invalid_source": {"source_kind": "invented"},
                    "null_source": {"source_kind": None},
                    "null_name": {"name": None},
                    "empty_code": {"code": " "},
                    "bad_metadata": {"metadata": []},
                    "huge_metadata": {"metadata": {"label": "x" * 9000}},
                    "unproven_verified": {"source_kind": "real_verified"},
                }[kind]
            )
            connection.execute(insert(Room.__table__).values(**room))
    assert database.engine.pool.checkedout() == 0


def test_seed_idempotency_and_collision_no_overwrite(catalog_database):
    database, _ = catalog_database
    seed(database)
    seed(database)
    with Session(database.engine) as session:
        assert session.scalar(select(func.count()).select_from(Room)) == 1
        assert session.scalar(select(func.count()).select_from(Object)) == 4
        assert session.get(Room, ROOM_ID).metadata_json["label"] == LABEL
        assert session.get(Object, OBJECT_IDS[0]).transform is None
    with database.engine.begin() as connection:
        connection.execute(
            text("UPDATE rooms SET name='Unrelated data' WHERE id=:id"), {"id": ROOM_ID}
        )
    with pytest.raises(RuntimeError), Session(database.engine) as session, session.begin():
        seed_demo(session)
    with Session(database.engine) as session:
        assert session.get(Room, ROOM_ID).name == "Unrelated data"


def test_timestamps_roundtrip_and_nullable_transform(catalog_database):
    database, _ = catalog_database
    given = datetime(2026, 11, 14, 15, 0, tzinfo=timezone(timedelta(hours=7)))
    with database.engine.begin() as connection:
        connection.execute(
            insert(Room).values(
                id=ROOM_ID, code="TZ", name="Demo", created_at=given, updated_at=given
            )
        )
    with Session(database.engine) as session:
        value = session.get(Room, ROOM_ID)
        assert value.created_at.tzinfo is not None
        assert value.created_at.astimezone(UTC) == given.astimezone(UTC)


def test_api_empty_and_actual_session_read_only(catalog_database):
    database, target = catalog_database
    with TestClient(create_app(Settings(_env_file=None, database_url=target))) as client:
        assert client.get("/api/v1/rooms").json()["data"] == []
        assert client.get(f"/api/v1/rooms/{ROOM_ID}/objects").status_code == 404
        assert client.get(f"/api/v1/objects/{OBJECT_IDS[0]}").status_code == 404
        request = Request({"type": "http", "app": client.app})
        dependency = get_session(request)
        session = next(dependency)
        try:
            assert session.scalar(text("SHOW transaction_read_only")) == "on"
            with pytest.raises(DBAPIError):
                session.execute(insert(Room).values(id=uuid4(), code="DENIED", name="Denied"))
        finally:
            dependency.close()
        assert client.app.state.database.engine.pool.checkedout() == 0
    assert database.engine.pool.checkedout() == 0


def test_api_pagination_privacy_multiroom_and_validation(catalog_database):
    database, target = catalog_database
    seed(database)
    second = uuid4()
    hidden = uuid4()
    hidden_child = uuid4()
    verified = uuid4()
    with database.engine.begin() as connection:
        connection.execute(
            insert(Room).values(
                id=second, code="DEMO-2", name="Second demo", source_kind="synthetic"
            )
        )
        connection.execute(
            insert(Room).values(id=hidden, code="UNPUBLISHED", name="Hidden", source_kind="unknown")
        )
        connection.execute(
            insert(Object).values(
                id=hidden_child,
                room_id=hidden,
                name="Hidden child",
                type="demo",
                source_kind="synthetic",
            )
        )
        connection.execute(
            Object.__table__.update()
            .where(Object.id == OBJECT_IDS[0])
            .values(
                evidence_ref="private-evidence",
                external_reference="private-serial",
                metadata={
                    "label": LABEL,
                    "private_note": "PRIVATE-MARKER",
                    "nested": {"key": "private"},
                },
            )
        )
        connection.execute(
            insert(Object).values(
                id=uuid4(),
                room_id=ROOM_ID,
                name="Unknown object",
                type="demo",
                source_kind="unknown",
            )
        )
    with database.engine.begin() as connection:
        connection.execute(
            insert(Object).values(
                id=verified,
                room_id=ROOM_ID,
                name="Verified hidden",
                type="demo",
                source_kind="real_verified",
                evidence_ref="private-ref",
            )
        )
    with TestClient(create_app(Settings(_env_file=None, database_url=target))) as client:
        result = client.get("/api/v1/rooms?limit=1")
        assert result.status_code == 200
        first = result.json()
        second_page = client.get(
            "/api/v1/rooms", params={"limit": 1, "cursor": first["meta"]["next_cursor"]}
        ).json()
        identities = [first["data"][0]["id"], second_page["data"][0]["id"]]
        assert identities == sorted(identities)
        assert len(set(identities)) == 2
        assert second_page["meta"]["next_cursor"] is None
        assert client.get(f"/api/v1/rooms/{second}/objects").json()["data"] == []
        assert client.get(f"/api/v1/rooms/{hidden}/objects").status_code == 404
        assert client.get(f"/api/v1/objects/{hidden_child}").status_code == 404
        assert client.get(f"/api/v1/objects/{verified}").status_code == 404
        objects = []
        cursor = None
        while True:
            params = {"limit": 2}
            if cursor:
                params["cursor"] = cursor
            response = client.get(f"/api/v1/rooms/{ROOM_ID}/objects", params=params)
            assert response.status_code == 200
            page = response.json()
            objects.extend(page["data"])
            cursor = page["meta"]["next_cursor"]
            if not cursor:
                break
        assert [row["id"] for row in objects] == sorted(str(identity) for identity in OBJECT_IDS)
        detail = client.get(f"/api/v1/objects/{OBJECT_IDS[0]}")
        assert detail.status_code == 200
        assert "evidence_ref" not in detail.text and "external_reference" not in detail.text
        assert "PRIVATE-MARKER" not in detail.text and "private-evidence" not in detail.text
        assert detail.json()["data"]["source_kind"] == "synthetic"
        assert (
            client.get(
                f"/api/v1/rooms/{ROOM_ID}/objects", params={"cursor": first["meta"]["next_cursor"]}
            ).status_code
            == 422
        )
        assert client.get("/api/v1/rooms?limit=101").status_code == 422
        assert client.get("/api/v1/objects/invalid").status_code == 422
        assert client.app.state.database.engine.pool.checkedout() == 0


def test_parent_visibility_is_filtered_in_same_object_query(catalog_database):
    from unittest.mock import patch

    from app.modules.catalog import service

    database, _ = catalog_database
    seed(database)
    with Session(database.engine) as session:
        original = session.scalar

        def changed_between_checks(statement):
            value = original(statement)
            # Simulate operator changing parent classification after the 404 guard read.
            session.execute(
                Room.__table__.update().where(Room.id == ROOM_ID).values(source_kind="unknown")
            )
            return value

        with patch.object(session, "scalar", side_effect=changed_between_checks):
            rows, cursor = service.objects_page(session, ROOM_ID, 25, None)
        assert rows == [] and cursor is None
        session.rollback()


def test_actual_cli_migration_and_seed_on_new_database():
    with isolated_catalog_database(migrate=False) as (database, secret_url):
        url = make_url(secret_url.get_secret_value())
        env = {**os.environ, "DATABASE_URL": secret_url.get_secret_value()}
        args = [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(API_ROOT / "alembic.ini"),
            "-x",
            f"confirm_catalog_database={url.database}",
        ]
        for action in [["upgrade", "head"], ["current"], ["upgrade", "head"], ["check"]]:
            result = subprocess.run(
                args + action, cwd=API_ROOT, env=env, capture_output=True, text=True, timeout=30
            )
            assert result.returncode == 0, f"Alembic CLI {action[0]} failed; see isolated test"
            if action == ["current"]:
                assert "0001_catalog (head)" in result.stdout
        for _ in range(2):
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "app.modules.catalog.seed",
                    "--confirm-database",
                    url.database,
                ],
                cwd=API_ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, "Explicit synthetic seed CLI failed"
        with Session(database.engine) as session:
            assert session.scalar(select(func.count()).select_from(Room)) == 1
            assert session.scalar(select(func.count()).select_from(Object)) == 4
        assert database.engine.pool.checkedout() == 0
