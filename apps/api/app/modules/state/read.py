from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.state_models import CurrentState, Outbox, RoomStateCursor, StateHistory
from app.modules.state.service import StateUnavailable, public_state, visible_room, visible_states


def snapshot(engine, room_id: UUID) -> dict:
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin(), Session(bind=connection) as session:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            visible_room(session, room_id)
            cursor = session.get(RoomStateCursor, room_id)
            rows = list(
                session.scalars(visible_states(room_id).order_by(CurrentState.id).limit(33))
            )
            if len(rows) > 32:
                raise StateUnavailable("Snapshot capacity exceeded")
            return {
                "type": "snapshot",
                "schema_version": 1,
                "message_id": str(uuid4()),
                "room_id": str(room_id),
                "sequence": cursor.sequence if cursor else 0,
                "states": [public_state(row) for row in rows],
            }


def replay(engine, room_id: UUID, after: int) -> tuple[list[dict], bool]:
    with Session(engine) as session, session.begin():
        visible_room(session, room_id)
        # Durable cursor reads include published rows; notification is only a wake-up hint.
        rows = list(
            session.scalars(
                select(Outbox)
                .where(
                    Outbox.room_id == room_id,
                    Outbox.sequence > after,
                    Outbox.published_at.is_not(None),
                )
                .order_by(Outbox.sequence)
                .limit(33)
            )
        )
        result = []
        for row in rows[:32]:
            state_id = UUID(row.payload["state"]["id"])
            state = session.scalar(visible_states(room_id).where(CurrentState.id == state_id))
            if state is None:
                raise StateUnavailable("Target no longer visible")
            from app.modules.state.schemas import StateResponse

            safe = StateResponse.model_validate(row.payload["state"]).model_dump(mode="json")
            if safe["room_id"] != str(room_id) or safe["id"] != str(state.id):
                raise StateUnavailable("Invalid durable payload scope")
            result.append(
                {
                    "type": "state.updated",
                    "schema_version": 1,
                    "message_id": str(row.message_id),
                    "room_id": str(room_id),
                    "sequence": row.sequence,
                    "published_at": row.published_at.isoformat(),
                    "state": safe,
                }
            )
        pending = session.scalar(
            select(Outbox)
            .where(
                Outbox.room_id == room_id, Outbox.sequence > after, Outbox.published_at.is_(None)
            )
            .order_by(Outbox.sequence)
            .limit(1)
        )
        now = session.scalar(select(func.clock_timestamp()))
        stalled = pending is not None and now - pending.committed_at > timedelta(seconds=2)
        return result, len(rows) > 32 or stalled


def history_rows(session: Session, room_id: UUID, state: CurrentState, after: int, limit: int):
    return list(
        session.scalars(
            select(StateHistory)
            .join(CurrentState, CurrentState.id == StateHistory.state_id)
            .where(
                StateHistory.state_id == state.id,
                StateHistory.source_kind == "synthetic",
                StateHistory.version > after,
                CurrentState.id.in_(visible_states(room_id).with_only_columns(CurrentState.id)),
            )
            .order_by(StateHistory.version)
            .limit(limit + 1)
        )
    )
