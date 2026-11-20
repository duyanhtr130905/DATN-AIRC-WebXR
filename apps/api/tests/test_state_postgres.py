import asyncio
import hashlib
import json
import os
import platform
import socket
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import uvicorn
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, Table, func, insert, inspect, select, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from test_catalog_postgres import isolated_catalog_database
from websockets.exceptions import InvalidStatus
from websockets.sync.client import connect

from alembic import command
from app.core.config import Settings
from app.database.models import Object, Room
from app.database.state_models import CurrentState, Outbox, RoomStateCursor, StateHistory
from app.main import create_app
from app.modules.catalog.seed import OBJECT_IDS, ROOM_ID, seed_demo
from app.modules.realtime.client_rules import sequence_action
from app.modules.realtime.dispatcher import Broker, Dispatcher, claim, finish
from app.modules.state.read import replay, snapshot, snapshot_v2
from app.modules.state.service import StateConflict, StateUnavailable, change_state

pytestmark = pytest.mark.postgres


@pytest.fixture
def state_database():
    with isolated_catalog_database() as (database, url):
        with Session(database.engine) as session, session.begin():
            seed_demo(session)
        yield database, url


def change(
    database,
    version,
    value="available",
    state_type="equipment_status",
    target_kind="object",
    target_id=None,
):
    with Session(database.engine) as session, session.begin():
        return change_state(
            session,
            room_id=ROOM_ID,
            target_kind=target_kind,
            target_id=target_id or OBJECT_IDS[0],
            state_type=state_type,
            value=value if isinstance(value, dict) else {"status": value},
            expected_version=version,
        )


def counts(database):
    with Session(database.engine) as session:
        return [
            session.scalar(select(func.count()).select_from(model))
            for model in (CurrentState, StateHistory, Outbox)
        ]


def test_upgrade_0001_to_0002_preserves_catalog():
    with isolated_catalog_database(migrate=False) as (database, _):
        with database.engine.begin() as connection:
            config = Config(
                str(Path(__file__).resolve().parents[1] / "alembic.ini"), stdout=StringIO()
            )
            config.attributes["connection"] = connection
            command.upgrade(config, "0001_catalog")
            with Session(bind=connection) as session:
                seed_demo(session)
                session.flush()
            command.upgrade(config, "head")
            command.check(config)
            assert connection.scalar(select(func.count()).select_from(Room)) == 1
            assert connection.scalar(select(func.count()).select_from(Object)) == 4
            assert connection.scalar(select(func.count()).select_from(CurrentState)) == 0
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version"))
                == "0007_visitor_terminal_capacity"
            )
            assert inspect(connection).get_unique_constraints("outbox")


