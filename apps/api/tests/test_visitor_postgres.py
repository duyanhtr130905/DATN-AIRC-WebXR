import csv
import io
import json
import os
import platform
import secrets
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import JSON, MetaData, func, inspect, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from test_catalog_postgres import API_ROOT, isolated_catalog_database
from visitor_oracle import expected_visits

from alembic import command
from app.core.config import Settings
from app.database.admin_models import AdminAccount, AdminAudit
from app.database.connection import Database
from app.database.visitor_models import VisitorEvent, VisitorSession, VisitorStartAttempt
from app.main import create_app
from app.modules.admin_auth import hash_password
from app.modules.catalog.seed import OBJECT_IDS, ROOM_ID, seed_demo
from app.modules.state.service import change_state
from app.modules.visitor import COOKIE, INTENT_COOKIE, PATH, ROOM, digest

pytestmark = pytest.mark.postgres
ORIGIN = "http://127.0.0.1:5173"
REPORT = "/api/v1/admin/visitor-reports"
HEAD = "0007_visitor_terminal_capacity"
ROOT = API_ROOT.parents[1]


@pytest.fixture
def local_database():
    with isolated_catalog_database() as data:
        yield data


def client_for(url, *, enabled=True, host="127.0.0.1", connected="127.0.0.1", admin=True):
    return TestClient(
        create_app(
            Settings(
                _env_file=None,
                database_url=url,
                visitor_synthetic_enabled=enabled,
                admin_enabled=admin,
                realtime_dispatcher_enabled=False,
            )
        ),
        base_url=f"http://{host}:5173",
        client=(connected, 55000),
        headers={"origin": ORIGIN, "x-airc-visitor": "1"},
    )


def prepare_start(client, previous=None):
    body = {
        "consent": "synthetic_opt_in_v1",
        "attempt_id": str(uuid4()),
        "previous_id": previous.rsplit("/", 1)[-1] if previous else None,
    }
    response = client.post(PATH + "/sessions/intent", json=body)
    assert response.status_code == 200
    assert response.json() == {"prepared": True}
    assert "HttpOnly" in response.headers["set-cookie"]
    return body


def opt_in(client):
    response = client.post(PATH + "/sessions", json=prepare_start(client))
    assert response.status_code == 201, response.text
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=strict" in response.headers["set-cookie"]
    assert "token" not in response.json()
    return PATH + "/sessions/" + response.json()["id"]


def event(kind="room_enter", *, time=None):
    return {
        "id": str(uuid4()),
        "schema_version": 1,
        "event_type": kind,
        "occurred_at": (time or datetime.now(UTC)).isoformat(),
        "room_id": ROOM,
        "object_id": None if kind in ("room_enter", "session_end") else "demo-object-cube",
    }


def send(client, path, *events):
    return client.post(path + "/events", json={"events": events})


def login_password(database):
    password = secrets.token_urlsafe(24)
    with Session(database.engine) as db, db.begin():
        db.add(
            AdminAccount(username="visitor_qa", password_hash=hash_password(password), active=True)
        )
    return password


def login(client, password):
    result = client.post(
        "/api/v1/admin/login", json={"username": "visitor_qa", "password": password}
    )
    assert result.status_code == 200
    return {"X-Admin-CSRF": result.json()["csrf"]}


def counts(database):
    with Session(database.engine) as db:
        return (
            db.scalar(select(func.count()).select_from(VisitorSession)),
            db.scalar(select(func.count()).select_from(VisitorEvent)),
        )


def dates():
    today = datetime.now(UTC).date()
    return f"start={today - timedelta(days=1)}&until={today + timedelta(days=2)}"


