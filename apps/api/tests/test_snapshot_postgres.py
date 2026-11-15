"""Real PostgreSQL18 and TCP protocol2, reusing the M1-B disposable DB guard."""

import asyncio
import json
import time
from uuid import UUID, uuid4

import pytest
from sqlalchemy import update
from sqlalchemy.orm import Session
from test_snapshot_protocol import AtomicReceiver
from test_state_postgres import change, receive_type
from test_state_postgres import live_server as live_server
from test_state_postgres import state_database as state_database
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from app.database.models import Object
from app.modules.catalog.seed import ROOM_ID
from app.modules.state.read import snapshot, snapshot_v2
from app.modules.state.service import StateUnavailable, change_state

pytestmark = pytest.mark.postgres


def populate(database, count):
    ids = []
    with Session(database.engine) as session, session.begin():
        for index in range(count):
            identity = uuid4()
            ids.append(identity)
            session.add(
                Object(
                    id=identity,
                    room_id=ROOM_ID,
                    name=f"SYNTHETIC {index}",
                    type="demo",
                    source_kind="synthetic",
                    metadata_json={},
                )
            )
            session.flush()
            change_state(
                session,
                room_id=ROOM_ID,
                target_kind="object",
                target_id=identity,
                state_type="equipment_status",
                value={"status": "available"},
                expected_version=0,
            )
    return ids


def uri(port):
    return f"ws://127.0.0.1:{port}/ws/v1/state?room_id={ROOM_ID}&protocol=2"


def receive_snapshot(ws):
    receiver = AtomicReceiver()
    frames = []
    while True:
        frame = json.loads(ws.recv(timeout=8))
        assert frame["schema_version"] == 2
        receiver.receive(frame)
        frames.append(frame)
        if frame["type"] == "snapshot.end":
            return receiver, frames


@pytest.mark.parametrize("count", [0, 1, 32, 33, 41, 80, 120])
def test_real_tcp_scalability_and_v1_compatibility(live_server, count):
    database, _, _, _, port = live_server
    populate(database, count)
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        receiver, frames = receive_snapshot(ws)
        assert len(receiver.visible) == count
        assert frames[0]["watermark"] == count
        assert all(frame["watermark"] == count for frame in frames)
    if count <= 32:
        assert len(snapshot(database.engine, ROOM_ID)["states"]) == count
    else:
        with pytest.raises(StateUnavailable):
            snapshot(database.engine, ROOM_ID)


def test_real_postgres_capacity_abort(state_database):
    database, _ = state_database
    populate(database, 513)
    with pytest.raises(StateUnavailable):
        snapshot_v2(database.engine, ROOM_ID)
    assert database.engine.pool.checkedout() == 0


def test_tcp_writer_between_chunks_replayed_after_atomic_snapshot(live_server, monkeypatch):
    import app.modules.realtime.router as wire

    database, _, _, _, port = live_server
    targets = populate(database, 41)
    original = wire.send
    changed = False

    async def send(socket, frame):
        nonlocal changed
        # The consistent DB transaction must be over before awaiting network.
        if frame["type"] == "snapshot.chunk" and not changed:
            changed = True

            def writer():
                with Session(database.engine) as session, session.begin():
                    change_state(
                        session,
                        room_id=ROOM_ID,
                        target_kind="object",
                        target_id=targets[0],
                        state_type="equipment_status",
                        value={"status": "maintenance"},
                        expected_version=1,
                    )

            await asyncio.to_thread(writer)
        await original(socket, frame)

    monkeypatch.setattr(wire, "send", send)
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        receiver, frames = receive_snapshot(ws)
        assert frames[-1]["watermark"] == 41
        assert all(row["version"] == 1 for row in receiver.visible.values())
        delta = receive_type(ws, "state.updated")
        assert delta["schema_version"] == 2 and delta["sequence"] == 42
        assert delta["state"]["version"] == 2
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        receiver, frames = receive_snapshot(ws)
        assert frames[-1]["watermark"] == 42
        assert max(row["version"] for row in receiver.visible.values()) == 2


