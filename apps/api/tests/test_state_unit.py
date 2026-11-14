import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app
from app.modules.realtime.client_rules import sequence_action
from app.modules.realtime.dispatcher import Broker
from app.modules.state.schemas import validate_value


@pytest.mark.parametrize(
    "kind,value",
    [
        ("equipment_status", {"status": "invented"}),
        ("equipment_status", {"status": "available", "private": "x"}),
        ("room_schedule", {"status": "free"}),
        ("exhibit_info", {"title": "", "text": "x"}),
        ("invalid", {}),
    ],
)
def test_reject_invalid_value(kind, value):
    with pytest.raises((ValidationError, ValueError)):
        validate_value(kind, value)


def test_three_baseline_values_and_old_duplicate_gap_rules():
    assert validate_value("equipment_status", {"status": "maintenance"})["status"] == "maintenance"
    assert (
        validate_value("room_schedule", {"status": "free", "activity": "DEMO"})["activity"]
        == "DEMO"
    )
    assert validate_value("exhibit_info", {"title": "DEMO", "text": "Synthetic"})["title"] == "DEMO"
    assert sequence_action(4, 3) == "ignore"
    assert sequence_action(4, 4) == "ignore"
    assert sequence_action(4, 5) == "apply"
    assert sequence_action(4, 6) == "resync"


def test_broker_bounds_and_slow_queue_no_unbounded_memory():
    async def check():
        from uuid import uuid4

        broker = Broker()
        room = uuid4()
        sub = broker.subscribe(room)
        for _ in range(20):
            await broker.notify(room)
        assert sub.overflow and sub.queue.qsize() == 8
        for _ in range(31):
            broker.subscribe(room)
        with pytest.raises(ValueError):
            broker.subscribe(room)

    asyncio.run(check())


def test_pool_disposed_even_if_dispatcher_stop_fails():
    database = Mock()
    application = create_app(Settings(_env_file=None, database_url=None), lambda _: database)
    with patch("app.main.Dispatcher.stop", new=AsyncMock(side_effect=RuntimeError("fault"))):
        with pytest.raises(RuntimeError, match="fault"):
            with TestClient(application):
                pass
    database.close.assert_called_once()


def test_state_cli_rejects_url_override_before_database(monkeypatch):
    from app.modules.state import cli

    monkeypatch.setattr(
        "sys.argv",
        [
            "cli",
            "--confirm-database",
            "airc_foundation",
            "--room-id",
            "10000000-0000-4000-8000-000000000001",
            "--target-kind",
            "room",
            "--target-id",
            "10000000-0000-4000-8000-000000000001",
            "--state-type",
            "room_schedule",
            "--expected-version",
            "0",
            "--value",
            '{"status":"free","activity":"DEMO"}',
        ],
    )
    monkeypatch.setattr(
        cli,
        "Settings",
        lambda: Settings(
            _env_file=None,
            database_url="postgresql+psycopg://test@127.0.0.1/airc_foundation?host=example.invalid",
        ),
    )
    database = Mock()
    monkeypatch.setattr(cli, "Database", database)
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    database.assert_not_called()