def test_migration_populated_0004_backup_restore_forward_only_and_guard():
    with (
        isolated_catalog_database(migrate=False) as (database, _),
        isolated_catalog_database(migrate=False) as (restore, _),
    ):
        config = Config(str(API_ROOT / "alembic.ini"))
        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0004_admin_provenance")
            with Session(connection) as db:
                seed_demo(db)
                db.flush()
                change_state(
                    db,
                    room_id=ROOM_ID,
                    target_kind="object",
                    target_id=OBJECT_IDS[0],
                    state_type="equipment_status",
                    value={"status": "available"},
                    expected_version=0,
                )
                db.add(
                    AdminAudit(
                        operation="m4_preflight",
                        outcome="success",
                        provenance="SYNTHETIC_TEST",
                        source_note="synthetic backup fixture",
                    )
                )
                db.flush()
            metadata = MetaData()
            metadata.reflect(connection)
            snapshot = {
                table.name: [dict(row) for row in connection.execute(select(table)).mappings()]
                for table in metadata.sorted_tables
                if table.name != "alembic_version"
            }
        assert all(
            snapshot[name]
            for name in ("rooms", "objects", "state_history", "outbox", "admin_audit")
        )
        with restore.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0004_admin_provenance")
            for table in metadata.sorted_tables:
                for column in table.columns:
                    if isinstance(column.type, JSON):
                        column.type.none_as_null = True
                if snapshot.get(table.name):
                    connection.execute(table.insert(), snapshot[table.name])
            command.upgrade(config, "head")
            for name, original in snapshot.items():
                actual = connection.execute(select(metadata.tables[name])).mappings()
                assert sorted(map(repr, map(dict, actual))) == sorted(map(repr, original))

        with database.engine.connect() as connection:
            with connection.begin() as transaction:
                config.attributes["connection"] = connection
                command.upgrade(config, HEAD)
                assert {"visitor_events", "visitor_start_attempts"}.issubset(
                    inspect(connection).get_table_names()
                )
                transaction.rollback()
            assert "visitor_start_attempts" not in inspect(connection).get_table_names()
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version"))
                == "0004_admin_provenance"
            )

        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, HEAD)
            command.check(config)
            for name, original in snapshot.items():
                actual = connection.execute(select(metadata.tables[name])).mappings()
                assert sorted(map(repr, map(dict, actual))) == sorted(map(repr, original))
            assert connection.scalar(text("SHOW server_version_num")).startswith("18")
        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            with pytest.raises(RuntimeError, match="Forward-only"):
                command.downgrade(config, "0004_admin_provenance")
        assert counts(database) == (0, 0)

    raw = os.environ["TEST_DATABASE_URL"]
    guard = Database(Settings(_env_file=None, database_url=raw))
    try:
        from alembic.script import ScriptDirectory

        migration = ScriptDirectory.from_config(config).get_revision(HEAD).module
        with guard.engine.begin() as connection:
            from alembic.migration import MigrationContext
            from alembic.operations import Operations

            with Operations.context(MigrationContext.configure(connection)):
                with pytest.raises(RuntimeError, match="verified loopback project database"):
                    migration.upgrade()
            assert "visitor_start_attempts" not in inspect(connection).get_table_names()
    finally:
        guard.close()


def test_upgrade_retains_existing_0005_visits():
    with isolated_catalog_database(migrate=False) as (database, url):
        config = Config(str(API_ROOT / "alembic.ini"))
        now = datetime.now(UTC)
        session_id, event_id = uuid4(), uuid4()
        proof = secrets.token_urlsafe(32)
        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0005_visitor_sessions")
            connection.execute(
                VisitorSession.__table__.insert().values(
                    id=session_id,
                    token_digest=digest(proof),
                    token_expires_at=now + timedelta(hours=1),
                    started_at=now,
                    last_seen_at=now,
                    ended_at=now,
                    event_count=1,
                )
            )
            connection.execute(
                VisitorEvent.__table__.insert().values(
                    id=event_id,
                    session_id=session_id,
                    ordinal=1,
                    event_type="session_start",
                    room_id=ROOM,
                    occurred_at=now,
                    received_at=now,
                )
            )
            command.upgrade(config, HEAD)
            command.check(config)
        with client_for(url) as client:
            client.cookies.set(COOKIE, proof, domain="127.0.0.1", path=PATH)
            path = f"{PATH}/sessions/{session_id}"
            assert client.get(path).json()["ended"]
            response = client.post(PATH + "/sessions", json=prepare_start(client, path))
            assert response.status_code == 201
        with Session(database.engine) as db:
            assert db.get(VisitorEvent, event_id).session_id == session_id
            assert db.get(VisitorSession, session_id).ended_at == now
        assert counts(database) == (2, 2)


def test_default_no_consent_and_origin_proxy_database_guards(local_database):
    database, url = local_database
    with client_for(url, enabled=False) as disabled:
        assert disabled.get(PATH + "/status").status_code == 404
        assert (
            disabled.post(PATH + "/sessions", json={"consent": "synthetic_opt_in_v1"}).status_code
            == 404
        )
        assert disabled.get(REPORT + "?" + dates()).status_code == 404
    with client_for(url) as client:
        assert client.get(PATH + "/status").status_code == 200
        assert client.get("/api/v1/rooms").status_code == 200
        assert client.post(PATH + "/sessions", json={}).status_code == 422
        assert client.post(PATH + "/sessions", json={"consent": "visitor"}).status_code == 422
        assert (
            client.post(
                PATH + "/sessions", content="{}", headers={"content-type": "text/plain"}
            ).status_code
            == 415
        )
        for headers in (
            {"origin": "https://example.invalid"},
            {"sec-fetch-site": "same-site"},
            {"x-forwarded-for": "127.0.0.1"},
            {"x-airc-visitor": "0"},
        ):
            assert (
                client.post(
                    PATH + "/sessions", json={"consent": "synthetic_opt_in_v1"}, headers=headers
                ).status_code
                == 403
            )
        body = prepare_start(client)
        assert (
            client.post(
                PATH + "/sessions",
                json=body,
                headers={"cookie": f"{INTENT_COOKIE}={body['attempt_id']}.{'a' * 43}"},
            ).status_code
            == 401
        )
        with Session(database.engine) as db, db.begin():
            db.execute(update(VisitorStartAttempt).values(expires_at=datetime.now(UTC)))
        assert client.post(PATH + "/sessions", json=body).status_code == 401
    with client_for(url, host="localhost") as client:
        assert client.get(PATH + "/status").status_code == 403
    with client_for(url, connected="192.0.2.10") as client:
        assert client.get(PATH + "/status").status_code == 403
    with client_for(os.environ["TEST_DATABASE_URL"]) as client:
        assert client.get(PATH + "/status").status_code == 404
    assert counts(database) == (0, 0)


