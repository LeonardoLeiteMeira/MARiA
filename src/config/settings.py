from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    environment: str = "development"
    database_connection_uri_maria: str | None = None
    database_connection_uri_maria_async: str | None = None
    notion_client_id: str | None = None
    notion_client_secret: str | None = None
    notion_redirect_uri: str | None = None
    openai_api_key: str | None = None
    authentication_api_key: str | None = None
    sentry_dsn: str | None = None
    evo_send_message_endpoint: str | None = None

    pluggy_client_id: str | None = None
    pluggy_client_secret: str | None = None
    timezone: str = "America/Sao_Paulo"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_echo(self) -> bool:
        return not self.is_production


@lru_cache()
def get_settings() -> Settings:
    return Settings()
