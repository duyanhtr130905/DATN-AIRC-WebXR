import pytest

from app.core.config import Settings
from app.modules.catalog import vertical_seed


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://test@remote.invalid/airc_foundation",
        "postgresql+psycopg://test@127.0.0.1/other",
        "postgresql+psycopg://test@127.0.0.1/airc_foundation?host=remote.invalid",
    ],
)
def test_vertical_seed_guard_rejects_before_connect(monkeypatch, url):
    monkeypatch.setattr("sys.argv", ["seed", "--confirm-database", "airc_foundation"])
    monkeypatch.setattr(
        vertical_seed, "Settings", lambda: Settings(_env_file=None, database_url=url)
    )

    def forbidden(_):
        pytest.fail("Database constructor must not run")

    monkeypatch.setattr(vertical_seed, "Database", forbidden)
    with pytest.raises(SystemExit) as error:
        vertical_seed.main()
    assert error.value.code == 2


@pytest.mark.parametrize(
    "target",
    [
        "postgresql+psycopg://test@127.0.0.1/airc_foundation",
        "postgresql+psycopg://test@remote.invalid/airc_test_catalog_" + "a" * 32,
        "postgresql+psycopg://test@127.0.0.1/airc_test_catalog_"
        + "a" * 32
        + "?host=remote.invalid",
    ],
)
def test_db_fault_guard_rejects_non_disposable_scope(monkeypatch, target):
    import database_fault

    monkeypatch.setattr("sys.argv", ["fault", "block", "airc_test_catalog_" + "a" * 32])
    monkeypatch.setenv("DATABASE_URL", target)
    monkeypatch.setenv(
        "TEST_DATABASE_URL", "postgresql+psycopg://test@127.0.0.1/airc_foundation_test"
    )
    monkeypatch.setenv("AIRC_ALLOW_TEST_DATABASES", "1")

    def forbidden(*args, **kwargs):
        pytest.fail("Fault must not open an admin connection")

    monkeypatch.setattr(database_fault, "create_engine", forbidden)
    with pytest.raises(RuntimeError, match="Refusing"):
        database_fault.main()


def test_partial_database_fault_restores_connectivity(monkeypatch):
    from unittest.mock import MagicMock

    import database_fault

    name = "airc_test_catalog_" + "a" * 32
    monkeypatch.setattr("sys.argv", ["fault", "block", name])
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test@127.0.0.1/" + name)
    monkeypatch.setenv(
        "TEST_DATABASE_URL", "postgresql+psycopg://test@127.0.0.1/airc_foundation_test"
    )
    monkeypatch.setenv("AIRC_ALLOW_TEST_DATABASES", "1")
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.scalar.return_value = "airc_foundation_test"
    connection.execute.side_effect = RuntimeError("Injected terminate failure after ALTER")
    monkeypatch.setattr(database_fault, "create_engine", lambda *args, **kwargs: engine)
    with pytest.raises(RuntimeError, match="Injected"):
        database_fault.main()
    statements = [call.args[0] for call in connection.exec_driver_sql.call_args_list]
    assert statements == [
        f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS false',
        f'ALTER DATABASE "{name}" ALLOW_CONNECTIONS true',
    ]
    engine.dispose.assert_called_once()