def test_receipts_collisions_bounds_reversed_events_and_revocation(local_database):
    database, url = local_database
    with client_for(url) as client, client_for(url) as outsider:
        path = opt_in(client)
        raw_token = client.cookies[COOKIE]
        assert outsider.get(path).status_code == 401
        other = opt_in(outsider)
        old = event("info_close")
        newer = event("object_select", time=datetime.now(UTC) + timedelta(milliseconds=100))
        item = send(client, path, newer, old, newer)
        assert item.status_code == 200, item.text
        receipts = item.json()["receipts"]
        assert [row["status"] for row in receipts] == ["accepted", "accepted", "duplicate"]
        assert [row["ordinal"] for row in receipts] == [2, 3, 2]
        assert client.get(path).json()["info_open"]
        equivalent = {
            **old,
            "occurred_at": datetime.fromisoformat(old["occurred_at"])
            .astimezone(timezone(timedelta(hours=7)))
            .isoformat(),
        }
        assert send(client, path, equivalent).json()["receipts"][0]["status"] == "duplicate"
        assert send(client, path, event(), {**old, "event_type": "info_open"}).status_code == 409
        assert send(outsider, other, old).status_code == 409
        for change in (
            {"room_id": "P507"},
            {"object_id": "=SUM(1,2)"},
            {"payload": {}},
            {"occurred_at": "2026-11-19T00:00:00"},
            {"schema_version": True},
            {"event_type": "anything"},
            {"id": "not-a-uuid"},
            {"object_id": None},
            {"occurred_at": (datetime.now(UTC) + timedelta(days=1)).isoformat()},
        ):
            assert send(client, path, {**old, "id": str(uuid4()), **change}).status_code == 422
        assert send(client, path, *[event()] * 33).status_code == 422
        assert (
            client.post(path + "/events", json={"events": [], "pad": "x" * 8200}).status_code == 413
        )
        assert counts(database) == (2, 4)
        with Session(database.engine) as db:
            row = db.scalar(
                select(VisitorSession).where(VisitorSession.token_digest == digest(raw_token))
            )
            assert row is not None and row.token_digest != raw_token

        close_at = datetime.now(UTC) + timedelta(seconds=1)
        ending = event("session_end", time=close_at)
        assert send(client, path, ending).status_code == 200
        assert send(client, path, ending).json()["receipts"][0]["status"] == "duplicate"
        assert send(client, path, event(time=close_at + timedelta(seconds=1))).status_code == 409
        assert (
            send(client, path, event(time=close_at - timedelta(milliseconds=10))).status_code == 200
        )
        assert client.get(path).json()["ended"]
        assert client.delete(path).status_code == 200
        assert client.get(path, headers={"cookie": f"{COOKIE}={raw_token}"}).status_code == 401
        with Session(database.engine) as db, db.begin():
            db.execute(update(VisitorSession).values(token_expires_at=datetime.now(UTC)))
        assert outsider.get(other).status_code == 401
        assert outsider.delete(other).status_code == 401
        assert counts(database) == (1, 1)


def test_concurrent_same_session_and_event_collision_across_sessions(local_database):
    database, url = local_database
    with client_for(url) as client, client_for(url) as other:
        path = opt_in(client)
        other_path = opt_in(other)
        item = event()
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(send, client, path, item)
            second = executor.submit(send, client, path, item)
            receipts = [task.result().json()["receipts"][0] for task in (first, second)]
            assert {r["status"] for r in receipts} == {"accepted", "duplicate"}
            assert {r["ordinal"] for r in receipts} == {2}
            cross = event()
            first = executor.submit(send, client, path, cross)
            second = executor.submit(send, other, other_path, cross)
            assert sorted(task.result().status_code for task in (first, second)) == [200, 409]
        assert counts(database) == (2, 4)