def test_upgrade_populated_0002_preserves_state_and_protocol():
    with isolated_catalog_database(migrate=False) as (database, _):
        with database.engine.begin() as connection:
            config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
            config.attributes["connection"] = connection
            command.upgrade(config, "0002_state_realtime")
            with Session(bind=connection) as db:
                seed_demo(db)
                db.flush()

            names = (
                "rooms",
                "objects",
                "current_states",
                "state_history",
                "room_state_cursors",
                "outbox",
            )
            metadata = MetaData()
            tables = {name: Table(name, metadata, autoload_with=connection) for name in names}
            now = datetime.now(UTC)
            sequence = 0
            for state_type, target, values in (
                (
                    "equipment_status",
                    OBJECT_IDS[0],
                    [{"status": "available"}, {"status": "offline"}],
                ),
                ("exhibit_info", OBJECT_IDS[1], [{"title": "Fixture", "text": "Synthetic"}]),
                ("room_schedule", ROOM_ID, [{"status": "free", "activity": "Fixture"}]),
            ):
                state_id = uuid4()
                target_kind = "room" if target == ROOM_ID else "object"
                identity = dict(
                    id=state_id,
                    room_id=ROOM_ID,
                    state_type=state_type,
                    target_room_id=target if target_kind == "room" else None,
                    object_id=target if target_kind == "object" else None,
                )
                for version, value in enumerate(values, 1):
                    sequence += 1
                    stamp = now + timedelta(seconds=sequence)
                    observation = dict(
                        version=version,
                        value=value,
                        source_kind="synthetic",
                        source_observed_at=stamp,
                        committed_at=stamp,
                    )
                    if version == 1:
                        connection.execute(
                            tables["current_states"].insert().values(**identity, **observation)
                        )
                    else:
                        connection.execute(
                            tables["current_states"]
                            .update()
                            .where(tables["current_states"].c.id == state_id)
                            .values(**observation)
                        )
                    connection.execute(
                        tables["state_history"]
                        .insert()
                        .values(id=uuid4(), state_id=state_id, **observation)
                    )
                    payload = dict(
                        observation,
                        id=str(state_id),
                        room_id=str(ROOM_ID),
                        target_kind=target_kind,
                        target_id=str(target),
                        state_type=state_type,
                        source_observed_at=stamp.isoformat(),
                        committed_at=stamp.isoformat(),
                    )
                    connection.execute(
                        tables["outbox"]
                        .insert()
                        .values(
                            message_id=uuid4(),
                            room_id=ROOM_ID,
                            sequence=sequence,
                            payload={"state": payload},
                            committed_at=stamp,
                            published_at=stamp if sequence <= 2 else None,
                        )
                    )
            connection.execute(
                tables["room_state_cursors"].insert().values(room_id=ROOM_ID, sequence=sequence)
            )

        def capture(connection):
            inspector = inspect(connection)
            return {
                name: {
                    "rows": [
                        dict(row)
                        for row in connection.execute(
                            select(tables[name]).order_by(*tables[name].primary_key.columns)
                        ).mappings()
                    ],
                    "primary_key": inspector.get_pk_constraint(name),
                    "foreign_keys": inspector.get_foreign_keys(name),
                    "legacy_checks": [
                        item
                        for item in inspector.get_check_constraints(name)
                        if not item["name"].endswith("_audience")
                    ],
                }
                for name in names
            }

        def summarize(capture):
            return {
                name: {
                    "rows": len(table["rows"]),
                    "sha256": hashlib.sha256(
                        json.dumps(table, sort_keys=True, default=str).encode()
                    ).hexdigest(),
                }
                for name, table in capture.items()
            }

        with database.engine.begin() as connection:
            config.attributes["connection"] = connection
            baseline = capture(connection)
            report = {"0002_state_realtime": summarize(baseline)}
            for revision in ("0003_admin_manual", "head"):
                command.upgrade(config, revision)
                actual = capture(connection)
                assert actual == baseline
                current = connection.scalar(text("SELECT version_num FROM alembic_version"))
                report[current] = summarize(actual)
                for name in ("current_states", "outbox"):
                    assert connection.execute(
                        text(f"SELECT DISTINCT audience FROM {name}")
                    ).scalars().all() == ["public"]
            command.check(config)

        with Session(database.engine) as db, db.begin():
            change_state(
                db,
                room_id=ROOM_ID,
                target_kind="object",
                target_id=OBJECT_IDS[0],
                state_type="equipment_status",
                value={"status": "maintenance"},
                expected_version=0,
                source_observed_at=now,
                audience="admin",
            )
        assert len(snapshot(database.engine, ROOM_ID)["states"]) == 3
        frames = snapshot_v2(database.engine, ROOM_ID)
        assert frames[-1]["type"] == "snapshot.end"
        assert frames[-1]["sequence"] == sequence
        assert "maintenance" not in json.dumps(frames)
    report_path = Path(__file__).resolve().parents[3] / ".local/m3-migration-report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def test_atomic_versions_stale_duplicate_and_rollback(state_database):
    database, _ = state_database
    first = change(database, 0)
    assert first["state"]["version"] == 1
    second = change(database, 1, "maintenance")
    assert second["state"]["version"] == 2 and second["sequence"] == 2
    with pytest.raises(StateConflict):
        change(database, 1, "maintenance")
    assert counts(database) == [1, 2, 2]
    with pytest.raises(RuntimeError), Session(database.engine) as session, session.begin():
        change_state(
            session,
            room_id=ROOM_ID,
            target_kind="object",
            target_id=OBJECT_IDS[0],
            state_type="equipment_status",
            value={"status": "offline"},
            expected_version=2,
        )
        raise RuntimeError("rollback")
    assert counts(database) == [1, 2, 2]
    with Session(database.engine) as session:
        state = session.scalar(select(CurrentState))
        assert state.version == 2 and state.value == {"status": "maintenance"}
        assert [
            row.version
            for row in session.scalars(select(StateHistory).order_by(StateHistory.version))
        ] == [1, 2]
        assert session.get(RoomStateCursor, ROOM_ID).sequence == 2


