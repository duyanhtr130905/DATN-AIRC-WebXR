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