def test_capacity_reserves_one_terminal_event(local_database):
    database, url = local_database
    with client_for(url) as client, client_for(url) as restarted:
        path = opt_in(client)
        at = datetime.now(UTC)
        interactions = [event(time=at) for _ in range(498)]
        for offset in range(0, len(interactions), 16):
            assert send(client, path, *interactions[offset:offset + 16]).status_code == 200
        assert counts(database) == (1, 499)
        last, excess = event(time=at), event(time=at)
        end = event("session_end", time=at + timedelta(milliseconds=10))
        assert send(client, path, last, excess).status_code == 413
        assert counts(database) == (1, 499)
        for item, ordinal in ((last, 500), (end, 501)):
            response = send(client, path, item)
            assert response.status_code == 200, response.text
            receipt = response.json()["receipts"][0]
            assert (receipt["status"], receipt["ordinal"]) == ("accepted", ordinal)

        restarted.cookies.set(COOKIE, client.cookies[COOKIE], domain="127.0.0.1", path=PATH)
        result = send(restarted, path, end, last)
        assert result.json()["remaining_events"] == 0
        assert [row["status"] for row in result.json()["receipts"]] == ["duplicate", "duplicate"]
        assert send(restarted, path, excess).status_code == 413
        assert send(restarted, path, event("session_end", time=at)).status_code == 409
        assert send(restarted, path, {**end, "occurred_at": at.isoformat()}).status_code == 409
        assert restarted.get(path).json()["ended"]

        with Session(database.engine) as db:
            session = db.scalar(select(VisitorSession))
            assert session.event_count == 501
            assert session.ended_at == datetime.fromisoformat(end["occurred_at"])
            rows = db.scalars(select(VisitorEvent).order_by(VisitorEvent.ordinal)).all()
            assert [row.ordinal for row in rows] == list(range(1, 502))
            assert [str(row.id) for row in rows[1:]] == [
                item["id"] for item in [*interactions, last, end]
            ]
            assert sum(row.event_type == "session_end" for row in rows) == 1
        csrf = login(client, login_password(database))
        json_out = client.post(REPORT + f"/export?format=json&{dates()}", headers=csrf)
        csv_out = client.post(REPORT + f"/export?format=csv&{dates()}", headers=csrf)
        assert json_out.status_code == csv_out.status_code == 200
        payload = json_out.json()
        assert payload["session_count"] == 1
        assert payload["sessions"][0]["event_count"] == payload["event_count"] == 501
        csv_rows = list(csv.DictReader(io.StringIO(csv_out.text)))
        assert [(row["event_id"], str(row["ordinal"])) for row in payload["events"]] == [
            (row["event_id"], row["ordinal"]) for row in csv_rows
        ] == [(str(row.id), str(row.ordinal)) for row in rows]


def test_capacity_terminal_batch_rollback_and_concurrent_end(local_database):
    database, url = local_database
    with client_for(url) as client, client_for(url) as other:
        path = opt_in(client)
        other.cookies.set(COOKIE, client.cookies[COOKIE], domain="127.0.0.1", path=PATH)
        at = datetime.now(UTC)
        interactions = [event(time=at) for _ in range(499)]
        for offset in range(0, len(interactions), 16):
            assert send(client, path, *interactions[offset:offset + 16]).status_code == 200
        assert counts(database) == (1, 500)
        ending, competing = (event("session_end", time=at) for _ in range(2))
        assert send(client, path, ending, event(time=at)).status_code == 413
        assert counts(database) == (1, 500)
        assert not client.get(path).json()["ended"]
        rendezvous = Barrier(2, timeout=10)

        def finish(browser, item):
            rendezvous.wait()
            return send(browser, path, item)

        with ThreadPoolExecutor(max_workers=2) as executor:
            tasks = [
                executor.submit(finish, client, ending),
                executor.submit(finish, other, competing),
            ]
            responses = [task.result() for task in tasks]
        assert sorted(result.status_code for result in responses) == [200, 409]
        index = next(i for i, result in enumerate(responses) if result.status_code == 200)
        winner = (ending, competing)[index]
        receipt = responses[index].json()["receipts"][0]
        assert (receipt["id"], receipt["ordinal"], receipt["status"]) == (
            winner["id"], 501, "accepted"
        )
        duplicate = send(other, path, winner).json()["receipts"][0]
        assert duplicate["status"] == "duplicate"
        assert (duplicate["id"], duplicate["ordinal"]) == (receipt["id"], receipt["ordinal"])
        assert datetime.fromisoformat(duplicate["received_at"]) == datetime.fromisoformat(
            receipt["received_at"]
        )
        assert counts(database) == (1, 501)


