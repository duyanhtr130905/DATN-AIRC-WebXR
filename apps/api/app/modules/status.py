from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["status"])


class HealthResponse(BaseModel):
    status: Literal["alive"]
    service: Literal["airc-api"]
    timestamp: datetime


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    database: Literal["ready", "unavailable", "not_configured"]
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="alive", service="airc-api", timestamp=datetime.now(UTC))


@router.get("/ready", response_model=ReadyResponse, responses={503: {"model": ReadyResponse}})
def ready(request: Request) -> JSONResponse:
    database = request.app.state.database.probe()
    result = ReadyResponse(
        status="ready" if database == "ready" else "not_ready",
        database=database,
        timestamp=datetime.now(UTC),
    )
    return JSONResponse(
        result.model_dump(mode="json"), status_code=200 if database == "ready" else 503
    )
