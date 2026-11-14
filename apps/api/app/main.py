from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.config import Settings
from app.database.connection import Database
from app.modules.catalog.router import router as catalog_router
from app.modules.realtime.dispatcher import Broker, Dispatcher
from app.modules.realtime.router import router as realtime_router
from app.modules.state.router import router as state_router
from app.modules.status import router


def create_app(
    settings: Settings | None = None,
    database_factory: Callable[[Settings], Database] = Database,
) -> FastAPI:
    config = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.database = database_factory(config)
        app.state.origins = config.origins
        app.state.broker = Broker()
        app.state.dispatcher = Dispatcher(app.state.database.engine, app.state.broker)
        if config.realtime_dispatcher_enabled and config.database_url is not None:
            app.state.dispatcher.start()
        try:
            yield
        finally:
            try:
                await app.state.dispatcher.stop()
            finally:
                app.state.database.close()

    application = FastAPI(title="DATN AIRC Foundation API", version="0.1.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        return JSONResponse(
            {
                "error": {
                    "code": error.detail
                    if isinstance(error.detail, str)
                    and error.detail
                    in {"CATALOG_NOT_FOUND", "INVALID_CURSOR", "DATABASE_UNAVAILABLE"}
                    else "HTTP_ERROR",
                    "message": "Yêu cầu không hợp lệ.",
                }
            },
            status_code=error.status_code,
            headers=error.headers,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "Dữ liệu không hợp lệ."}},
            status_code=422,
        )

    @application.exception_handler(Exception)
    async def internal_error(request: Request, error: Exception):
        return JSONResponse(
            {"error": {"code": "INTERNAL_ERROR", "message": "Lỗi nội bộ."}}, status_code=500
        )

    application.include_router(router)
    application.include_router(catalog_router)
    application.include_router(realtime_router)
    application.include_router(state_router)
    return application