def test_migration_capacity_preserves_populated_0006_and_allows_legacy_close():
    with (
        isolated_catalog_database(migrate=False) as (database, url),
        isolated_catalog_database(migrate=False) as (restore, _),
    ):
        config = Config(str(API_ROOT / "alembic.ini"))
        old = "0006_visitor_start_attempts"
        tables = [VisitorSession.__table__, VisitorEvent.__table__, VisitorStartAttempt.__table__]
        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, old)
        with client_for(url) as client:
            path = opt_in(client)
            at = datetime.now(UTC)
            interactions = [event(time=at) for _ in range(499)]
            for offset in range(0, len(interactions), 16):
                assert send(client, path, *interactions[offset:offset + 16]).status_code == 200
            end = event("session_end", time=at)
            with database.engine.connect() as connection:
                backup = [
                    [dict(row) for row in connection.execute(select(table)).mappings()]
                    for table in tables
                ]
            with restore.engine.begin() as connection:
                config.attributes["connection"] = connection
                command.upgrade(config, old)
                for table, rows in zip(tables, backup, strict=True):
                    connection.execute(table.insert(), rows)

            with database.engine.connect() as connection:
                transaction = connection.begin()
                config.attributes["connection"] = connection
                command.upgrade(config, HEAD)
                assert "501" in inspect(connection).get_check_constraints("visitor_events")[0][
                    "sqltext"
                ]
                transaction.rollback()
                assert connection.scalar(text("SELECT version_num FROM alembic_version")) == old
                assert "501" not in inspect(connection).get_check_constraints("visitor_events")[0][
                    "sqltext"
                ]
            for target in (database, restore):
                with target.engine.begin() as connection:
                    config.attributes["connection"] = connection
                    command.upgrade(config, HEAD)
                    command.check(config)
                    for table, rows in zip(tables, backup, strict=True):
                        actual = connection.execute(select(table)).mappings()
                        assert sorted(map(repr, map(dict, actual))) == sorted(map(repr, rows))
                    with pytest.raises(IntegrityError), connection.begin_nested():
                        connection.execute(
                            VisitorEvent.__table__.insert().values(
                                {**backup[1][0], "id": uuid4(), "ordinal": 501}
                            )
                        )
                    with pytest.raises(RuntimeError, match="Forward-only"):
                        command.downgrade(config, old)
            assert send(client, path, end).json()["receipts"][0]["ordinal"] == 501
            assert counts(database) == (1, 501)
            assert counts(restore) == (1, 500)


def test_start_retry_rollback_rotation_and_consumed_intent_after_delete(
    local_database, monkeypatch
):
    database, url = local_database
    with client_for(url) as client:
        a_body = prepare_start(client)
        a_intent = client.cookies[INTENT_COOKIE]
        assert counts(database) == (0, 0)
        no_session_cookie = {"cookie": f"{INTENT_COOKIE}={a_intent}"}
        # Concurrent initial delivery with the same cookie before either response applies.
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    client.post, PATH + "/sessions", json=a_body, headers=no_session_cookie
                )
                for _ in range(2)
            ]
            starts = [future.result() for future in futures]
        assert [r.status_code for r in starts] == [201, 201]
        assert starts[0].json() == starts[1].json()
        path_a = f"{PATH}/sessions/{starts[0].json()['id']}"
        proof_a = client.cookies[COOKIE]
        assert counts(database) == (1, 1)

        b_body = prepare_start(client, path_a)
        assert client.post(PATH + "/sessions", json=b_body).status_code == 409
        item = event("object_select")
        assert send(client, path_a, item).status_code == 200
        closed = event("session_end", time=datetime.now(UTC) + timedelta(milliseconds=10))
        assert send(client, path_a, closed).status_code == 200
        assert send(client, path_a, closed).json()["receipts"][0]["status"] == "duplicate"

        # The new start must be atomic with proof revocation, even if commit fails.
        with monkeypatch.context() as fault:
            ids = iter([uuid4(), UUID(item["id"])])
            fault.setattr("app.modules.visitor.uuid4", lambda: next(ids))
            assert client.post(PATH + "/sessions", json=b_body).status_code == 409
        assert client.get(path_a).json()["ended"]
        assert counts(database) == (1, 3)

        b_intent = client.cookies[INTENT_COOKIE]
        before_transfer = {"cookie": f"{COOKIE}={proof_a}; {INTENT_COOKIE}={b_intent}"}
        response = client.post(PATH + "/sessions", json=b_body, headers=before_transfer)
        assert response.status_code == 201
        path_b = f"{PATH}/sessions/{response.json()['id']}"
        assert path_b != path_a
        assert response.json()["selected_id"] is None
        assert client.cookies[COOKIE] != proof_a
        replay = client.post(PATH + "/sessions", json=b_body, headers=before_transfer)
        assert replay.status_code == 201 and replay.json() == response.json()
        assert counts(database) == (2, 4)
        assert client.get(path_a, headers=before_transfer).status_code == 401
        assert client.delete(path_a, headers=before_transfer).status_code == 401
        assert (
            client.post(
                path_a + "/events",
                json={"events": [item]},
                headers=before_transfer,
            ).status_code
            == 401
        )
        assert (
            client.post(
                PATH + "/sessions",
                json=a_body,
                headers=no_session_cookie,
            ).status_code
            == 401
        )

        assert client.delete(path_b).status_code == 200
        assert (
            client.post(PATH + "/sessions", json=b_body, headers=before_transfer).status_code == 401
        )
        assert counts(database) == (1, 3)


