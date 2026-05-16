"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import asyncio
import os
import sys
from typing import AsyncGenerator

# Set test database URL BEFORE importing any gql_learn modules
# Use file-based database for testing to ensure proper isolation
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_db.sqlite"

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Now import gql_learn modules with test database configured
from gql_learn.api.app import create_app
from gql_learn.db.models import Base
from gql_learn.db.session import get_db


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_engine():
    """Create test database engine."""
    # Use same database as the app
    from gql_learn.db.session import engine as app_engine

    # Create tables
    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield app_engine


@pytest_asyncio.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def db_session_override(test_db_session: AsyncSession):
    """Override get_db dependency."""

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    return get_test_db


@pytest_asyncio.fixture
async def app(db_session_override):
    """Create FastAPI test app with overridden database."""
    app = create_app()
    app.dependency_overrides[get_db] = db_session_override
    return app


@pytest_asyncio.fixture
async def client(app):
    """Create async HTTP client for testing."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def sample_authors(test_db_session: AsyncSession):
    """Create sample authors in test database."""
    from gql_learn.db.models import Author

    authors = [
        Author(name="George Orwell", birth_year=1903, nationality="British"),
        Author(name="J.K. Rowling", birth_year=1965, nationality="British"),
        Author(name="Isaac Asimov", birth_year=1920, nationality="American"),
    ]
    for author in authors:
        test_db_session.add(author)
    await test_db_session.commit()
    for author in authors:
        await test_db_session.refresh(author)
    return authors


@pytest_asyncio.fixture
async def sample_books(
    test_db_session: AsyncSession, sample_authors
) -> list:
    """Create sample books in test database."""
    from gql_learn.db.models import Book

    books = [
        Book(
            title="1984",
            author_id=sample_authors[0].id,
            year=1949,
            genre="Dystopian",
            isbn="978-0451524935",
        ),
        Book(
            title="Animal Farm",
            author_id=sample_authors[0].id,
            year=1945,
            genre="Satire",
            isbn="978-0451526342",
        ),
        Book(
            title="Harry Potter and the Philosopher's Stone",
            author_id=sample_authors[1].id,
            year=1997,
            genre="Fantasy",
            isbn="978-0747532699",
        ),
        Book(
            title="Foundation",
            author_id=sample_authors[2].id,
            year=1951,
            genre="Science Fiction",
            isbn="978-0553382563",
        ),
    ]
    for book in books:
        test_db_session.add(book)
    await test_db_session.commit()
    for book in books:
        await test_db_session.refresh(book)
    return books