def test_two_real_postgres_writers_only_one_wins(state_database):
    database, _ = state_database
    change(database, 0)
    barrier = threading.Barrier(2)

    def writer(status):
        barrier.wait(timeout=5)
        try:
            return change(database, 1, status)["state"]["version"]
        except StateConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        result = list(executor.map(writer, ["maintenance", "offline"]))
    assert sorted(map(str, result)) == ["2", "conflict"]
    assert counts(database) == [1, 2, 2]


@pytest.mark.parametrize("protected", ["unknown", "real_verified"])
def test_target_mapping_protection_read_api_history(state_database, protected):
    database, url = state_database
    change(database, 0)
    change(database, 1, "maintenance")
    change(database, 0, {"status": "free", "activity": "DEMO"}, "room_schedule", "room", ROOM_ID)
    change(database, 0, {"title": "DEMO", "text": "Synthetic"}, "exhibit_info")
    with pytest.raises(ValueError):
        change(database, 0, {"status": "free", "activity": "DEMO"}, "room_schedule")
    with pytest.raises(StateUnavailable):
        change(database, 0, target_id=uuid4())
    with TestClient(
        create_app(Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=False))
    ) as client:
        first = client.get(
            f"/api/v1/objects/{OBJECT_IDS[0]}/states/equipment_status/history?limit=1"
        ).json()
        assert first["data"][0]["version"] == 1 and first["meta"]["next_after_version"] == 1
        second = client.get(
            f"/api/v1/objects/{OBJECT_IDS[0]}/states/equipment_status/history?after_version=1"
        ).json()
        assert second["data"][0]["version"] == 2 and second["meta"]["next_after_version"] is None
    with Session(database.engine) as session, session.begin():
        session.execute(
            update(CurrentState)
            .where(CurrentState.state_type == "equipment_status")
            .values(source_kind=protected)
        )
    with pytest.raises(StateUnavailable):
        change(database, 2, "offline")
    with TestClient(
        create_app(Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=False))
    ) as client:
        data = client.get(f"/api/v1/rooms/{ROOM_ID}/states?limit=1").json()
        assert len(data["data"]) == 1 and data["meta"]["next_cursor"]
        all_states = client.get(f"/api/v1/objects/{OBJECT_IDS[0]}/states").json()["data"]
        assert len(all_states) == 1 and all_states[0]["state_type"] == "exhibit_info"
        assert (
            client.get(
                f"/api/v1/objects/{OBJECT_IDS[0]}/states/equipment_status/history"
            ).status_code
            == 404
        )
        assert client.get("/api/v1/rooms/not-uuid/states").status_code == 422
        assert client.get(f"/api/v1/rooms/{ROOM_ID}/states?limit=101").status_code == 422
        assert client.post(f"/api/v1/rooms/{ROOM_ID}/states", json={}).status_code == 405
    with Session(database.engine) as session, session.begin():
        session.execute(update(Room).where(Room.id == ROOM_ID).values(source_kind="unknown"))
    with pytest.raises(StateUnavailable):
        change(database, 0, target_id=OBJECT_IDS[1])
    with TestClient(
        create_app(Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=False))
    ) as client:
        assert client.get(f"/api/v1/rooms/{ROOM_ID}/states").status_code == 404
        assert client.get(f"/api/v1/objects/{OBJECT_IDS[0]}/states").status_code == 404


@pytest.mark.parametrize(
    "kind",
    [
        "history_update",
        "history_delete",
        "duplicate_history",
        "version_zero",
        "bad_target",
        "bad_value",
        "bad_fk",
        "duplicate_sequence",
    ],
)
def test_state_constraints_and_immutable_history(state_database, kind):
    database, _ = state_database
    change(database, 0)
    with pytest.raises(DBAPIError), database.engine.begin() as connection:
        if kind == "history_update":
            connection.execute(text("UPDATE state_history SET version=9"))
        elif kind == "history_delete":
            connection.execute(text("DELETE FROM state_history"))
        elif kind == "duplicate_history":
            connection.execute(
                text(
                    "INSERT INTO state_history SELECT gen_random_uuid(),state_id,version,value,"
                    "source_kind,source_observed_at,committed_at FROM state_history"
                )
            )
        elif kind == "version_zero":
            connection.execute(text("UPDATE current_states SET version=0"))
        elif kind == "bad_target":
            connection.execute(text("UPDATE current_states SET state_type='room_schedule'"))
        elif kind == "bad_value":
            connection.execute(text("UPDATE current_states SET value='[]'::jsonb"))
        elif kind == "bad_fk":
            connection.execute(text("UPDATE current_states SET object_id=:id"), {"id": uuid4()})
        elif kind == "duplicate_sequence":
            row = connection.execute(select(Outbox.__table__)).mappings().one()
            connection.execute(insert(Outbox.__table__).values(**{**row, "message_id": uuid4()}))


