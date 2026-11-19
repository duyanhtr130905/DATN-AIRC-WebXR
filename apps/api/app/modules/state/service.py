from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models import Object, Room
from app.database.state_models import CurrentState, Outbox, RoomStateCursor, StateHistory
from app.modules.state.schemas import StateResponse, validate_value


class StateConflict(Exception):
    pass


class StateUnavailable(Exception):
    pass


def visible_room(session: Session, room_id: UUID, lock=False):
    query = select(Room).where(Room.id == room_id, Room.source_kind == "synthetic")
    if lock:
        query = query.with_for_update()
    room = session.scalar(query)
    if room is None:
        raise StateUnavailable("Target unavailable")
    return room


def visible_states(room_id: UUID):
    return (
        select(CurrentState)
        .join(Room, Room.id == CurrentState.room_id)
        .outerjoin(Object, Object.id == CurrentState.object_id)
        .where(
            CurrentState.room_id == room_id,
            CurrentState.audience == "public",
            CurrentState.source_kind == "synthetic",
            Room.source_kind == "synthetic",
            or_(
                CurrentState.target_room_id == room_id,
                and_(Object.source_kind == "synthetic", Object.room_id == room_id),
            ),
        )
    )


def public_state(state: CurrentState, history: StateHistory | None = None) -> dict:
    return StateResponse.model_validate(state_payload(state, history)).model_dump(mode="json")


def state_payload(state: CurrentState, history: StateHistory | None = None) -> dict:
    row = history or state
    return dict(
        id=str(state.id),
        room_id=str(state.room_id),
        target_kind="room" if state.target_room_id else "object",
        target_id=str(state.target_room_id or state.object_id),
        state_type=state.state_type,
        value=validate_value(state.state_type, row.value),
        version=row.version,
        source_kind=row.source_kind,
        source_observed_at=row.source_observed_at.isoformat() if row.source_observed_at else None,
        committed_at=row.committed_at.isoformat(),
    )


def next_admin_sequence(session: Session, room_id: UUID) -> int:
    # Callers hold the room row lock before allocating a private sequence.
    sequence = session.scalar(
        select(func.coalesce(func.max(Outbox.sequence), 0)).where(
            Outbox.room_id == room_id, Outbox.audience == "admin"
        )
    )
    if sequence >= 2**63 - 1:
        raise StateConflict("Admin sequence exhausted")
    return sequence + 1


def change_state(
    session: Session,
    *,
    room_id: UUID,
    target_kind: str,
    target_id: UUID,
    state_type: str,
    value: dict,
    expected_version: int,
    source_observed_at: datetime | None = None,
    audience: str = "public",
    source_note: str | None = None,
) -> dict:
    # Caller owns transaction; current/history/outbox/cursor roll back together.
    value = validate_value(state_type, value)
    if expected_version < 0 or expected_version > 2**63 - 2:
        raise ValueError("Invalid expected_version")
    if source_observed_at is not None and source_observed_at.utcoffset() is None:
        raise ValueError("Timezone required")
    if (state_type == "room_schedule") != (target_kind == "room") or target_kind not in {
        "room",
        "object",
    }:
        raise ValueError("State type/target mismatch")
    if audience not in {"admin", "public"}:
        raise ValueError("Unknown audience")
    source = "unknown" if audience == "admin" else "synthetic"
    allowed_sources = ("synthetic", "unknown") if audience == "admin" else ("synthetic",)
    visible_room(session, room_id, lock=True)
    if target_kind == "room":
        if target_id != room_id:
            raise StateUnavailable("Wrong room")
        target_filter = CurrentState.target_room_id == target_id
    else:
        obj = session.scalar(
            select(Object)
            .where(
                Object.id == target_id,
                Object.room_id == room_id,
                Object.source_kind.in_(allowed_sources),
            )
            .with_for_update()
        )
        if obj is None:
            raise StateUnavailable("Target unavailable")
        target_filter = CurrentState.object_id == target_id
    state = session.scalar(
        select(CurrentState)
        .where(
            target_filter, CurrentState.state_type == state_type, CurrentState.audience == audience
        )
        .with_for_update()
    )
    if state is not None and state.source_kind != source:
        raise StateUnavailable("Non-synthetic state protected")
    if (state.version if state else 0) != expected_version:
        raise StateConflict("Stale expected_version")
    if audience == "admin":
        if source_observed_at is None:
            raise ValueError("Private observation requires a timestamp")
        if state and state.source_observed_at and source_observed_at <= state.source_observed_at:
            raise StateConflict("Source observation must advance")
        sequence = next_admin_sequence(session, room_id)
    else:
        session.execute(
            insert(RoomStateCursor).values(room_id=room_id, sequence=0).on_conflict_do_nothing()
        )
        cursor = session.scalar(
            select(RoomStateCursor).where(RoomStateCursor.room_id == room_id).with_for_update()
        )
        if cursor.sequence >= 2**63 - 1:
            raise StateConflict("Room sequence exhausted")
        cursor.sequence += 1
        sequence = cursor.sequence
    # Database mutation timestamp, not an assertion about exact WAL commit time.
    timestamp = session.scalar(text("SELECT clock_timestamp()"))
    if state is None:
        state = CurrentState(
            id=uuid4(),
            audience=audience,
            room_id=room_id,
            target_room_id=target_id if target_kind == "room" else None,
            object_id=target_id if target_kind == "object" else None,
            state_type=state_type,
            value=value,
            version=1,
            source_kind=source,
            source_observed_at=source_observed_at,
            committed_at=timestamp,
        )
        session.add(state)
    else:
        changed = session.execute(
            update(CurrentState)
            .where(CurrentState.id == state.id, CurrentState.version == expected_version)
            .values(
                value=value,
                version=expected_version + 1,
                source_observed_at=source_observed_at,
                committed_at=timestamp,
            )
            .returning(CurrentState.id)
        ).scalar_one_or_none()
        if changed is None:
            raise StateConflict("Concurrent update")
        session.refresh(state)
    session.flush()
    payload = public_state(state) if audience == "public" else state_payload(state)
    session.add(
        StateHistory(
            id=uuid4(),
            state_id=state.id,
            source_note=source_note if audience == "admin" else None,
            version=state.version,
            value=value,
            source_kind=source,
            source_observed_at=source_observed_at,
            committed_at=timestamp,
        )
    )
    message_id = uuid4()
    session.add(
        Outbox(
            message_id=message_id,
            room_id=room_id,
            sequence=sequence,
            audience=audience,
            payload={"state": payload}
            if audience == "public"
            else {
                "state_id": str(state.id),
                "version": state.version,
            },
            committed_at=timestamp,
        )
    )
    session.flush()
    return {"state": payload, "message_id": str(message_id), "sequence": sequence}
