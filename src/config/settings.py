from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"

    postgres_db: str | None = None
    postgres_host: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_port: str | None = None

    notion_client_id: str | None = None
    notion_client_secret: str | None = None
    notion_redirect_uri: str | None = None

    openai_api_key: str | None = None

    sentry_dsn: str | None = None

    evo_authentication_api_key: str | None = None
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

    @property
    def database_connection_uri_maria_async(self) -> str | None:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def database_connection_uri_maria(self) -> str | None:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