def test_outbox_claim_retry_crash_restart_and_worker_race(state_database):
    database, _ = state_database
    change(database, 0)

    async def exercise():
        broker = Broker()
        dispatcher = Dispatcher(database.engine, broker)
        original = broker.notify

        async def fail(_):
            raise RuntimeError("publisher failure")

        broker.notify = fail
        await dispatcher.run_once()
        with Session(database.engine) as session:
            row = session.scalar(select(Outbox))
            assert (
                row.attempts == 1
                and row.published_at is None
                and row.next_attempt_at > row.committed_at
            )
        with database.engine.begin() as c:
            c.execute(update(Outbox).values(next_attempt_at=func.now()))
        broker.notify = original
        await dispatcher.run_once()
        with Session(database.engine) as session:
            assert session.scalar(select(Outbox)).published_at is not None

    asyncio.run(exercise())
    change(database, 1, "maintenance")
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(lambda owner: claim(database.engine, owner), [uuid4(), uuid4()]))
    assert sum(len(rows) for rows in claims) == 1
    with database.engine.begin() as c:
        c.execute(
            update(Outbox)
            .where(Outbox.published_at.is_(None))
            .values(lease_until=func.now() - text("interval '1 second'"))
        )
    recovery_owner = uuid4()
    recovered = claim(database.engine, recovery_owner)
    assert len(recovered) == 1 and recovered[0]["attempts"] == 2
    finish(database.engine, recovery_owner, recovered[0], True)
    with Session(database.engine) as session:
        assert all(row.published_at is not None for row in session.scalars(select(Outbox)))


def test_latest_exhausted_delta_requires_resync_and_gap(state_database):
    database, _ = state_database
    change(database, 0)
    with database.engine.begin() as c:
        c.execute(
            update(Outbox).values(
                exhausted=True, attempts=5, committed_at=func.now() - text("interval '3 seconds'")
            )
        )
    rows, requires = replay(database.engine, ROOM_ID, 0)
    assert rows == [] and requires
    assert claim(database.engine, uuid4()) == []
    assert snapshot(database.engine, ROOM_ID)["sequence"] == 1
    assert (
        sequence_action(1, 1) == "ignore"
        and sequence_action(1, 0) == "ignore"
        and sequence_action(1, 3) == "resync"
    )


@pytest.fixture
def live_server(state_database, live_options):
    database, url = state_database
    application = create_app(
        Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=True, **live_options)
    )
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            application,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            ws="websockets-sansio",
            ws_max_size=8192,
            ws_max_queue=1,
            timeout_graceful_shutdown=3,
        )
    )
    thread = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
    try:
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started
        yield database, url, application, server, port
    finally:
        server.should_exit = True
        if thread.ident is not None:
            thread.join(timeout=15)
            if thread.is_alive():
                server.force_exit = True
                thread.join(timeout=3)
        listener.close()
        assert not thread.is_alive(), "Server must shut down within timeout"
        assert database.engine.pool.checkedout() == 0
        broker = getattr(application.state, "broker", None)
        assert broker is None or not broker.subscribers


def receive_type(ws, kind):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        message = json.loads(ws.recv(timeout=max(0.1, deadline - time.monotonic())))
        if message["type"] == kind:
            return message
        assert message["type"] not in {"error", "resync.required"}, message
    pytest.fail("WebSocket timed out")


