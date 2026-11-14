import json
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

StateType = Literal["room_schedule", "equipment_status", "exhibit_info"]


class EquipmentValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["available", "maintenance", "offline"]


class ScheduleValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(min_length=1, max_length=160)
    status: Literal["free", "occupied", "closed"]


class ExhibitValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=160)
    text: str = Field(max_length=800)


def validate_value(state_type: str, value: dict) -> dict:
    models = {
        "equipment_status": EquipmentValue,
        "room_schedule": ScheduleValue,
        "exhibit_info": ExhibitValue,
    }
    if state_type not in models:
        raise ValueError("Invalid state type")
    result = models[state_type].model_validate(value).model_dump()
    if len(json.dumps(result, ensure_ascii=False).encode()) > 4096:
        raise ValueError("State value too large")
    return result


class StateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    room_id: UUID
    target_kind: Literal["room", "object"]
    target_id: UUID
    state_type: StateType
    value: dict
    version: int = Field(ge=1)
    source_kind: Literal["synthetic"]
    source_observed_at: AwareDatetime | None
    committed_at: AwareDatetime

    @model_validator(mode="after")
    def validate_public(self):
        self.value = validate_value(self.state_type, self.value)
        if (self.state_type == "room_schedule") != (self.target_kind == "room"):
            raise ValueError("Invalid target type")
        return self


class StatePageMeta(BaseModel):
    schema_version: Literal[1] = 1
    next_cursor: str | None = None


class StatesPage(BaseModel):
    data: list[StateResponse]
    meta: StatePageMeta


class HistoryMeta(BaseModel):
    schema_version: Literal[1] = 1
    next_after_version: int | None = None


class HistoryPage(BaseModel):
    data: list[StateResponse]
    meta: HistoryMeta
