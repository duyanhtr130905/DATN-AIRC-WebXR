import json
import os
import secrets
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect
from test_catalog_postgres import isolated_catalog_database
from test_state_postgres import live_server as live_server

from app.core.config import Settings
from app.database.admin_models import AdminAccount, AdminAudit, AdminSession
from app.database.models import Object, Room
from app.database.state_models import CurrentState, Outbox, StateHistory
from app.main import create_app
from app.modules.admin_auth import COOKIE, hash_password
from app.modules.p507 import ROOM_ID, ROOT, evidence, object_id, validate_mapping
from app.modules.state.service import StateConflict, change_state

pytestmark = pytest.mark.postgres
ORIGIN = "http://127.0.0.1:5173"
BASE = "/api/v1/admin"
PRIVATE = BASE + "/p507"


@pytest.fixture
def state_database():
    with isolated_catalog_database() as result:
        yield result


@pytest.fixture
def live_options():
    return {"admin_enabled": True}


def seed(database, *, active=True):
    password = secrets.token_urlsafe(24)
    with Session(database.engine) as db, db.begin():
        validate_mapping(db, seed=True)
        db.add(
            AdminAccount(
                username="qa_operator", password_hash=hash_password(password), active=active
            )
        )
    return password


def test_auth_catalog_state_and_public_isolation(state_database):
    database, url = state_database
    password = seed(database)
    _, ids = evidence()
    target = str(object_id(ids[0]))
    with Session(database.engine) as db, db.begin():
        room = Room(code="OTHER-ADMIN-TEST", name="Other test room", source_kind="synthetic")
        db.add(room)
        db.flush()
        item = Object(room_id=room.id, name="Wrong scope", type="fixture", source_kind="unknown")
        db.add(item)
        db.flush()
        other_id = str(item.id)
    with TestClient(
        create_app(Settings(_env_file=None, database_url=url, admin_enabled=True)),
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 55000),
        headers={"origin": ORIGIN},
    ) as client:
        assert client.get(PRIVATE).status_code == 401
        with pytest.raises(WebSocketDisconnect) as denied:
            with client.websocket_connect("/ws/v1/admin/p507"):
                pass
        assert getattr(denied.value, "code", None) == 1008
        assert (
            client.post(
                BASE + "/login", json={"username": "qa_operator", "password": "wrong"}
            ).status_code
            == 401
        )
        response = client.post(
            BASE + "/login", json={"username": "qa_operator", "password": password}
        )
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "SameSite=strict" in response.headers["set-cookie"]
        csrf = {"X-Admin-CSRF": response.json()["csrf"]}
        cookie = client.cookies[COOKIE]
        assert (
            client.get(PRIVATE, headers={"cookie": f"{COOKIE}={cookie[:-1]}!"}).status_code == 401
        )
        data = dict(
            name="Private fixture",
            kind="test",
            group_name="test",
            modeling="NOT_MODELED",
            archived=False,
            expected_version=0,
            description="PRIVATE DESCRIPTION",
            location="",
        )
        assert client.post(PRIVATE + "/objects", json=data).status_code == 403
        assert (
            client.post(
                PRIVATE + "/objects", json=data, headers={**csrf, "origin": "http://localhost:5173"}
            ).status_code
            == 403
        )
        created = client.post(PRIVATE + "/objects", json=data, headers=csrf)
        assert created.status_code == 201
        object_key = created.json()["id"]
        assert client.get(f"/api/v1/objects/{object_key}").status_code == 404
        assert (
            client.put(
                f"{PRIVATE}/objects/{target}",
                json={**data, "modeling": "MODELED", "external_reference": "fake"},
                headers=csrf,
            ).status_code
            == 422
        )
        assert (
            client.put(
                f"{PRIVATE}/objects/{target}", json={**data, "modeling": "MODELED"}, headers=csrf
            ).status_code
            == 200
        )
        assert "PRIVATE DESCRIPTION" not in client.get(f"/api/v1/objects/{target}").text
        value = dict(
            target_id=target,
            state_type="equipment_status",
            expected_version=0,
            observed_at=datetime.now(UTC).isoformat(),
            value={"status": "maintenance"},
        )
        assert client.put(PRIVATE + "/state", json=value, headers=csrf).status_code == 200
        assert client.put(PRIVATE + "/state", json=value, headers=csrf).status_code == 409
        assert (
            client.put(
                PRIVATE + "/state", json={**value, "target_id": str(ROOM_ID)}, headers=csrf
            ).status_code
            == 404
        )
        assert client.get(f"/api/v1/objects/{target}/states").json()["data"] == []
        assert (
            client.put(
                PRIVATE + "/state", json={**value, "target_id": other_id}, headers=csrf
            ).status_code
            == 404
        )
        assert (
            client.put(
                f"{PRIVATE}/objects/{object_key}",
                json={**data, "archived": True, "expected_version": 1},
                headers=csrf,
            ).json()["archived"]
            is True
        )
        assert (
            client.put(
                PRIVATE + "/state", json={**value, "target_id": object_key}, headers=csrf
            ).status_code
            == 409
        )

        legacy = client.get(PRIVATE).json()
        assert legacy["states"][0]["operator"] == "qa_operator"
        assert legacy["states"][0]["provenance"] == "UNKNOWN"
        history_path = PRIVATE + f"/state/{legacy['states'][0]['id']}/history"
        history = client.get(history_path)
        assert history.headers["cache-control"] == "no-store"
        assert history.json() == {"data": legacy["states"], "next_after_version": None}
        assert client.get(history_path + "?after_version=1").json()["data"] == []
        assert (
            next(row for row in legacy["objects"] if row["id"] == object_key)["provenance"]
            == "UNKNOWN"
        )
        assert next(row for row in legacy["objects"] if row["logical_id"] and row["id"] != target)[
            "provenance"
        ] == ("SYNTHETIC_TEST / NOT_AIRC")
        observed_at = (datetime.now(UTC) + timedelta(minutes=1)).isoformat()
        for source in ("real_verified", "VERIFIED", "INVALID"):
            assert (
                client.put(
                    PRIVATE + "/state", json={**value, "provenance": source}, headers=csrf
                ).status_code
                == 422
            )
        owner = {
            **data,
            "expected_version": 1,
            "modeling": "MODELED",
            "provenance": "OWNER_ENTERED",
        }
        assert (
            client.put(f"{PRIVATE}/objects/{target}", json=owner, headers=csrf).status_code == 422
        )
        entered = client.put(
            f"{PRIVATE}/objects/{target}",
            json={**owner, "observed_at": observed_at, "source_note": "Protected observation note"},
            headers=csrf,
        )
        assert entered.status_code == 200
        assert entered.json()["provenance"] == "OWNER_ENTERED / PENDING_VERIFICATION"
        updated = client.put(
            f"{PRIVATE}/objects/{target}",
            json={**data, "expected_version": 2, "modeling": "MODELED"},
            headers=csrf,
        ).json()
        assert updated["version"] == 3
        assert updated["provenance"] == entered.json()["provenance"]
        assert updated["source_note"] == "Protected observation note"
        assert updated["operator"] == "qa_operator"
        assert updated["committed_at"]
        assert "Protected observation note" not in client.get(f"/api/v1/objects/{target}").text
        assert client.post(BASE + "/logout", headers=csrf).status_code == 200
        assert client.get(PRIVATE, headers={"cookie": f"{COOKIE}={cookie}"}).status_code == 401
        assert client.get(history_path).status_code == 401

        # Reuse the revoked cookie to try a write directly, outside the UI.
        assert (
            client.put(
                PRIVATE + "/state", json=value, headers={**csrf, "cookie": f"{COOKIE}={cookie}"}
            ).status_code
            == 401
        )

        session = client.post(
            BASE + "/login", json={"username": "qa_operator", "password": password}
        )
        assert session.status_code == 200
        first = client.cookies[COOKIE]
        rotated = client.post(
            BASE + "/login", json={"username": "qa_operator", "password": password}
        )
        assert rotated.status_code == 200
        assert client.get(PRIVATE, headers={"cookie": f"{COOKIE}={first}"}).status_code == 401
        with Session(database.engine) as db, db.begin():
            db.execute(
                update(AdminSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
            )
        assert client.get(PRIVATE).status_code == 401

    with Session(database.engine) as db:
        for table in (CurrentState, StateHistory):
            assert db.scalar(select(func.count()).select_from(table)) == 1
        assert db.scalar(select(func.count()).select_from(Outbox)) == 6
        assert (
            db.scalar(
                select(func.count())
                .select_from(AdminAudit)
                .where(
                    AdminAudit.operation == "equipment_status",
                    AdminAudit.revision == 1,
                )
            )
            == 1
        )
        assert set(db.scalars(select(Outbox.audience))) == {"admin"}


def test_inactive_account_and_throttle(state_database):
    database, url = state_database
    password = seed(database, active=False)
    with TestClient(
        create_app(Settings(_env_file=None, database_url=url, admin_enabled=True)),
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 55000),
    ) as client:
        for _ in range(5):
            assert (
                client.post(
                    BASE + "/login",
                    headers={"origin": ORIGIN},
                    json={"username": "qa_operator", "password": password},
                ).status_code
                == 401
            )
        assert (
            client.post(
                BASE + "/login",
                headers={"origin": ORIGIN},
                json={"username": "qa_operator", "password": password},
            ).status_code
            == 429
        )