def test_real_tcp_websocket_snapshot_delta_reconnect_backlog_and_metrics(live_server):
    database, _, application, server, port = live_server
    change(database, 0)
    uri = f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}"
    measurements = []
    replica = {"sequence": 0, "state": None}
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        first = receive_type(ws, "snapshot")
        measured_subscribers = len(application.state.broker.subscribers)
        assert measured_subscribers == 1
        assert first["states"][0]["value"] == {"status": "available"}
        for index in range(20):
            start = time.monotonic_ns()
            result = change(database, index + 1, "maintenance" if index % 2 == 0 else "available")
            commit = time.monotonic_ns()
            delta = receive_type(ws, "state.updated")
            received = time.monotonic_ns()
            assert (
                delta["state"]["version"] == index + 2 and delta["sequence"] == result["sequence"]
            )
            assert delta["message_id"] == result["message_id"]
            assert (
                sequence_action(
                    first["sequence"] if index == 0 else replica["sequence"], delta["sequence"]
                )
                == "apply"
            )
            previous = replica["state"]
            replica = {"sequence": delta["sequence"], "state": delta["state"]}
            saved = json.dumps(replica, sort_keys=True)
            for old_sequence in [delta["sequence"], delta["sequence"] - 1]:
                if sequence_action(replica["sequence"], old_sequence) == "apply":
                    replica["state"] = previous
            assert json.dumps(replica, sort_keys=True) == saved

            with Session(database.engine) as session:
                row = session.get(Outbox, UUID(delta["message_id"]))
                # Same-host test clocks: report wall-clock split with uncertainty, monotonic total.
                published = row.published_at
                committed = row.committed_at
            deadline = time.monotonic() + 2
            observation = None
            while time.monotonic() < deadline:
                observation = next(
                    (
                        row
                        for row in application.state.dispatcher.observations
                        if row["message_id"] == delta["message_id"]
                    ),
                    None,
                )
                if observation:
                    break
                time.sleep(0.005)
            assert observation is not None
            measurements.append(
                {
                    "transaction_ms": (commit - start) / 1e6,
                    "commit_return_to_publish_ms": (observation["notification_ns"] - commit) / 1e6,
                    "publish_to_client_ms": (received - observation["notification_ns"]) / 1e6,
                    "update_to_client_ms": (received - start) / 1e6,
                    "commit_to_client_ms": (received - commit) / 1e6,
                    "db_mutation_to_publish_ms": (published - committed).total_seconds() * 1000,
                }
            )
    change(database, 21, "offline")
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        state = receive_type(ws, "snapshot")
        assert state["states"][0]["version"] == 22
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with Session(database.engine) as session:
            if (
                session.scalar(
                    select(func.count()).select_from(Outbox).where(Outbox.published_at.is_(None))
                )
                == 0
            ):
                break
        time.sleep(0.02)
    else:
        pytest.fail("Existing notifications must finish before pause")
    # Stop/restart the actual server dispatcher through its event loop, not a publisher mock.
    loop = application.state.dispatcher.task.get_loop()
    asyncio.run_coroutine_threadsafe(application.state.dispatcher.stop(), loop).result(timeout=8)
    result = change(database, 22, "maintenance")
    with Session(database.engine) as session:
        assert session.get(Outbox, UUID(result["message_id"])).published_at is None
    loop.call_soon_threadsafe(application.state.dispatcher.start)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with Session(database.engine) as session:
            if session.get(Outbox, UUID(result["message_id"])).published_at:
                break
        time.sleep(0.02)
    else:
        pytest.fail("Restart must process pending outbox")
    with Session(database.engine) as session:
        backlog = session.scalar(
            select(func.count()).select_from(Outbox).where(Outbox.published_at.is_(None))
        )
        retries = session.scalar(select(func.sum(Outbox.attempts))) - 23
        postgres_version = session.scalar(text("SHOW server_version"))
        assert counts(database) == [1, 23, 23]
    deadline = time.monotonic() + 3
    while application.state.broker.subscribers and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not application.state.broker.subscribers
    report = {
        "samples": len(measurements),
        "environment": {
            "os": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
            "postgres": postgres_version,
            "uvicorn": uvicorn.__version__,
            "api_processes": 1,
            "transport": "same-host loopback TCP",
        },
        "clock": "monotonic_ns for transaction, commit-return, notification and client receive; "
        "DB timestamps are mutation/publish markers, not exact WAL commit",
        "measurements": measurements,
        "backlog": backlog,
        "retry_count": retries,
        "subscriber_count_during_stream": measured_subscribers,
        "subscriber_count_after_disconnect": len(application.state.broker.subscribers),
        "not_a_kpi": "No source-to-render or real device/FPS measurement",
    }
    for metric in measurements[0]:
        values = sorted(row[metric] for row in measurements)
        report[metric] = {"p50": statistics.median(values), "p95": values[18]}
    out = Path(__file__).resolve().parents[3] / ".local" / "m1-b-metrics.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def test_real_tcp_wrong_origin_room_hidden_and_no_client_writes(live_server):
    database, _, _, _, port = live_server
    base = f"ws://127.0.0.1:{port}/ws/v1/state"
    with pytest.raises(InvalidStatus):
        connect(base + f"?room_id={ROOM_ID}", origin="https://untrusted.test", open_timeout=3)
    for identity in [uuid4(), ROOM_ID]:
        if identity == ROOM_ID:
            with database.engine.begin() as c:
                c.execute(update(Room).where(Room.id == ROOM_ID).values(source_kind="unknown"))
        with connect(
            base + f"?room_id={identity}",
            origin="http://localhost:5173",
            open_timeout=3,
            close_timeout=2,
        ) as ws:
            assert json.loads(ws.recv(timeout=5))["type"] == "error"
    with database.engine.begin() as c:
        c.execute(update(Room).where(Room.id == ROOM_ID).values(source_kind="synthetic"))
    with connect(
        base + f"?room_id={ROOM_ID}",
        origin="http://localhost:5173",
        open_timeout=3,
        close_timeout=2,
    ) as ws:
        receive_type(ws, "snapshot")
        ws.send('{"type":"state.update"}')
        assert json.loads(ws.recv(timeout=5))["code"] == "READ_ONLY"
    assert counts(database) == [0, 0, 0]


