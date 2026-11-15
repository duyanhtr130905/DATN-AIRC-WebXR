import json
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import pytest
from process_cleanup import terminate_owned
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from test_catalog_postgres import isolated_catalog_database
from test_state_postgres import live_server as live_server

from app.database.models import Room
from app.database.state_models import CurrentState, Outbox, StateHistory
from app.modules.catalog.vertical_seed import ROOM_IDS, seed_vertical_slice

pytestmark = pytest.mark.postgres


@pytest.fixture
def state_database():
    # Override only this module's M1-B fixture: browser must first observe an empty DB.
    with isolated_catalog_database() as result:
        yield result


def test_fixture_idempotency_and_actual_browser_vertical_slice(live_server):
    database, url, application, server, port = live_server
    root = Path(__file__).resolve().parents[3]
    request = root / ".local/m1-c-stop-api.request"
    request.unlink(missing_ok=True)  # This runner's own ignored sentinel only.
    empty_id = uuid4()
    empty_request = root / ".local/m1-c-seed-empty.request"
    empty_request.unlink(missing_ok=True)
    empty_seeded = False
    process = subprocess.Popen(
        ["node", str(root / "apps/web/tests/vertical-slice.mjs")],
        cwd=root,
        env={
            **os.environ,
            "API_PORT": str(port),
            "API_PYTHON": sys.executable,
            "DATABASE_URL": url.get_secret_value(),
            "SYNTHETIC_ROOM_ID": str(ROOM_IDS[0]),
            "SECOND_ROOM_ID": str(ROOM_IDS[1]),
            "EMPTY_ROOM_ID": str(empty_id),
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name != "nt",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    deadline = time.monotonic() + 180
    try:
        while True:
            if request.exists():
                server.should_exit = True
            if empty_request.exists() and not empty_seeded:
                with Session(database.engine) as session, session.begin():
                    session.add(
                        Room(
                            id=empty_id,
                            code="DEMO-EMPTY-TEST",
                            name="Synthetic empty test room",
                            source_kind="synthetic",
                            metadata_json={"label": "SYNTHETIC — NOT AIRC REAL DATA"},
                        )
                    )
                empty_seeded = True
            try:
                stdout, stderr = process.communicate(timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                if time.monotonic() > deadline:
                    terminate_owned(process)
                    pytest.fail("Browser E2E timed out")
    finally:
        try:
            terminate_owned(process)
        finally:
            # Parent restores its own disposable DB even if Node was killed mid-fault.
            restored = subprocess.run(
                [
                    sys.executable,
                    str(root / "apps/api/tests/database_fault.py"),
                    "restore",
                    make_url(url.get_secret_value()).database,
                ],
                env={**os.environ, "DATABASE_URL": url.get_secret_value()},
                capture_output=True,
                timeout=10,
            )
            assert restored.returncode == 0, "Parent must restore disposable database connectivity"
    assert process.returncode == 0, stdout[-4000:] + stderr[-4000:]
    report = json.loads((root / ".local/m1-c-browser/report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    with Session(database.engine) as session, session.begin():
        seed_vertical_slice(session)  # Rerun must preserve explicit updates, not reset them.
        before = session.scalar(select(func.count()).select_from(StateHistory))
        seed_vertical_slice(session)
        assert session.scalar(select(func.max(CurrentState.version))) == 22
        assert session.scalar(select(func.count()).select_from(CurrentState)) == 44
        assert session.scalar(select(func.count()).select_from(StateHistory)) == before == 65
        assert session.scalar(select(func.count()).select_from(Outbox)) == 65
    assert not application.state.broker.subscribers
