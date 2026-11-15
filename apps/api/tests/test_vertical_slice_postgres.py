import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_catalog_postgres import isolated_catalog_database
from test_state_postgres import live_server as live_server

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
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 180
    try:
        while True:
            if request.exists():
                server.should_exit = True
            try:
                stdout, stderr = process.communicate(timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                if time.monotonic() > deadline:
                    process.kill()
                    stdout, stderr = process.communicate(timeout=5)
                    pytest.fail("Browser E2E timed out")
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
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
