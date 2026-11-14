from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.database.connection import Database
from app.main import create_app


def settings(**values):
    return Settings(_env_file=None, database_url=None, **values)


def test_liveness_independent_from_database():
    with TestClient(create_app(settings())) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
        ready = client.get("/api/ready")
        assert ready.status_code == 503
        assert ready.json()["database"] == "not_configured"
        assert client.get("/openapi.json").json()["paths"]["/api/ready"]


@pytest.mark.parametrize("result,code", [("ready", 200), ("unavailable", 503)])
def test_readiness_and_lifecycle_with_injected_probe(result, code):
    database = Mock()
    database.probe.return_value = result
    with TestClient(create_app(settings(), lambda _: database)) as client:
        assert client.get("/api/ready").status_code == code
        database.close.assert_not_called()
    database.close.assert_called_once()


@pytest.mark.parametrize("url", ["sqlite:///demo.db", "postgresql://host/db", "invalid"])
def test_reject_non_postgres_or_wrong_driver(url):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url=url)


@pytest.mark.parametrize("origin", ["*", "https://example.test/path", "null", "https://u:p@x"])
def test_reject_unsafe_cors(origin):
    with pytest.raises(ValidationError):
        settings(cors_origins=origin)


def test_cors_and_safe_error():
    with TestClient(create_app(settings())) as client:
        allowed = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
        assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert "access-control-allow-credentials" not in allowed.headers
        denied = client.get("/api/health", headers={"Origin": "https://untrusted.test"})
        assert "access-control-allow-origin" not in denied.headers
        missing = client.get("/api/missing")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "HTTP_ERROR"


def test_real_connection_failure_and_disposal():
    database = Database(
        Settings(_env_file=None, database_url="postgresql+psycopg://test@127.0.0.1:1/airc_test")
    )
    assert database.probe() == "unavailable"
    assert database.engine.pool.checkedout() == 0
    database.close()


def test_unexpected_error_is_redacted():
    database = Mock()
    database.probe.side_effect = RuntimeError("private-detail")
    with TestClient(
        create_app(settings(), lambda _: database), raise_server_exceptions=False
    ) as client:
        response = client.get("/api/ready")
        assert response.status_code == 500
        assert "private-detail" not in response.text
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


def test_config_validation_redacts_input_credentials():
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, database_url="postgresql://user:private-test-value@host/db")
    assert "private-test-value" not in str(error.value)
