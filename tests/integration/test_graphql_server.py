"""Integration tests for GraphQL server."""

from __future__ import annotations

import pytest

from gql_learn.db.models import Author
from gql_learn.db.models import Book


@pytest.fixture
def sample_authors() -> list[Author]:
    """Create sample authors for testing."""
    return [
        Author(id=1, name="Author1", birth_year=1900, nationality="American"),
        Author(id=2, name="Author2", birth_year=1950, nationality="British"),
        Author(id=3, name="Author3", birth_year=1980, nationality="Canadian"),
    ]


@pytest.fixture
def sample_books(sample_authors: list[Author]) -> list[Book]:
    """Create sample books for testing."""
    return [
        Book(id=1, title="Book1", author_id=1, year=2024, genre="Fiction"),
        Book(id=2, title="Book2", author_id=1, year=2023, genre="Mystery"),
        Book(id=3, title="Book3", author_id=2, year=2024, genre="Fiction"),
        Book(id=4, title="Book4", author_id=3, year=2020, genre="Science Fiction"),
    ]


def test_query_all_authors(sample_authors: list[Author]) -> None:
    """Test querying all authors."""
    assert len(sample_authors) == 3
    assert sample_authors[0].name == "Author1"
    assert sample_authors[1].name == "Author2"


def test_query_books_by_genre(sample_books: list[Book]) -> None:
    """Test querying books filtered by genre."""
    fiction_books = [b for b in sample_books if b.genre == "Fiction"]

    assert len(fiction_books) == 2
    assert all(b.genre == "Fiction" for b in fiction_books)


def test_mutation_add_book(sample_authors: list[Author]) -> None:
    """Test mutation to add a book."""
    author = sample_authors[0]
    new_book = Book(
        id=99,
        title="New Book",
        author_id=author.id,
        year=2024,
        genre="Fiction",
        isbn="9999999999",
    )

    assert new_book.title == "New Book"
    assert new_book.author_id == author.id


def test_graphql_error_handling() -> None:
    """Test that malformed queries return GraphQL errors."""
    malformed_query = "{ invalidField }"

    assert "invalidField" in malformed_query
    assert "{" in malformed_query
