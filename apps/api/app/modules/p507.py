"""Provisional R4 Catalog mapping and synthetic-only ingest."""

import hashlib
import json
import re
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.database.models import Object, Room
from app.database.state_models import CurrentState
from app.modules.state.schemas import StateType, validate_value
from app.modules.state.service import StateConflict, change_state, public_state

ROOT = Path(__file__).resolve().parents[4]
REVISION = "p507-r4-synthetic-v1"
ROOM_ID = uuid5(NAMESPACE_URL, "airc-webxr/synthetic/room/P507")
LABEL = "PROVISIONAL / SYNTHETIC"
UNPLACED = frozenset({"P507-CHAIR-C-09", "P507-CHAIR-C-10"})


def object_id(logical_id: str):
    return uuid5(NAMESPACE_URL, f"airc-webxr/synthetic/room/P507/object/{logical_id}")


def evidence():
    root = ROOT / "experiments/p507-webxr"
    lock = json.loads((root / "asset-lock.json").read_bytes())
    reference = json.loads((root / "export-bounds-v1.json").read_bytes())
    model = lock["files"]["P507_G1_G2_PROVISIONAL.glb"]
    if (reference["model_sha256"], reference["model_bytes"]) != (model["sha256"], model["bytes"]):
        raise ValueError("Frozen asset identity mismatch")
    ids = [row["id"] for row in reference["records"]]
    if len(ids) != 121 or len(set(ids)) != 121 or UNPLACED.intersection(ids):
        raise ValueError("Invalid placed logical IDs")
    return lock, ids


def validate_mapping(session: Session, *, seed: bool = False):
    lock, ids = evidence()
    mappings = {key: object_id(key) for key in ids}
    ref = f"{REVISION}:sha256:{lock['files']['asset-manifest.json']['sha256']}"
    # Serialize fixture and state writes using the same room row lock as M1.
    session.execute(text("SELECT pg_advisory_xact_lock(817405507)"))
    rooms = session.scalars(
        select(Room).where(or_(Room.id == ROOM_ID, Room.code == "DEMO-P507")).with_for_update()
    ).all()
    if not rooms and seed:
        session.add(
            Room(
                id=ROOM_ID,
                code="DEMO-P507",
                name="P507 synthetic",
                source_kind="synthetic",
                evidence_ref=ref,
                metadata_json={"label": LABEL},
            )
        )
        session.flush()
    elif len(rooms) != 1 or (
        rooms[0].id,
        rooms[0].code,
        rooms[0].source_kind,
        rooms[0].evidence_ref,
    ) != (ROOM_ID, "DEMO-P507", "synthetic", ref):
        raise ValueError("P507 room mapping conflict")
    rows = session.scalars(
        select(Object)
        .where(
            or_(
                Object.room_id == ROOM_ID,
                Object.id.in_(mappings.values()),
                Object.external_reference.in_(set(ids) | UNPLACED),
            )
        )
        .order_by(Object.id)
        .with_for_update()
    ).all()
    seen = set()
    for row in rows:
        key = row.external_reference
        if (
            key not in mappings
            or key in seen
            or row.id != mappings[key]
            or row.room_id != ROOM_ID
            or row.source_kind != "synthetic"
            or row.evidence_ref != ref
        ):
            raise ValueError("P507 object mapping conflict")
        seen.add(key)
    missing = mappings.keys() - seen
    if missing and not seed:
        raise ValueError("P507 mapping incomplete")
    session.add_all(
        Object(
            id=mappings[key],
            room_id=ROOM_ID,
            name=key,
            type="p507_fixture",
            source_kind="synthetic",
            external_reference=key,
            evidence_ref=ref,
            metadata_json={"label": key, "description": ref},
        )
        for key in sorted(missing)
    )
    session.flush()
    return mappings


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    logical_id: str | None = Field(max_length=64)
    state_type: StateType
    expected_version: int = Field(strict=True, ge=0, le=2**63 - 2)
    observed_at: AwareDatetime
    value: dict

    @field_validator("observed_at", mode="before")
    @classmethod
    def require_source_timestamp(cls, value):
        if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value
        ):
            raise ValueError("Explicit ISO 8601 source timestamp with timezone required")
        return value


def parse_observation(raw: bytes) -> Observation:
    if len(raw) > 8192:
        raise ValueError("Observation exceeds size budget")
    return Observation.model_validate_json(raw)


def ingest(session: Session, observation: Observation, *, authorization: str | None):
    if authorization != REVISION:
        raise PermissionError("Synthetic fixture authorization required")
    value = validate_value(observation.state_type, observation.value)
    is_room = observation.state_type == "room_schedule"
    if is_room != (observation.logical_id is None):
        raise ValueError("State type/target mismatch")
    mapping = validate_mapping(session)
    if not is_room and observation.logical_id not in mapping:
        raise ValueError("Unknown or unplaced logical ID")
    target = ROOM_ID if is_room else mapping[observation.logical_id]
    column = CurrentState.target_room_id if is_room else CurrentState.object_id
    current = session.scalar(
        select(CurrentState)
        .where(
            column == target,
            CurrentState.state_type == observation.state_type,
        )
        .with_for_update()
    )
    if current is not None:
        if current.source_kind != "synthetic":
            raise PermissionError("Non-synthetic state protected")
        observed = current.source_observed_at
        if (
            current.version == observation.expected_version + 1
            and observed == observation.observed_at
            and current.value == value
        ):
            return {"state": public_state(current), "replayed": True}
        if observed is not None and observation.observed_at <= observed:
            raise StateConflict("Source observation must advance")
    return change_state(
        session,
        room_id=ROOM_ID,
        target_kind="room" if is_room else "object",
        target_id=target,
        state_type=observation.state_type,
        value=value,
        expected_version=observation.expected_version,
        source_observed_at=observation.observed_at,
    )


def verify_manifest(raw: bytes, lock: dict, ids: list[str]):
    expected = lock["files"]["asset-manifest.json"]
    if len(raw) != expected["bytes"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
        raise ValueError("Frozen manifest hash/size mismatch")
    rows = json.loads(raw)["instances"]
    placed = [row["id"] for row in rows if row["status"] != "UNPLACED"]
    unplaced = [row["id"] for row in rows if row["status"] == "UNPLACED"]
    if (
        len(placed) != len(ids)
        or set(placed) != set(ids)
        or len(unplaced) != 2
        or set(unplaced) != UNPLACED
    ):
        raise ValueError("Frozen manifest placed/unplaced mismatch")
