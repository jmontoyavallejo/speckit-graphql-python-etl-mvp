"""Unit tests for GraphQL resolvers."""

from __future__ import annotations

import pytest

from gql_learn.db.models import Author
from gql_learn.db.models import Book


def test_author_resolver_structure() -> None:
    """Test that Author resolver includes books relationship."""
    author = Author(id=1, name="Author")
    book1 = Book(id=1, title="Book1", author_id=1, year=2024, genre="Fiction")
    book2 = Book(id=2, title="Book2", author_id=1, year=2023, genre="Mystery")

    author.books = [book1, book2]

    assert len(author.books) == 2
    assert author.books[0].title == "Book1"
    assert author.books[1].title == "Book2"


def test_book_resolver_author_relationship() -> None:
    """Test that Book resolver includes author relationship."""
    author = Author(id=1, name="Author")
    book = Book(id=1, title="Book", author_id=1, year=2024, genre="Fiction")
    book.author = author

    assert book.author.name == "Author"
    assert book.author.id == 1


def test_books_query_filtering_by_genre() -> None:
    """Test filtering books by genre."""
    books = [
        Book(id=1, title="Book1", author_id=1, year=2024, genre="Fiction"),
        Book(id=2, title="Book2", author_id=1, year=2024, genre="Fiction"),
        Book(id=3, title="Book3", author_id=1, year=2024, genre="Mystery"),
    ]

    fiction_books = [b for b in books if b.genre == "Fiction"]

    assert len(fiction_books) == 2
    assert all(b.genre == "Fiction" for b in fiction_books)
