import csv
from datetime import UTC, date, datetime, time, timedelta
from io import StringIO
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import func, select

from app.database.visitor_models import SCOPE, VisitorEvent, VisitorSession
from app.modules.admin_auth import DB, Operator
from app.modules.visitor import Local, verify_database

router = APIRouter(prefix="/api/v1/admin/visitor-reports")
MAX_SESSIONS = 200
MAX_EVENTS = 10_000


def base_filter(start: date, until: date):
    if not timedelta(0) < until - start <= timedelta(days=31):
        raise HTTPException(422)
    return (
        VisitorSession.started_at >= datetime.combine(start, time.min, UTC),
        VisitorSession.started_at < datetime.combine(until, time.min, UTC),
        VisitorSession.scope == SCOPE,
    )


def session_fields(session):
    return {
        "session_id": str(session.id),
        "scope": SCOPE,
        "schema_version": session.schema_version,
        "started_at": session.started_at.isoformat(),
        "last_seen_at": session.last_seen_at.isoformat(),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "event_count": session.event_count,
    }


def event_fields(event):
    return {
        "event_id": str(event.id),
        "event_type": event.event_type,
        "room_id": event.room_id,
        "object_id": event.object_id,
        "ordinal": event.ordinal,
        "occurred_at": event.occurred_at.isoformat(),
        "received_at": event.received_at.isoformat(),
    }


@router.get("")
def report(
    _: Local,
    operator: Operator,
    db: DB,
    start: date,
    until: date,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 25,
):
    verify_database(db)
    filters = base_filter(start, until)
    totals = (
        select(
            func.count().label("sessions"),
            func.coalesce(func.sum(VisitorSession.event_count), 0).label("events"),
        )
        .where(*filters)
        .subquery()
    )
    page_ids = (
        select(VisitorSession.id)
        .where(*filters)
        .order_by(VisitorSession.started_at, VisitorSession.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    rows = db.execute(
        select(VisitorSession, totals.c.sessions, totals.c.events)
        .select_from(totals)
        .outerjoin(VisitorSession, VisitorSession.id.in_(page_ids))
        .order_by(VisitorSession.started_at, VisitorSession.id)
    ).all()
    return {
        "scope": SCOPE,
        "sessions": rows[0].sessions,
        "events": rows[0].events,
        "rows": [session_fields(row[0]) for row in rows if row[0] is not None],
        "next_page": page + 1 if page * limit < rows[0].sessions and page < 1000 else None,
    }


@router.post("/export")
def export(
    response: Response,
    _: Local,
    operator: Operator,
    db: DB,
    start: date,
    until: date,
    format: Literal["json", "csv"],
):
    verify_database(db)
    filters = base_filter(start, until)
    session_ids = (
        select(VisitorSession.id)
        .where(*filters)
        .order_by(VisitorSession.started_at, VisitorSession.id)
        .limit(MAX_SESSIONS + 1)
    )
    rows = db.execute(
        select(VisitorSession, VisitorEvent)
        .outerjoin(VisitorEvent, VisitorEvent.session_id == VisitorSession.id)
        .where(VisitorSession.id.in_(session_ids))
        .order_by(VisitorSession.started_at, VisitorSession.id, VisitorEvent.ordinal)
        .limit(MAX_EVENTS + 1)
    ).all()
    sessions = {session.id: session_fields(session) for session, _ in rows}
    if len(sessions) > MAX_SESSIONS or len(rows) > MAX_EVENTS:
        raise HTTPException(413)
    headers = {
        "Cache-Control": "no-store",
        "Content-Disposition": f'attachment; filename="synthetic-local-sessions.{format}"',
        "X-Content-Type-Options": "nosniff",
    }
    if format == "json":
        response.headers.update(headers)
        return {
            "scope": SCOPE,
            "session_count": len(sessions),
            "event_count": sum(session["event_count"] for session in sessions.values()),
            "sessions": list(sessions.values()),
            "events": [
                {"session_id": str(session.id), **event_fields(event)}
                for session, event in rows
                if event is not None
            ],
        }

    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(
        [
            "session_id",
            "scope",
            "schema_version",
            "started_at",
            "last_seen_at",
            "ended_at",
            "event_count",
            "event_id",
            "event_type",
            "room_id",
            "object_id",
            "ordinal",
            "occurred_at",
            "received_at",
        ]
    )
    for session, event in rows:
        # Only server UUIDs, typed timestamps/numbers and fixed contract literals reach CSV.
        fields = sessions[session.id]
        writer.writerow(
            [*fields.values(), *(event_fields(event).values() if event else [None] * 7)]
        )
    return Response(output.getvalue(), media_type="text/csv", headers=headers)
