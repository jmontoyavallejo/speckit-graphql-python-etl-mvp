"""Application configuration using Pydantic."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    database_url: str = "postgresql://gql_learn:learner123@localhost:5432/gql_learn"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    debug: bool = False
    environment: str = "development"
    graphql_playground: bool = True
    reload: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