def test_competing_new_intents_can_only_rotate_one_ended_session(local_database):
    database, url = local_database
    with client_for(url) as client, client_for(url) as first, client_for(url) as second:
        path = opt_in(client)
        assert send(client, path, event("session_end")).status_code == 200
        proof = client.cookies[COOKIE]
        bodies = [prepare_start(tab, path) for tab in (first, second)]
        headers = [
            {"cookie": f"{COOKIE}={proof}; {INTENT_COOKIE}={tab.cookies[INTENT_COOKIE]}"}
            for tab in (first, second)
        ]
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = [
                executor.submit(tab.post, PATH + "/sessions", json=body, headers=cookie)
                for tab, body, cookie in zip((first, second), bodies, headers, strict=True)
            ]
            assert sorted(future.result().status_code for future in outcomes) == [201, 401]
        with Session(database.engine) as db:
            attempts = db.scalar(select(func.count()).select_from(VisitorStartAttempt))
            assert attempts == 3
        assert counts(database) == (2, 3)


def test_restart_database_outage_retains_id_and_commit_receipt(local_database):
    database, url = local_database
    with client_for(url) as client:
        path = opt_in(client)
        token = client.cookies[COOKIE]
    item = event("object_select")
    name = database.engine.url.database

    def fault(mode):
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("database_fault.py")), mode, name],
            env={**os.environ, "DATABASE_URL": url.get_secret_value()},
            check=True,
            timeout=15,
        )

    with client_for(url) as restarted:
        restarted.cookies.set(COOKIE, token, domain="127.0.0.1", path=PATH)
        assert restarted.get(path).status_code == 200
        try:
            fault("block")
            assert send(restarted, path, item).status_code == 503
        finally:
            fault("restore")
        assert counts(database) == (1, 1)
        assert send(restarted, path, item).json()["receipts"][0]["status"] == "accepted"
        assert send(restarted, path, item).json()["receipts"][0]["status"] == "duplicate"
        assert restarted.get(path).json()["selected_id"] == "demo-object-cube"