@pytest.mark.parametrize("fault", ["hide", "overflow", "disconnect"])
def test_interrupted_snapshot_not_committed_and_cleanup(live_server, monkeypatch, fault):
    import app.modules.realtime.router as wire

    database, _, application, _, port = live_server
    populate(database, 41)
    original = wire.send
    injected = False

    async def send(socket, frame):
        nonlocal injected
        await original(socket, frame)
        if frame["type"] == "snapshot.chunk" and not injected:
            injected = True
            if fault == "hide":
                # Hide an already-sent target. End validation must reject whole staging.
                target = UUID(frame["states"][0]["target_id"])

                def hide():
                    with database.engine.begin() as c:
                        c.execute(
                            update(Object).where(Object.id == target).values(source_kind="unknown")
                        )

                await asyncio.to_thread(hide)
            elif fault == "overflow":
                for sub in application.state.broker.subscribers:
                    sub.overflow = True
            else:
                await socket.close(code=1013)
                raise ConnectionError("Fault injection: transport gone")

    monkeypatch.setattr(wire, "send", send)
    receiver = AtomicReceiver()
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        while True:
            try:
                frame = json.loads(ws.recv(timeout=8))
            except ConnectionClosed:
                break
            if frame["type"] in {"error", "resync.required"}:
                break
            receiver.receive(frame)
    assert injected and receiver.visible == {"old": True}
    deadline = time.monotonic() + 4
    while application.state.broker.subscribers and time.monotonic() < deadline:
        time.sleep(0.01)
    assert not application.state.broker.subscribers


def test_v2_dispatcher_restart_durable_delta(live_server):
    database, _, application, _, port = live_server
    change(database, 0)
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        receiver, _ = receive_snapshot(ws)
        assert next(iter(receiver.visible.values()))["version"] == 1
        loop = application.state.dispatcher.task.get_loop()
        asyncio.run_coroutine_threadsafe(application.state.dispatcher.stop(), loop).result(8)
        change(database, 1, "maintenance")
        loop.call_soon_threadsafe(application.state.dispatcher.start)
        delta = receive_type(ws, "state.updated")
        assert delta["sequence"] == 2 and delta["state"]["version"] == 2
        assert delta["schema_version"] == 2


def test_tcp_client_write_during_snapshot_is_rejected(live_server, monkeypatch):
    import app.modules.realtime.router as wire

    database, _, _, _, port = live_server
    populate(database, 41)
    original = wire.send

    async def slow_start(socket, frame):
        await original(socket, frame)
        if frame["type"] == "snapshot.start":
            await asyncio.sleep(0.2)  # Fault injection: hold sending while client writes.

    monkeypatch.setattr(wire, "send", slow_start)
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        assert json.loads(ws.recv(timeout=5))["type"] == "snapshot.start"
        ws.send('{"type":"state.update"}')
        frame = json.loads(ws.recv(timeout=5))
        assert frame["type"] == "error" and frame["code"] == "READ_ONLY"
        with pytest.raises(ConnectionClosed) as error:
            ws.recv(timeout=5)
        assert error.value.rcvd.code == 1008


@pytest.mark.parametrize("fault", ["missing", "duplicate", "reordered", "watermark"])
def test_tcp_corrupted_snapshot_is_rejected_atomically(live_server, monkeypatch, fault):
    import app.modules.realtime.router as wire

    database, _, _, _, port = live_server
    populate(database, 41)
    original = wire.send
    held = None

    async def corrupt(socket, frame):
        nonlocal held
        if frame["type"] == "snapshot.chunk":
            index = frame["chunk_index"]
            if fault == "missing" and index == 0:
                return
            if fault == "duplicate" and index == 0:
                await original(socket, frame)
            if fault == "watermark" and index == 0:
                frame = {**frame, "watermark": frame["watermark"] + 1}
            if fault == "reordered" and index == 0:
                held = frame
                return
            if fault == "reordered" and index == 1:
                await original(socket, frame)
                await original(socket, held)
                return
        await original(socket, frame)

    monkeypatch.setattr(wire, "send", corrupt)
    receiver = AtomicReceiver()
    with connect(uri(port), origin="http://localhost:5173", open_timeout=5) as ws:
        with pytest.raises(AssertionError):
            for _ in range(10):
                frame = json.loads(ws.recv(timeout=5))
                receiver.receive(frame)
        assert receiver.visible == {"old": True}
