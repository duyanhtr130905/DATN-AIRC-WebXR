import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.state_models import Outbox


@dataclass(eq=False)
class Subscription:
    room_id: UUID | tuple[UUID, str]
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=8))
    overflow: bool = False
    coalesce: bool = False


class Broker:
    def __init__(self):
        self.subscribers: set[Subscription] = set()

    def subscribe(self, room_id, *, coalesce=False):
        if len(self.subscribers) >= 32:
            raise ValueError("Connection limit")
        subscription = Subscription(room_id, coalesce=coalesce)
        self.subscribers.add(subscription)
        return subscription

    async def notify(self, room_id):
        for sub in tuple(self.subscribers):
            if sub.room_id == room_id:
                try:
                    sub.queue.put_nowait(None)
                except asyncio.QueueFull:
                    # V2 hints are coalescible: durable SQL replay owns every delta.
                    if not sub.coalesce:
                        sub.overflow = True


def claim(engine, owner: UUID, lease_seconds=5) -> list[dict]:
    with Session(engine) as session, session.begin():
        now = session.scalar(select(func.clock_timestamp()))
        rows = list(
            session.scalars(
                select(Outbox)
                .where(
                    Outbox.published_at.is_(None),
                    Outbox.exhausted.is_(False),
                    Outbox.next_attempt_at <= now,
                    or_(Outbox.lease_until.is_(None), Outbox.lease_until <= now),
                )
                .order_by(Outbox.room_id, Outbox.sequence)
                .with_for_update(skip_locked=True)
                .limit(16)
            )
        )
        messages = []
        for row in rows:
            if row.attempts >= 5:
                row.exhausted = True
                row.lease_owner = None
                row.lease_until = None
                continue
            row.attempts += 1
            row.lease_owner = owner
            row.lease_until = now + timedelta(seconds=lease_seconds)
            messages.append(
                {
                    "message_id": row.message_id,
                    "room_id": (row.room_id, "admin") if row.audience == "admin" else row.room_id,
                    "attempts": row.attempts,
                }
            )
        return messages


def finish(engine, owner, message, success):
    with Session(engine) as session, session.begin():
        now = session.scalar(select(func.clock_timestamp()))
        values = {"lease_owner": None, "lease_until": None}
        if success:
            values["published_at"] = now
        else:
            values["exhausted"] = message["attempts"] >= 5
            values["next_attempt_at"] = now + timedelta(seconds=min(2 ** message["attempts"], 30))
        session.execute(
            update(Outbox)
            .where(
                Outbox.message_id == message["message_id"],
                Outbox.lease_owner == owner,
                Outbox.published_at.is_(None),
            )
            .values(**values)
        )


class Dispatcher:
    def __init__(self, engine, broker):
        self.engine, self.broker = engine, broker
        self.owner = uuid4()
        self.task = None
        self.stop_event = asyncio.Event()
        self.errors = 0
        self.observations = deque(maxlen=256)

    async def run_once(self):
        messages = await asyncio.to_thread(claim, self.engine, self.owner)
        for message in messages:
            if self.stop_event.is_set():
                break
            success = False
            try:
                await asyncio.wait_for(self.broker.notify(message["room_id"]), timeout=1)
                success = True
            except Exception:
                self.errors += 1
            notification_ns = time.monotonic_ns()
            await asyncio.to_thread(finish, self.engine, self.owner, message, success)
            if success:
                self.observations.append(
                    {
                        "message_id": str(message["message_id"]),
                        "notification_ns": notification_ns,
                        "persisted_ns": time.monotonic_ns(),
                    }
                )
        return len(messages)

    async def run(self):
        while not self.stop_event.is_set():
            if self.engine is not None:
                try:
                    await self.run_once()
                except SQLAlchemyError:
                    self.errors += 1
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=0.1)
            except TimeoutError:
                pass

    def start(self):
        if self.task is None:
            self.stop_event.clear()
            self.task = asyncio.create_task(self.run())

    async def stop(self):
        self.stop_event.set()
        if self.task:
            await self.task
            self.task = None