def test_oracle_reconciles_50_sessions_1000_ids_database_report_and_exports(
    local_database, monkeypatch
):
    database, url = local_database
    password = login_password(database)
    # All IDs and content are prepared before any session start/network write.
    oracle = dict(expected_visits(datetime.now(UTC)))
    expected = {}
    bindings = {}
    replies = {"accepted": 0, "duplicate": 0, "conflict": 0}
    with client_for(url) as client:
        assert client.get(REPORT + "?" + dates()).status_code == 401
        csrf = login(client, password)
        assert client.post(REPORT + "/export?" + dates() + "&format=json").status_code == 403
        assert (
            client.post(
                REPORT + "/export?" + dates() + "&format=json",
                headers={
                    **csrf,
                    "origin": "http://localhost:5173",
                },
            ).status_code
            == 403
        )
        assert client.get(REPORT + "?start=2020-01-01&until=2026-12-31").status_code == 422
        for index, inputs in oracle.items():
            if COOKIE in client.cookies:
                client.cookies.delete(COOKIE, domain="127.0.0.1", path=PATH)
            path = opt_in(client)
            session_id = path.rsplit("/", 1)[1]
            bindings[index] = session_id
            observed = datetime.now(UTC)
            for sequence, item in enumerate(inputs):
                item["occurred_at"] = (observed + timedelta(milliseconds=sequence)).isoformat()
            expected.update({e["id"]: (session_id, e) for e in inputs})
            for events, want in ((inputs[::-1], "accepted"), (inputs, "duplicate")):
                result = send(client, path, *events)
                assert result.status_code == 200, result.text
                assert {r["status"] for r in result.json()["receipts"]} == {want}
                replies[want] += len(events)
            changed = {**inputs[0], "occurred_at": inputs[1]["occurred_at"]}
            assert send(client, path, changed).status_code == 409
            replies["conflict"] += 1

        report = client.get(REPORT + "?" + dates() + "&limit=25").json()
        second = client.get(REPORT + "?" + dates() + "&limit=25&page=2").json()
        assert (report["sessions"], report["events"], report["next_page"]) == (50, 1050, 2)
        assert second["next_page"] is None
        assert {s["session_id"] for s in report["rows"] + second["rows"]} == set(bindings.values())
        assert all(s["event_count"] == 21 for s in report["rows"] + second["rows"])
        assert client.get(REPORT + "?start=2000-01-01&until=2000-01-02").json()["events"] == 0

        json_out = client.post(REPORT + "/export?" + dates() + "&format=json", headers=csrf)
        csv_out = client.post(REPORT + "/export?" + dates() + "&format=csv", headers=csrf)
        assert json_out.status_code == csv_out.status_code == 200
        assert json_out.headers["cache-control"] == "no-store"
        assert csv_out.headers["content-type"].startswith("text/csv")
        assert b"\r\n" in csv_out.content and b"\n" not in csv_out.content.replace(b"\r\n", b"")
        exported = json_out.json()
        csv_rows = list(csv.DictReader(io.StringIO(csv_out.text, newline="")))
        assert all(row["scope"] == "synthetic_local" for row in csv_rows)
        assert exported["session_count"] == 50 and exported["event_count"] == 1050
        with monkeypatch.context() as cap:
            cap.setattr("app.modules.visitor_reports.MAX_SESSIONS", 49)
            assert (
                client.post(REPORT + "/export?" + dates() + "&format=csv", headers=csrf).status_code
                == 413
            )
            cap.setattr("app.modules.visitor_reports.MAX_SESSIONS", 200)
            cap.setattr("app.modules.visitor_reports.MAX_EVENTS", 1049)
            assert (
                client.post(
                    REPORT + "/export?" + dates() + "&format=json", headers=csrf
                ).status_code
                == 413
            )
        for field in ("token_digest", "token_expires_at", "source_note", "qa_operator"):
            assert field not in json_out.text and field not in csv_out.text

    with Session(database.engine) as db:
        db_rows = [
            {
                "event_id": str(e.id),
                "session_id": str(e.session_id),
                "event_type": e.event_type,
                "room_id": e.room_id,
                "object_id": e.object_id,
                "occurred_at": e.occurred_at.isoformat(),
                "ordinal": e.ordinal,
                "received_at": e.received_at.isoformat(),
            }
            for e in db.scalars(
                select(VisitorEvent).order_by(VisitorEvent.session_id, VisitorEvent.ordinal)
            )
        ]
        postgres = db.scalar(text("SHOW server_version"))
    assert len(set(bindings.values())) == 50

    def end_to_end(rows):
        seen = {}
        starts = []
        duplicates = conflicts = 0
        for row in rows:
            if row["event_type"] == "session_start":
                starts.append(row["session_id"])
                continue
            identifier = row["event_id"]
            duplicates += identifier in seen
            seen[identifier] = row
            if identifier in expected:
                scope, item = expected[identifier]
                conflicts += (
                    scope != row["session_id"]
                    or any(row[key] != item[key] for key in ("event_type", "room_id"))
                    or (row["object_id"] or None) != item["object_id"]
                    or datetime.fromisoformat(row["occurred_at"])
                    != datetime.fromisoformat(item["occurred_at"])
                )
        assert sorted(starts) == sorted(bindings.values())
        return {
            "missing": len(expected.keys() - seen.keys()),
            "extra": len(seen.keys() - expected.keys()),
            "duplicates": duplicates,
            "conflicts": conflicts,
        }

    comparison = {
        "database": end_to_end(db_rows),
        "json": end_to_end(exported["events"]),
        "csv": end_to_end(csv_rows),
    }
    assert comparison == dict.fromkeys(
        comparison, dict(missing=0, extra=0, duplicates=0, conflicts=0)
    )
    assert replies == {"accepted": 1000, "duplicate": 1000, "conflict": 50}
    assert (
        {r["event_id"] for r in db_rows}
        == {r["event_id"] for r in csv_rows}
        == {r["event_id"] for r in exported["events"]}
    )
    evidence = Path(os.environ.get("M4_ORACLE_OUT", ROOT / ".local/m4-visitor-evidence"))
    evidence.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": "PASS",
        "code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "dirty_tracked_files": bool(
            subprocess.check_output(["git", "status", "--porcelain", "-uno"], cwd=ROOT)
        ),
        "postgresql": postgres,
        "python": platform.python_version(),
        "platform": platform.system(),
        "sessions": 50,
        "expected_client_events": 1000,
        "server_start_events": 50,
        "receipts": replies,
        "reconciliation": comparison,
    }
    for filename, data in {
        "oracle.json": {"sessions": oracle, "bindings": bindings},
        "database.json": db_rows,
        "export.json": exported,
        "reconciliation.json": summary,
    }.items():
        (evidence / filename).write_text(json.dumps(data, indent=2), encoding="utf-8")
    (evidence / "export.csv").write_bytes(csv_out.content)


