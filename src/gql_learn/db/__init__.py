"""Database module with session and model exports."""

from __future__ import annotations

from gql_learn.db.models import Author
from gql_learn.db.models import Base
from gql_learn.db.models import Book
from gql_learn.db.session import SessionLocal
from gql_learn.db.session import engine
from gql_learn.db.session import get_db

__all__ = [
    "Author",
    "Book",
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
]