def test_bounded_publisher_retries_keep_business_state(state_database):
    database, _ = state_database
    change(database, 0)

    async def run():
        broker = Broker()

        async def fail(_):
            raise RuntimeError("failure")

        broker.notify = fail
        dispatcher = Dispatcher(database.engine, broker)
        for _ in range(5):
            with database.engine.begin() as connection:
                connection.execute(update(Outbox).values(next_attempt_at=func.now()))
            await dispatcher.run_once()
        assert await dispatcher.run_once() == 0
        with Session(database.engine) as session:
            row = session.scalar(select(Outbox))
            assert row.attempts == 5 and row.exhausted and row.published_at is None
        assert counts(database) == [1, 1, 1]

    asyncio.run(run())


def test_actual_database_backend_disconnect_rolls_back(state_database):
    database, _ = state_database
    with pytest.raises(DBAPIError):
        with Session(database.engine) as session, session.begin():
            change_state(
                session,
                room_id=ROOM_ID,
                target_kind="object",
                target_id=OBJECT_IDS[0],
                state_type="equipment_status",
                value={"status": "available"},
                expected_version=0,
            )
            pid = session.scalar(text("SELECT pg_backend_pid()"))
            with database.engine.begin() as killer:
                assert killer.scalar(text("SELECT pg_terminate_backend(:pid)"), {"pid": pid})
            session.execute(text("SELECT 1"))
    assert counts(database) == [0, 0, 0]
    assert change(database, 0)["state"]["version"] == 1


def test_actual_snapshot_subscribe_race_and_queue_resync(live_server):
    from unittest.mock import patch

    from app.modules.realtime import router as websocket_router

    database, _, application, _, port = live_server
    change(database, 0)
    original = websocket_router.snapshot

    def change_after_snapshot(engine, room_id):
        initial = original(engine, room_id)
        change(database, 1, "maintenance")
        return initial

    uri = f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}"
    with patch.object(websocket_router, "snapshot", side_effect=change_after_snapshot):
        with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
            first = receive_type(ws, "snapshot")
            assert first["states"][0]["version"] == 1
            updated = receive_type(ws, "state.updated")
            assert updated["state"]["version"] == 2

            async def pressure():
                for _ in range(20):
                    await application.state.broker.notify(ROOM_ID)

            loop = application.state.dispatcher.task.get_loop()
            asyncio.run_coroutine_threadsafe(pressure(), loop).result(timeout=3)
            assert json.loads(ws.recv(timeout=5))["type"] == "resync.required"


def test_actual_out_of_order_publication_resync(live_server):
    database, _, application, _, port = live_server
    change(database, 0)
    uri = f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}"
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        receive_type(ws, "snapshot")
        loop = application.state.dispatcher.task.get_loop()
        asyncio.run_coroutine_threadsafe(application.state.dispatcher.stop(), loop).result(
            timeout=8
        )
        change(database, 1, "maintenance")
        change(database, 2, "offline")
        with database.engine.begin() as connection:
            connection.execute(
                update(Outbox).where(Outbox.sequence == 3).values(published_at=func.now())
            )
        asyncio.run_coroutine_threadsafe(application.state.broker.notify(ROOM_ID), loop).result(
            timeout=3
        )
        result = json.loads(ws.recv(timeout=5))
        assert result["type"] == "resync.required" and result["reason"] == "gap"
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        result = receive_type(ws, "snapshot")
        assert result["sequence"] == 3 and result["states"][0]["value"] == {"status": "offline"}