def test_chrome_fixture_uses_real_api_and_postgres(local_database):
    database, url = local_database
    password = login_password(database)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = subprocess.run(
        ["node", "apps/web/tests/visitor-browser.mjs"],
        cwd=ROOT,
        env={
            **os.environ,
            "DATABASE_URL": url.get_secret_value(),
            "API_PYTHON": sys.executable,
            "M4_TEST_OPERATOR_PASSWORD": password,
            "M4_TEST_SHA": sha,
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-4000:]
    assert counts(database) == (3, 143)
    out = Path(os.environ.get("M4_BROWSER_OUT", ROOT / ".local/m4-visitor-browser"))
    exported = json.loads((out / "rotation-export.json").read_text(encoding="utf-8"))
    with (out / "rotation-export.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))

    legacy = json.loads((out / "legacy-128-browser.json").read_text(encoding="utf-8"))
    assert legacy["code_sha"] == sha
    legacy_export = json.loads((out / "legacy-export.json").read_text(encoding="utf-8"))
    with (out / "legacy-export.csv").open(encoding="utf-8", newline="") as stream:
        legacy_csv = list(csv.DictReader(stream))

    with Session(database.engine) as db:
        sessions = db.scalars(select(VisitorSession).order_by(VisitorSession.started_at)).all()
        events = db.scalars(
            select(VisitorEvent).order_by(VisitorEvent.session_id, VisitorEvent.ordinal)
        ).all()
        event_rows = [
            dict(
                session_id=str(e.session_id),
                event_id=str(e.id),
                ordinal=e.ordinal,
                event_type=e.event_type,
                room_id=e.room_id,
                object_id=e.object_id,
                occurred_at=e.occurred_at.isoformat(),
                received_at=e.received_at.isoformat(),
            )
            for e in events
        ]
        legacy_session = next(s for s in sessions if str(s.id) == legacy["session_id"])
        assert legacy_session.ended_at is not None
        assert legacy_session.event_count == 131  # Start, bootstrap room_enter, 128 legacy, end.
        legacy_rows = [row for row in event_rows if row["session_id"] == legacy["session_id"]]
        sessions = [s for s in sessions if s.id != legacy_session.id]
        event_rows = [row for row in event_rows if row["session_id"] != legacy["session_id"]]
        assert all(s.ended_at is not None for s in sessions)
        assert sessions[0].token_expires_at < sessions[1].started_at
        assert sessions[0].token_digest != sessions[1].token_digest
        assert [s.event_count for s in sessions] == [7, 5]
        for session, expected_types in zip(
            sessions,
            (
                [
                    "session_start",
                    "room_enter",
                    "object_select",
                    "object_select",
                    "info_close",
                    "info_open",
                    "session_end",
                ],
                ["session_start", "room_enter", "object_select", "info_close", "session_end"],
            ),
            strict=True,
        ):
            rows = [row for row in event_rows if row["session_id"] == str(session.id)]
            assert [row["ordinal"] for row in rows] == list(range(1, session.event_count + 1))
            assert [row["event_type"] for row in rows] == expected_types
        assert [row["session_id"] for row in exported["sessions"]] == [str(s.id) for s in sessions]

    def canonical(row):
        return (
            row["session_id"],
            row["event_id"],
            int(row["ordinal"]),
            row["event_type"],
            row["room_id"],
            row["object_id"] or None,
            datetime.fromisoformat(row["occurred_at"]),
            datetime.fromisoformat(row["received_at"]),
        )

    expected = {canonical(row) for row in event_rows}
    assert len({row["event_id"] for row in event_rows}) == 12
    for export in (csv_rows, exported["events"]):
        assert len(export) == len(expected) and {canonical(row) for row in export} == expected
    (out / "rotation-database.json").write_text(
        json.dumps(
            dict(
                status="PASS",
                code_sha=sha,
                sessions=2,
                counts=[7, 5],
                db_csv_json_ids_match=True,
                events=event_rows,
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    queued = legacy["persisted_after_offline_reload"]["queue"]
    assert "remaining_events" not in legacy["original"]["view"]
    assert legacy["original"]["queue"] == queued[:-1]
    assert len(queued) == 129
    assert [row["ordinal"] for row in legacy_rows] == list(range(1, 132))
    assert [row["event_type"] for row in legacy_rows[:2]] == ["session_start", "room_enter"]
    assert [row["event_type"] for row in legacy_rows].count("session_end") == 1
    for row, item in zip(legacy_rows[2:], queued, strict=True):
        assert row["event_id"] == item["id"]
        assert row["event_type"] == item["event_type"]
        assert row["room_id"] == item["room_id"]
        assert row["object_id"] == item["object_id"]
        assert datetime.fromisoformat(row["occurred_at"]) == datetime.fromisoformat(
            item["occurred_at"]
        )
    terminal_receipts = [
        receipt
        for batch in legacy["receipts"]
        for receipt in batch
        if receipt["id"] == queued[-1]["id"]
    ]
    assert [(row["status"], row["ordinal"]) for row in terminal_receipts] == [
        ("accepted", 131), ("duplicate", 131),
    ]
    received_at = datetime.fromisoformat(legacy_rows[-1]["received_at"])
    receipt_times = {datetime.fromisoformat(row["received_at"]) for row in terminal_receipts}
    assert receipt_times == {received_at}
    expected = {canonical(row) for row in event_rows + legacy_rows}
    assert len(expected) == 143
    for export in (legacy_csv, legacy_export["events"]):
        assert len(export) == len(expected) and {canonical(row) for row in export} == expected
    assert [row["event_count"] for row in legacy_export["sessions"]] == [7, 5, 131]
    (out / "legacy-128-database.json").write_text(
        json.dumps(
            dict(
                status="PASS",
                code_sha=sha,
                sessions=3,
                counts=[7, 5, 131],
                db_csv_json_match=True,
                events=legacy_rows,
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
