"""Contract tests for Strawberry GraphQL schema."""

from __future__ import annotations

import pytest

from gql_learn.db.models import Author
from gql_learn.db.models import Book


def test_author_type_structure() -> None:
    """Test that Author type has required fields."""
    author = Author(id=1, name="Test Author", birth_year=1900, nationality="American")

    assert author.id == 1
    assert author.name == "Test Author"
    assert author.birth_year == 1900
    assert author.nationality == "American"


def test_book_type_structure() -> None:
    """Test that Book type has required fields."""
    author = Author(id=1, name="Test Author")
    book = Book(
        id=1,
        title="Test Book",
        author_id=1,
        year=2024,
        genre="Fiction",
        isbn="123456789",
    )

    assert book.id == 1
    assert book.title == "Test Book"
    assert book.author_id == 1
    assert book.year == 2024
    assert book.genre == "Fiction"
    assert book.isbn == "123456789"


def test_author_book_relationship() -> None:
    """Test that Author can have multiple books."""
    author = Author(id=1, name="Author")

    book1 = Book(id=1, title="Book1", author_id=1, year=2024, genre="Fiction")
    book2 = Book(id=2, title="Book2", author_id=1, year=2023, genre="Mystery")

    assert book1.author_id == author.id
    assert book2.author_id == author.id
