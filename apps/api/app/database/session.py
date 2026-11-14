from collections.abc import Iterator

from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def get_session(request: Request) -> Iterator[Session]:
    engine = request.app.state.database.engine
    if engine is None:
        raise HTTPException(503, detail="DATABASE_UNAVAILABLE")
    try:
        with Session(engine, expire_on_commit=False) as session, session.begin():
            # Enforced by PostgreSQL, in addition to absence of mutation routes.
            session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
    except SQLAlchemyError:
        raise HTTPException(503, detail="DATABASE_UNAVAILABLE") from None
