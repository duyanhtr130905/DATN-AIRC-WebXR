"""Independent fixture generator. Imports no application model, DTO or write code."""

from datetime import datetime, timedelta
from random import Random
from uuid import UUID


def expected_visits(at: datetime):
    generator = Random(2700005)
    for synthetic_index in range(50):
        events = []
        for index in range(20):
            kind = ("room_enter", "object_select", "info_open", "info_close")[index % 4]
            object_id = (
                None
                if kind == "room_enter"
                else ("demo-object-cube", "demo-object-column")[(synthetic_index + index // 4) % 2]
            )
            events.append(
                {
                    "id": str(UUID(int=generator.getrandbits(128), version=4)),
                    "schema_version": 1,
                    "event_type": kind,
                    "room_id": "demo-room-foundation",
                    "object_id": object_id,
                    "occurred_at": (at + timedelta(milliseconds=index)).isoformat(),
                }
            )
        yield synthetic_index, events
