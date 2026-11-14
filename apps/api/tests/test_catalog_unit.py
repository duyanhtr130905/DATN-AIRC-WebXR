import base64
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.core.config import Settings
from app.database.models import Base, Object, Room
from app.database.session import get_session
from app.main import create_app
from app.modules.catalog.schemas import RoomResponse, public_metadata
from app.modules.catalog.service import decode_cursor, encode_cursor


def test_orm_ddl_has_catalog_constraints():
    assert set(Base.metadata.tables) == {"rooms", "objects"}
    for model in (Room, Object):
        sql = str(CreateTable(model.__table__).compile(dialect=postgresql.dialect()))
        assert "JSONB" in sql and "TIMESTAMP WITH TIME ZONE" in sql
        assert "source_kind IN" in sql
    assert "ON DELETE RESTRICT" in str(
        CreateTable(Object.__table__).compile(dialect=postgresql.dialect())
    )


@pytest.mark.parametrize(
    "value",
    [
        "bad!",
        "e30",
        "W10",
        "bnVsbA",
        base64.urlsafe_b64encode(b'{"v":true,"scope":"rooms","after":12}').decode(),
    ],
)
def test_invalid_cursor_is_validation_error(value):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as error:
        decode_cursor(value, "rooms")
    assert error.value.status_code == 422


def test_cursor_scope_and_roundtrip():
    from fastapi import HTTPException

    identity = UUID("10000000-0000-4000-8000-000000000001")
    cursor = encode_cursor("rooms", identity)
    assert decode_cursor(cursor, "rooms") == identity
    with pytest.raises(HTTPException):
        decode_cursor(cursor, "room:another")


def test_metadata_allowlist_and_response_validation():
    result = public_metadata({"description": "demo", "private_note": "secret", "label": {"x": 1}})
    assert result.model_dump() == {"label": None, "description": "demo"}
    assert public_metadata({"description": "x" * 513}).description is None
    with pytest.raises(ValidationError):
        RoomResponse(
            id="bad",
            code="demo",
            name="demo",
            source_kind="real_verified",
            metadata={},
            created_at="2026-11-14T00:00:00",
            updated_at="bad",
        )


def test_api_validation_empty_and_no_mutation_routes():
    application = create_app(Settings(_env_file=None, database_url=None))
    session = Mock()
    session.scalars.return_value = []
    session.scalar.return_value = None
    application.dependency_overrides[get_session] = lambda: session
    with TestClient(application) as client:
        assert client.get("/api/v1/rooms").json() == {
            "data": [],
            "meta": {"schema_version": 1, "next_cursor": None},
        }
        for url in [
            "/api/v1/rooms?limit=0",
            "/api/v1/rooms?limit=101",
            "/api/v1/rooms?cursor=bad!",
            "/api/v1/objects/not-uuid",
            "/api/v1/rooms/not-uuid/objects",
        ]:
            response = client.get(url)
            assert response.status_code == 422
            assert "error" in response.json()
        assert client.get("/api/v1/objects/00000000-0000-4000-8000-000000000099").status_code == 404
        schema = client.get("/openapi.json").json()
        assert all(
            set(value) == {"get"}
            for key, value in schema["paths"].items()
            if key.startswith("/api/v1")
        )
        assert client.post("/api/v1/rooms", json={}).status_code == 405
        assert (
            client.patch(
                "/api/v1/objects/00000000-0000-4000-8000-000000000099", json={}
            ).status_code
            == 405
        )


def test_catalog_without_database_is_unavailable_and_redacted():
    with TestClient(create_app(Settings(_env_file=None, database_url=None))) as client:
        response = client.get("/api/v1/rooms")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
        assert "postgresql" not in response.text


def test_explicit_seed_refuses_unrelated_database(monkeypatch):
    from app.modules.catalog import seed

    monkeypatch.setattr("sys.argv", ["seed", "--confirm-database", "unrelated_db"])
    monkeypatch.setattr(
        seed,
        "Settings",
        lambda: Settings(
            _env_file=None, database_url="postgresql+psycopg://user@127.0.0.1/unrelated_db"
        ),
    )
    database = Mock()
    monkeypatch.setattr(seed, "Database", database)
    with pytest.raises(SystemExit) as error:
        seed.main()
    assert error.value.code == 2
    database.assert_not_called()


def test_alembic_offline_sql_and_guard(monkeypatch):
    from argparse import Namespace
    from io import StringIO
    from pathlib import Path

    from alembic.config import Config

    from alembic import command

    name = "airc_test_catalog_offline"
    monkeypatch.setenv("DATABASE_URL", f"postgresql+psycopg://test@127.0.0.1/{name}")
    output = StringIO()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"), output_buffer=output)
    config.cmd_opts = Namespace(x=[f"confirm_catalog_database={name}"])
    command.upgrade(config, "head", sql=True)
    sql = output.getvalue()
    assert "CREATE TABLE rooms" in sql and "CREATE TABLE objects" in sql
    assert "ON DELETE RESTRICT" in sql
    assert "INSERT INTO rooms" not in sql and "INSERT INTO objects" not in sql
    config.cmd_opts = Namespace(x=[])
    with pytest.raises(RuntimeError, match="confirmation required"):
        command.upgrade(config, "head", sql=True)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://test@127.0.0.1/airc_foundation_test?host=example.invalid&dbname=unrelated",
        "postgresql+psycopg://test@example.invalid/airc_foundation_test",
        "postgresql+psycopg://test@127.0.0.1/unrelated",
    ],
)
def test_postgres_fixture_refuses_override_before_connect(monkeypatch, url):
    import test_catalog_postgres as postgres_tests

    monkeypatch.setenv("TEST_DATABASE_URL", url)
    monkeypatch.setenv("AIRC_ALLOW_TEST_DATABASES", "1")
    connect = Mock(side_effect=AssertionError("Must not connect to rejected target"))
    monkeypatch.setattr(postgres_tests, "create_engine", connect)
    fixture = postgres_tests.catalog_database.__wrapped__()
    try:
        with pytest.raises(pytest.fail.Exception):
            next(fixture)
    finally:
        fixture.close()
    connect.assert_not_called()
