"""Loopback-only operator authentication; no public registration."""

import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.admin_models import AdminAccount, AdminAudit, AdminSession

router = APIRouter(prefix="/api/v1/admin")
LOOPBACK = {"localhost", "127.0.0.1", "::1"}
COOKIE = "airc_admin"
LIFETIME = 8 * 60 * 60
TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")
USERNAME = re.compile(r"[a-z0-9][a-z0-9_.-]{2,63}")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = secrets.token_bytes(16) if salt is None else salt
    key = hashlib.scrypt(password.encode(), salt=salt, n=2**17, r=8, p=1, maxmem=256 * 1024 * 1024)
    return f"scrypt:{salt.hex()}:{key.hex()}"


def allowed(connection, *, check_origin: bool) -> bool:
    config = connection.app.state.admin_config
    if not config.admin_enabled or not connection.client or connection.client.host not in LOOPBACK:
        return False
    if connection.url.hostname not in LOOPBACK:
        return False
    origin = connection.headers.get("origin")
    if check_origin and origin != config.admin_origin:
        return False
    if origin and origin != config.admin_origin:
        return False
    expected = urlsplit(config.admin_origin).scheme
    scheme = {"ws": "http", "wss": "https"}.get(connection.url.scheme, connection.url.scheme)
    return scheme == expected


def admin_db(request: Request, response: Response):
    if not allowed(request, check_origin=request.method != "GET"):
        raise HTTPException(403)
    response.headers["Cache-Control"] = "no-store"
    engine = request.app.state.database.engine
    if engine is None:
        raise HTTPException(503)
    try:
        with Session(engine, expire_on_commit=False) as db, db.begin():
            yield db
    except SQLAlchemyError:
        raise HTTPException(503) from None


DB = Annotated[Session, Depends(admin_db, scope="function")]


def auth(db: Session, token: str | None):
    if not token or not TOKEN.fullmatch(token):
        return None
    return db.scalar(
        select(AdminAccount)
        .join(AdminSession)
        .where(
            AdminSession.digest == digest(token),
            AdminSession.expires_at > func.now(),
            AdminAccount.active.is_(True),
        )
    )


def operator(request: Request, db: DB):
    token = request.cookies.get(COOKIE)
    account = auth(db, token)
    if account is None:
        raise HTTPException(401)
    if request.method != "GET" and not hmac.compare_digest(
        request.headers.get("x-admin-csrf", "").encode(), digest("csrf:" + token).encode()
    ):
        raise HTTPException(403)
    return account


Operator = Annotated[AdminAccount, Depends(operator)]


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


@router.post("/login")
def login(body: Login, request: Request, response: Response, db: DB):
    # One local operator, globally serialized per database, even across workers.
    if not db.scalar(text("SELECT pg_try_advisory_xact_lock(817405508)")):
        response.status_code = 429
        return {"error": "LOGIN_BUSY"}
    now = datetime.now(UTC)
    failures = db.scalar(
        select(func.count())
        .select_from(AdminAudit)
        .where(
            AdminAudit.operation == "login",
            AdminAudit.outcome == "denied",
            AdminAudit.recorded_at >= now - timedelta(minutes=1),
        )
    )
    if failures >= 5:
        response.status_code = 429
        return {"error": "LOGIN_THROTTLED"}
    username = body.username.strip().lower()
    account = db.scalar(select(AdminAccount).where(AdminAccount.username == username))
    valid = account is not None and account.active
    encoded = account.password_hash if valid else "scrypt:" + "00" * 16 + ":" + "00" * 64
    candidate = hash_password(body.password, bytes.fromhex(encoded.split(":")[1]))
    if not valid or not hmac.compare_digest(candidate, encoded):
        db.add(AdminAudit(operation="login", outcome="denied"))
        response.status_code = 401
        return {"error": "INVALID_CREDENTIALS"}
    token = secrets.token_urlsafe(32)
    db.execute(
        delete(AdminSession).where(
            (AdminSession.account_id == account.id) | (AdminSession.expires_at <= now)
        )
    )
    db.add(
        AdminSession(
            digest=digest(token),
            account_id=account.id,
            expires_at=now + timedelta(seconds=LIFETIME),
        )
    )
    db.add(AdminAudit(account_id=account.id, operation="login", outcome="success"))
    response.set_cookie(
        COOKIE,
        token,
        max_age=LIFETIME,
        path="/",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
    )
    return {"username": account.username, "csrf": digest("csrf:" + token)}


@router.get("/session")
def session_info(request: Request, account: Operator):
    return {"username": account.username, "csrf": digest("csrf:" + request.cookies[COOKIE])}


@router.post("/logout")
def logout(request: Request, response: Response, db: DB, account: Operator):
    db.execute(delete(AdminSession).where(AdminSession.digest == digest(request.cookies[COOKIE])))
    db.add(AdminAudit(account_id=account.id, operation="logout", outcome="success"))
    response.delete_cookie(
        COOKIE, path="/", httponly=True, secure=request.url.scheme == "https", samesite="strict"
    )
    return {"signed_out": True}
