"""Database session configuration with SQLAlchemy async engine."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from gql_learn.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    future=True,
)

SessionLocal = sessionmaker(  # type: ignore[call-overload]
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with SessionLocal() as session:
        yield session
