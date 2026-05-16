"""Application configuration using Pydantic."""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    database_url: str = "postgresql://gql_learn:learner123@localhost:5432/gql_learn"
    host: str = "127.0.0.1"
    port: int = 8000
    graphql_endpoint: str = "http://localhost:8000/graphql"
    log_level: str = "INFO"
    debug: bool = False
    environment: str = "development"
    graphql_playground: bool = True
    reload: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def setup_logging() -> None:
    """Configure logging for the application."""
    log_dir = Path.home() / ".gql-learn"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {settings.log_level}, File: {log_file}")

