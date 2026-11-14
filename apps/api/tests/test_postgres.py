import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import Settings
from app.database.connection import Database
from app.main import create_app


@pytest.mark.postgres
def test_isolated_postgres_readiness_and_pool_return():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail("TEST_DATABASE_URL is required for PostgreSQL integration; do not claim PASS")
    settings = Settings(_env_file=None, database_url=url, realtime_dispatcher_enabled=False)
    database = Database(settings)
    try:
        assert database.probe() == "ready"
        with database.engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version()")).scalar_one().startswith("PostgreSQL")
            )
        assert database.engine.pool.checkedout() == 0
        with TestClient(create_app(settings)) as client:
            result = client.get("/api/ready")
            assert result.status_code == 200
            assert result.json()["database"] == "ready"
            assert client.app.state.database.engine.pool.checkedout() == 0
    finally:
        database.close()
