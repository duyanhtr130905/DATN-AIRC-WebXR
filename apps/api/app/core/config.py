from urllib.parse import urlsplit

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    database_url: SecretStr | None = None
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    @field_validator("database_url")
    @classmethod
    def validate_database(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            try:
                url = make_url(value.get_secret_value())
                valid = url.drivername == "postgresql+psycopg" and bool(url.host and url.database)
            except Exception:
                valid = False
            if not valid:
                raise ValueError("DATABASE_URL must use postgresql+psycopg with host and database")
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, value: str) -> str:
        for origin in value.split(","):
            parsed = urlsplit(origin.strip())
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.path
                or parsed.query
                or parsed.fragment
                or "*" in origin
            ):
                raise ValueError("CORS_ORIGINS requires explicit http(s) origins without paths")
        return value

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
