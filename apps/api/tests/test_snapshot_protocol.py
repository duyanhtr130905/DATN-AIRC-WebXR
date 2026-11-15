"""Protocol framing and a deliberately strict reference receiver, no hardware claims."""

from copy import deepcopy
from uuid import uuid4

import pytest

from app.modules.realtime.snapshot_protocol import (
    MAX_FRAME_BYTES,
    MAX_STATES,
    encoded_size,
    frames_from_snapshot,
)
from app.modules.state.service import StateUnavailable


class AtomicReceiver:
    """Reference client oracle for C1. C2 must implement equivalent TypeScript rules."""

    def __init__(self):
        self.visible = {"old": True}
        self.pending = None

    def receive(self, frame):
        if frame["type"] == "snapshot.start":
            self.pending = {"start": frame, "chunks": [], "states": []}
            return
        assert self.pending is not None
        staged = self.pending
        start = staged["start"]
        assert all(
            frame[key] == start[key]
            for key in ["schema_version", "snapshot_id", "room_id", "watermark", "sequence"]
        )
        if frame["type"] == "snapshot.chunk":
            assert frame["chunk_index"] == len(staged["chunks"])
            staged["chunks"].append(frame)
            staged["states"].extend(frame["states"])
            assert len(staged["states"]) <= start["total_states"] <= MAX_STATES
        else:
            assert frame["type"] == "snapshot.end"
            assert frame["total_chunks"] == start["total_chunks"] == len(staged["chunks"])
            assert frame["total_states"] == start["total_states"] == len(staged["states"])
            assert len({row["id"] for row in staged["states"]}) == len(staged["states"])
            self.visible = {row["id"]: row for row in staged["states"]}
            self.pending = None


def fixture(count):
    return {
        "room_id": str(uuid4()),
        "sequence": count,
        "states": [
            {"id": str(uuid4()), "version": 1, "value": {"text": "Synthetic " * 50}}
            for _ in range(count)
        ],
    }


@pytest.mark.parametrize("count", [0, 1, 32, 33, 41, 80, 120, 512])
def test_bounded_frames_and_atomic_commit(count):
    frames = frames_from_snapshot(fixture(count))
    receiver = AtomicReceiver()
    for frame in frames[:-1]:
        receiver.receive(frame)
        assert receiver.visible == {"old": True}
        assert encoded_size(frame) < MAX_FRAME_BYTES
    receiver.receive(frames[-1])
    assert len(receiver.visible) == count


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "duplicate",
        "reordered",
        "watermark",
        "room",
        "snapshot",
        "totals",
        "duplicate_state",
    ],
)
def test_invalid_or_interrupted_snapshot_never_replaces_visible(fault):
    frames = deepcopy(frames_from_snapshot(fixture(41)))
    if fault == "missing":
        del frames[1]
    elif fault == "duplicate":
        frames.insert(2, deepcopy(frames[1]))
    elif fault == "reordered":
        frames[1], frames[2] = frames[2], frames[1]
    elif fault == "watermark":
        frames[2]["watermark"] += 1
    elif fault == "room":
        frames[2]["room_id"] = str(uuid4())
    elif fault == "snapshot":
        frames[2]["snapshot_id"] = str(uuid4())
    elif fault == "totals":
        frames[-1]["total_states"] += 1
    else:
        frames[2]["states"][0] = frames[1]["states"][0]
    receiver = AtomicReceiver()
    with pytest.raises(AssertionError):
        for frame in frames:
            receiver.receive(frame)
    assert receiver.visible == {"old": True}


def test_capacity_and_byte_limits():
    for data in [fixture(513), {**fixture(1), "sequence": 2**53}]:
        with pytest.raises(StateUnavailable):
            frames_from_snapshot(data)
    data = fixture(1)
    data["states"][0]["value"] = {"text": "x" * 40000}
    with pytest.raises(StateUnavailable):
        frames_from_snapshot(data)
    data = fixture(512)
    for state in data["states"]:
        state["value"] = {"text": "x" * 5000}
    with pytest.raises(StateUnavailable):
        frames_from_snapshot(data)
