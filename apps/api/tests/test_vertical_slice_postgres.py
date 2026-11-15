import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_state_postgres import live_server as live_server
from test_state_postgres import state_database as state_database

from app.database.state_models import CurrentState, Outbox, StateHistory
from app.modules.catalog.vertical_seed import ROOM_IDS, seed_vertical_slice

pytestmark = pytest.mark.postgres


def test_fixture_idempotency_and_actual_browser_vertical_slice(live_server):
    database, url, _, _, port = live_server
    with Session(database.engine) as session, session.begin():
        seed_vertical_slice(session)
    with Session(database.engine) as session, session.begin():
        seed_vertical_slice(session)
        assert session.scalar(select(func.count()).select_from(CurrentState)) == 44
        assert session.scalar(select(func.count()).select_from(StateHistory)) == 44
        assert session.scalar(select(func.count()).select_from(Outbox)) == 44
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
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
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    report = json.loads((root / ".local/m1-c-browser/report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    with Session(database.engine) as session, session.begin():
        seed_vertical_slice(session)  # Rerun must preserve explicit updates, not reset them.
        assert session.scalar(select(func.max(CurrentState.version))) == 2
        assert session.scalar(select(func.count()).select_from(StateHistory)) == 45