def test_admin_real_chrome(live_server):
    database, _, _, _, port = live_server
    password = seed(database)
    process = subprocess.run(
        ["node", str(ROOT / "apps/web/tests/admin-browser.mjs")],
        cwd=ROOT,
        text=True,
        env={**os.environ, "API_PORT": str(port), "M3_TEST_LOGIN": password},
        capture_output=True,
        timeout=150,
        check=False,
    )
    assert process.returncode == 0, process.stdout[-1600:] + process.stderr[-2300:]
    report_path = ROOT / ".local/m3-admin-browser/report.json"
    report = json.loads(report_path.read_bytes())
    assert report["status"] == "PASS"
    with Session(database.engine) as db:
        for table in (CurrentState, StateHistory):
            assert db.scalar(select(func.count()).select_from(table)) == 3
        query = (
            select(Outbox)
            .where(
                Outbox.room_id == ROOM_ID,
                Outbox.audience == "admin",
                Outbox.payload["state_id"].astext.is_not(None),
            )
            .order_by(Outbox.sequence)
        )
        # The cursor fallback may deliver a hint before the dispatcher records its receipt.
        deadline = time.monotonic() + 5
        while True:
            rows = db.scalars(query).all()
            if len(rows) == 3 and all(row.published_at is not None for row in rows):
                break
            assert time.monotonic() < deadline, "Missing Admin outbox publication record"
            db.expire_all()
            time.sleep(0.05)
        assert len(report["samples"]) == len(rows)
        for sample, row in zip(report["samples"], rows, strict=True):
            assert sample["sequence"] == row.sequence
            assert sample["state_id"] == row.payload["state_id"]
            assert sample["version"] == row.payload["version"]
            assert row.published_at >= row.committed_at
            sample["message_id"] = str(row.message_id)
            sample["outbox_published_at"] = row.published_at.isoformat()
        report["postgres_version"] = db.scalar(select(func.version()))
    report["clock_alignment"] = "UNMEASURED"
    report["evidence_scope"] = "SYNTHETIC_TEST"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def test_private_state_concurrency_and_transaction_rollback(state_database):
    database, _ = state_database
    seed(database)
    _, ids = evidence()
    target = object_id(ids[0])

    def write(db, version, timestamp):
        return change_state(
            db,
            room_id=ROOM_ID,
            target_kind="object",
            target_id=target,
            state_type="equipment_status",
            value={"status": "offline"},
            expected_version=version,
            source_observed_at=timestamp,
            audience="admin",
        )

    def race(offset):
        try:
            with Session(database.engine) as db, db.begin():
                write(db, 0, datetime(2026, 11, 19, tzinfo=UTC) + timedelta(seconds=offset))
        except StateConflict:
            return "conflict"
        return "success"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(race, [1, 2])) == ["conflict", "success"]
    with pytest.raises(RuntimeError), Session(database.engine) as db, db.begin():
        write(db, 1, datetime(2026, 11, 20, tzinfo=UTC))
        account_id = db.scalar(select(AdminAccount.id))
        db.add(
            AdminAudit(
                account_id=account_id,
                target_id=target,
                operation="equipment_status",
                outcome="success",
                previous_revision=1,
                revision=2,
            )
        )
        db.flush()
        raise RuntimeError("Synthetic rollback")
    with Session(database.engine) as db:
        for table in (CurrentState, StateHistory, Outbox):
            assert db.scalar(select(func.count()).select_from(table)) == 1
        assert db.scalar(select(func.count()).select_from(AdminAudit)) == 0
        assert db.scalar(select(Outbox.payload)).keys() == {"state_id", "version"}


def test_https_requires_explicit_origin_and_secure_cookie(state_database):
    database, url = state_database
    password = seed(database)
    login = {"username": "qa_operator", "password": password}
    config = Settings(
        _env_file=None, database_url=url, admin_enabled=True, admin_origin="https://127.0.0.1:5173"
    )
    with TestClient(
        create_app(config), base_url="https://127.0.0.1", client=("127.0.0.1", 55000)
    ) as client:
        assert (
            client.post(BASE + "/login", headers={"origin": ORIGIN}, json=login).status_code == 403
        )
        response = client.post(BASE + "/login", headers={"origin": config.admin_origin}, json=login)
        assert response.status_code == 200
        assert "Secure" in response.headers["set-cookie"]
        assert client.get(PRIVATE).status_code == 200
    with TestClient(
        create_app(config), base_url="https://127.0.0.1", client=("192.0.2.1", 55000)
    ) as client:
        assert (
            client.post(
                BASE + "/login", headers={"origin": config.admin_origin}, json=login
            ).status_code
            == 403
        )
