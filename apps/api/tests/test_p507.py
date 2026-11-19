import json
import os
import subprocess
import sys

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_catalog_postgres import isolated_catalog_database
from test_state_postgres import live_server as live_server

from app.database.models import Object
from app.database.state_models import CurrentState, Outbox, StateHistory
from app.modules.p507 import (
    REVISION,
    ROOM_ID,
    ROOT,
    evidence,
    ingest,
    parse_observation,
    validate_mapping,
)
from app.modules.state.service import StateConflict


@pytest.fixture
def state_database():
    with isolated_catalog_database() as result:
        yield result


@pytest.mark.postgres
def test_p507_transactions_and_conflicts(state_database):
    database, _ = state_database
    _, ids = evidence()

    def observation(version, instant, status="available", logical=ids[-1]):
        return parse_observation(
            json.dumps(
                {
                    "state_type": "equipment_status",
                    "logical_id": logical,
                    "observed_at": instant,
                    "expected_version": version,
                    "value": {"status": status},
                }
            ).encode()
        )

    with Session(database.engine) as session, session.begin():
        with pytest.raises(ValueError):
            validate_mapping(session)
        assert len(validate_mapping(session, seed=True)) == 121
        assert len(validate_mapping(session, seed=True)) == 121
        initial = observation(0, "2026-01-01T00:00:00Z")
        with pytest.raises(PermissionError):
            ingest(session, initial, authorization=None)
        assert ingest(session, initial, authorization=REVISION)["sequence"] == 1
        assert ingest(session, initial, authorization=REVISION)["replayed"]
        with pytest.raises(StateConflict):
            ingest(session, observation(1, "2025-01-01T00:00:00Z"), authorization=REVISION)
        with pytest.raises(StateConflict):
            ingest(session, observation(0, "2026-01-02T00:00:00Z"), authorization=REVISION)
        with pytest.raises(ValueError):
            ingest(
                session,
                observation(0, "2026-01-02T00:00:00Z", logical="P507-CHAIR-C-09"),
                authorization=REVISION,
            )
    with pytest.raises(RuntimeError), Session(database.engine) as session, session.begin():
        ingest(session, observation(1, "2026-01-02T00:00:00Z", "offline"), authorization=REVISION)
        raise RuntimeError("rollback after ingest")
    with Session(database.engine) as session, session.begin():
        for model in (CurrentState, StateHistory, Outbox):
            assert session.scalar(select(func.count()).select_from(model)) == 1
        session.add(
            Object(
                room_id=ROOM_ID,
                name="Conflict",
                type="fixture",
                source_kind="synthetic",
                external_reference=ids[-1],
            )
        )
        session.flush()
        with pytest.raises(ValueError, match="mapping conflict"):
            validate_mapping(session)


def test_committed_browser_mapping_is_exact():
    lock, ids = evidence()
    path = ROOT / "apps/web/src/app/p507-mapping.json"
    mapping = json.loads(path.read_bytes())
    from app.modules.p507 import object_id

    assert mapping == {
        "room_id": str(ROOM_ID),
        "revision": REVISION,
        "evidence_ref": f"{REVISION}:sha256:{lock['files']['asset-manifest.json']['sha256']}",
        "objects": {key: str(object_id(key)) for key in ids},
    }


@pytest.mark.parametrize(
    "fields",
    [
        {"source_kind": "real_verified"},
        {"observed_at": None},
        {"observed_at": "2026-11-19T12:00:00"},
        {"expected_version": "0"},
    ],
)
def test_observation_rejects_invalid_or_self_declared_provenance(fields):
    raw = {
        "state_type": "room_schedule",
        "logical_id": None,
        "observed_at": "2026-11-19T12:00:00Z",
        "expected_version": 0,
        "value": {"status": "free", "activity": "Synthetic"},
        **fields,
    }
    with pytest.raises(ValueError):
        parse_observation(json.dumps(raw).encode())


@pytest.mark.postgres
def test_p507_browser_three_types(live_server):
    database, url, _, _, port = live_server
    with Session(database.engine) as session, session.begin():
        validate_mapping(session, seed=True)
    process = subprocess.run(
        ["node", str(ROOT / "apps/web/tests/p507-integration.mjs")],
        cwd=ROOT,
        text=True,
        env={
            **os.environ,
            "API_PORT": str(port),
            "API_PYTHON": sys.executable,
            "DATABASE_URL": url.get_secret_value(),
        },
        capture_output=True,
        timeout=135,
        check=False,
    )
    assert process.returncode == 0, process.stdout[-3000:] + process.stderr[-3000:]
    report_path = ROOT / ".local/m3-browser/report.json"
    report = json.loads(report_path.read_bytes())
    assert report["status"] == "PASS"
    with Session(database.engine) as session:
        rows = session.scalars(
            select(Outbox).where(Outbox.room_id == ROOM_ID).order_by(Outbox.sequence)
        )
        report["outbox"] = [
            {
                "sequence": row.sequence,
                "publish_recorded_at": row.published_at.isoformat() if row.published_at else None,
            }
            for row in rows
        ]
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
