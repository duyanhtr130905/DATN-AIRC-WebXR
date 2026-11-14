import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import SQLAlchemyError

from app.modules.state.read import replay, snapshot
from app.modules.state.service import StateUnavailable

router = APIRouter()


async def send(socket, message):
    message.setdefault("timestamp", datetime.now(UTC).isoformat())
    if len(json.dumps(message).encode()) > 256 * 1024:
        raise ValueError("Message capacity")
    await asyncio.wait_for(socket.send_json(message), timeout=1)


@router.websocket("/ws/v1/state")
async def websocket_state(socket: WebSocket):
    app = socket.app
    if socket.headers.get("origin") not in app.state.origins:
        await socket.close(code=1008)
        return
    try:
        room_id = UUID(socket.query_params["room_id"])
        engine = app.state.database.engine
        if engine is None:
            raise StateUnavailable("Database unavailable")
        sub = app.state.broker.subscribe(room_id)
    except (ValueError, KeyError, StateUnavailable):
        await socket.close(code=1008)
        return
    receive = None
    try:
        await socket.accept()
        receive = asyncio.create_task(socket.receive())
        # Register before repeatable-read snapshot; durable replay after watermark closes the race.
        initial = await asyncio.to_thread(snapshot, engine, room_id)
        sequence = initial["sequence"]
        await send(socket, initial)
        ticks = 0
        while True:
            if receive.done():
                incoming = receive.result()
                if incoming["type"] != "websocket.disconnect":
                    await send(
                        socket,
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
                await send(
                    socket,
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
                await send(
                    socket,
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
                await send(socket, message)
                sequence = message["sequence"]
            ticks += 1
            if ticks % 10 == 0:
                await send(
                    socket,
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
            await send(
                socket,
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