def test_actual_websocket_database_outage_returns_safe_error(live_server):
    from sqlalchemy import create_engine
    from sqlalchemy.engine import make_url
    from sqlalchemy.pool import NullPool

    database, url, application, _, port = live_server
    change(database, 0)
    parsed = make_url(url.get_secret_value())
    name = parsed.database
    assert name.startswith("airc_test_catalog_") and name.replace("_", "").isalnum()
    administrator = create_engine(
        parsed.set(database="airc_foundation_test"),
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    uri = f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}"
    try:
        with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
            receive_type(ws, "snapshot")
            with administrator.connect() as connection:
                connection.exec_driver_sql(f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS false')
                connection.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=:name"
                    ),
                    {"name": name},
                )
            message = json.loads(ws.recv(timeout=8))
            assert message["type"] == "error" and message["code"] == "STATE_UNAVAILABLE"
            assert "password" not in json.dumps(message).lower()
    finally:
        with administrator.connect() as connection:
            connection.exec_driver_sql(f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS true')
        administrator.dispose()
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        assert receive_type(ws, "snapshot")["states"][0]["version"] == 1


def test_actual_guarded_state_cli_value_file_and_duplicate(state_database):
    import subprocess
    import sys

    from sqlalchemy.engine import make_url

    database, url = state_database
    api_root = Path(__file__).resolve().parents[1]
    name = make_url(url.get_secret_value()).database
    env = {**os.environ, "DATABASE_URL": url.get_secret_value()}
    base = [
        sys.executable,
        "-m",
        "app.modules.state.cli",
        "--confirm-database",
        name,
        "--room-id",
        str(ROOM_ID),
        "--target-kind",
        "object",
        "--target-id",
        str(OBJECT_IDS[0]),
        "--state-type",
        "equipment_status",
    ]
    for version, filename in [(0, "equipment-available.json"), (1, "equipment-maintenance.json")]:
        result = subprocess.run(
            base
            + [
                "--expected-version",
                str(version),
                "--value-file",
                str(api_root / "examples" / filename),
            ],
            cwd=api_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0
        assert json.loads(result.stdout)["state"]["version"] == version + 1
    result = subprocess.run(
        base
        + [
            "--expected-version",
            "0",
            "--value-file",
            str(api_root / "examples/equipment-available.json"),
        ],
        cwd=api_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0 and counts(database) == [1, 2, 2]


def test_actual_rollback_never_emits_websocket_delta(live_server):
    database, _, _, _, port = live_server
    change(database, 0)
    uri = f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}"
    with connect(uri, origin="http://localhost:5173", open_timeout=5, close_timeout=2) as ws:
        assert receive_type(ws, "snapshot")["sequence"] == 1
        with pytest.raises(RuntimeError), Session(database.engine) as session, session.begin():
            change_state(
                session,
                room_id=ROOM_ID,
                target_kind="object",
                target_id=OBJECT_IDS[0],
                state_type="equipment_status",
                value={"status": "maintenance"},
                expected_version=1,
            )
            with pytest.raises(TimeoutError):
                ws.recv(timeout=0.4)
            raise RuntimeError("transaction rollback")
        assert counts(database) == [1, 1, 1]
        change(database, 1, "offline")
        delta = receive_type(ws, "state.updated")
        assert delta["sequence"] == 2 and delta["state"]["value"] == {"status": "offline"}


def test_actual_dispatcher_drains_connections_before_dispose(state_database):
    database, url = state_database
    change(database, 0)
    application = create_app(
        Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=True)
    )
    with TestClient(application) as client:
        assert application.state.dispatcher.task is not None
        assert client.get("/api/ready").status_code == 200
        client.portal.call(application.state.dispatcher.stop)
        assert application.state.dispatcher.task is None
        assert application.state.database.engine.pool.checkedout() == 0
        assert client.get("/api/ready").status_code == 200
        assert application.state.database.engine.pool.checkedout() == 0
    assert database.engine.pool.checkedout() == 0
