from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    environment: str = "development"
    database_connection_uri_maria: str | None = None
    database_connection_uri_maria_new: str | None = None
    notion_api_key: str | None = None
    openai_api_key: str | None = None
    authentication_api_key: str | None = None
    sentry_dsn: str | None = None
    evo_send_message_endpoint: str|None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",  extra='allow') # TODO Fazer o mapeamento de todas as variaveis para remover esse parametro 'extra'

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_echo(self) -> bool:
        """Enable SQLAlchemy query logging only in development."""
        return not self.is_production


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of Settings."""
    return Settings()
