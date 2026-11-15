import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import SQLAlchemyError

from app.modules.realtime.snapshot_protocol import MAX_SAFE_INTEGER
from app.modules.state.read import replay, revalidate_snapshot_visibility, snapshot, snapshot_v2
from app.modules.state.service import StateUnavailable

router = APIRouter()


async def send(socket, message):
    message.setdefault("timestamp", datetime.now(UTC).isoformat())
    if message.get("schema_version") == 2:
        sequence = message.get("sequence")
        version = message.get("state", {}).get("version", 1)
        if not isinstance(sequence, int) or not 0 <= sequence <= MAX_SAFE_INTEGER:
            raise ValueError("Unsafe wire sequence")
        if not isinstance(version, int) or not 1 <= version <= MAX_SAFE_INTEGER:
            raise ValueError("Unsafe wire version")
    capacity = 32 * 1024 if message.get("schema_version") == 2 else 256 * 1024
    if len(json.dumps(message).encode()) > capacity:
        raise ValueError("Message capacity")
    await asyncio.wait_for(socket.send_json(message), timeout=1)


@router.websocket("/ws/v1/state")
async def websocket_state(socket: WebSocket):
    app = socket.app
    if socket.headers.get("origin") not in app.state.origins:
        await socket.close(code=1008)
        return
    try:
        protocol = int(socket.query_params.get("protocol", "1"))
        if protocol not in {1, 2}:
            raise ValueError("Unsupported protocol")
        room_id = UUID(socket.query_params["room_id"])
        engine = app.state.database.engine
        if engine is None:
            raise StateUnavailable("Database unavailable")
        sub = app.state.broker.subscribe(room_id, coalesce=protocol == 2)
    except (ValueError, KeyError, StateUnavailable):
        await socket.close(code=1008)
        return

    async def deliver(message):
        message["schema_version"] = protocol
        await send(socket, message)

    receive = None
    try:
        await socket.accept()
        receive = asyncio.create_task(socket.receive())
        # Register before repeatable-read snapshot; durable replay after watermark closes the race.
        if protocol == 1:
            initial = await asyncio.to_thread(snapshot, engine, room_id)
            sequence = initial["sequence"]
            await deliver(initial)
        else:
            frames = await asyncio.to_thread(snapshot_v2, engine, room_id)
            sequence = frames[0]["watermark"]
            all_ids = [
                UUID(state["id"])
                for frame in frames
                if frame["type"] == "snapshot.chunk"
                for state in frame["states"]
            ]
            for frame in frames:
                if receive.done():
                    if receive.result()["type"] != "websocket.disconnect":
                        await deliver(
                            {
                                "type": "error",
                                "message_id": str(uuid4()),
                                "room_id": str(room_id),
                                "sequence": sequence,
                                "code": "READ_ONLY",
                            }
                        )
                        await socket.close(code=1008)
                    return
                if sub.overflow:
                    await deliver(
                        {
                            "type": "resync.required",
                            "message_id": str(uuid4()),
                            "room_id": str(room_id),
                            "sequence": sequence,
                            "reason": "backpressure",
                        }
                    )
                    await socket.close(code=1013)
                    return
                ids = (
                    all_ids
                    if frame["type"] == "snapshot.end"
                    else [UUID(state["id"]) for state in frame.get("states", [])]
                )
                await asyncio.to_thread(revalidate_snapshot_visibility, engine, room_id, ids)
                await deliver(frame)
        ticks = 0
        while True:
            if receive.done():
                incoming = receive.result()
                if incoming["type"] != "websocket.disconnect":
                    await deliver(
                        {
                            "type": "error",
                            "schema_version": 1,
                            "message_id": str(uuid4()),
                            "room_id": str(room_id),
                            "sequence": sequence,
                            "code": "READ_ONLY",
                        },
                    )
                    await socket.close(code=1008)
                return
            if sub.overflow:
                await deliver(
                    {
                        "type": "resync.required",
                        "schema_version": 1,
                        "message_id": str(uuid4()),
                        "room_id": str(room_id),
                        "sequence": sequence,
                        "reason": "backpressure",
                    },
                )
                await socket.close(code=1013)
                return
            try:
                await asyncio.wait_for(sub.queue.get(), timeout=0.25)
            except TimeoutError:
                pass
            messages, more = await asyncio.to_thread(replay, engine, room_id, sequence)
            if more or any(
                message["sequence"] != sequence + index + 1
                for index, message in enumerate(messages)
            ):
                await deliver(
                    {
                        "type": "resync.required",
                        "schema_version": 1,
                        "message_id": str(uuid4()),
                        "room_id": str(room_id),
                        "sequence": sequence,
                        "reason": "gap",
                    },
                )
                await socket.close(code=1013)
                return
            for message in messages:
                await deliver(message)
                sequence = message["sequence"]
            ticks += 1
            if ticks % 10 == 0:
                await deliver(
                    {
                        "type": "heartbeat",
                        "schema_version": 1,
                        "message_id": str(uuid4()),
                        "room_id": str(room_id),
                        "sequence": sequence,
                    },
                )
    except (SQLAlchemyError, StateUnavailable, ValueError, KeyError):
        try:
            await deliver(
                {
                    "type": "error",
                    "schema_version": 1,
                    "message_id": str(uuid4()),
                    "room_id": str(room_id),
                    "sequence": 0,
                    "code": "STATE_UNAVAILABLE",
                },
            )
            await socket.close(code=1011)
        except (RuntimeError, WebSocketDisconnect, OSError, TimeoutError):
            pass
    except (WebSocketDisconnect, OSError, RuntimeError, TimeoutError):
        pass
    finally:
        app.state.broker.subscribers.discard(sub)
        if receive:
            receive.cancel()
            await asyncio.gather(receive, return_exceptions=True)
