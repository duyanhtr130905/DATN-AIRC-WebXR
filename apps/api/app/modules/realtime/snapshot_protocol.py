"""Protocol2 bounded snapshot framing; no network or database lifetime here."""

import json
from uuid import uuid4

from app.modules.state.service import StateUnavailable

MAX_STATES = 512
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_FRAME_BYTES = 32 * 1024
MAX_SAFE_INTEGER = 2**53 - 1


def encoded_size(value) -> int:
    # Conservative vs UTF-8 send_json: escaping non-ASCII can only increase size.
    return len(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode())


def frames_from_snapshot(snapshot: dict) -> list[dict]:
    states = snapshot["states"]
    watermark = snapshot["sequence"]
    if (
        len(states) > MAX_STATES
        or not 0 <= watermark <= MAX_SAFE_INTEGER
        or any(not 1 <= state["version"] <= MAX_SAFE_INTEGER for state in states)
        or encoded_size(states) > MAX_SNAPSHOT_BYTES
    ):
        raise StateUnavailable("Snapshot capacity exceeded")
    snapshot_id = str(uuid4())
    common = {
        "schema_version": 2,
        "snapshot_id": snapshot_id,
        "room_id": snapshot["room_id"],
        "watermark": watermark,
        "sequence": watermark,
    }
    groups = []
    current = []
    for state in states:
        # Reserve1024 bytes for envelope/timestamp, enforce both item and byte limits.
        if current and (
            len(current) >= 16 or encoded_size([*current, state]) > MAX_FRAME_BYTES - 1024
        ):
            groups.append(current)
            current = []
        if encoded_size([state]) > MAX_FRAME_BYTES - 1024:
            raise StateUnavailable("State frame capacity exceeded")
        current.append(state)
    if current:
        groups.append(current)
    totals = {"total_chunks": len(groups), "total_states": len(states)}
    result = [{**common, "type": "snapshot.start", "message_id": str(uuid4()), **totals}]
    result.extend(
        {
            **common,
            "type": "snapshot.chunk",
            "message_id": str(uuid4()),
            "chunk_index": index,
            "states": group,
        }
        for index, group in enumerate(groups)
    )
    result.append({**common, "type": "snapshot.end", "message_id": str(uuid4()), **totals})
    if any(encoded_size(frame) > MAX_FRAME_BYTES - 128 for frame in result):
        raise StateUnavailable("Snapshot envelope capacity exceeded")
    return result
