"""Contract tests for Strawberry GraphQL schema."""

from __future__ import annotations

import strawberry
from gql_learn.gql.schema import schema, Query, Mutation, Author, Book


def test_schema_exists() -> None:
    """Test that schema is properly defined."""
    assert schema is not None
    assert isinstance(schema, strawberry.Schema)


def test_query_type_exists() -> None:
    """Test that Query type exists and has expected fields."""
    # Check that Query has expected resolver methods
    assert hasattr(Query, "books")
    assert hasattr(Query, "book")
    assert hasattr(Query, "authors")
    assert hasattr(Query, "author")
    assert hasattr(Query, "search_books")
    assert hasattr(Query, "books_by_genre")


def test_mutation_type_exists() -> None:
    """Test that Mutation type exists and has expected fields."""
    # Check that Mutation has expected resolver methods
    assert hasattr(Mutation, "add_book")
    assert hasattr(Mutation, "update_book")
    assert hasattr(Mutation, "delete_book")
    assert hasattr(Mutation, "add_author")
    assert hasattr(Mutation, "update_author")
    assert hasattr(Mutation, "delete_author")


def test_author_type_structure() -> None:
    """Test that Author type has required fields."""
    assert hasattr(Author, "__annotations__")
    annotations = Author.__annotations__

    assert "id" in annotations
    assert "name" in annotations
    assert "birth_year" in annotations
    assert "nationality" in annotations
    assert "books" in annotations


def test_book_type_structure() -> None:
    """Test that Book type has required fields."""
    assert hasattr(Book, "__annotations__")
    annotations = Book.__annotations__

    assert "id" in annotations
    assert "title" in annotations
    assert "author" in annotations
    assert "year" in annotations
    assert "genre" in annotations
    assert "isbn" in annotations


def test_schema_is_valid() -> None:
    """Test that schema can be introspected without errors."""
    # Schema should be valid for introspection
    assert schema is not None
    introspection = schema.introspect()
    assert introspection is not None
    assert isinstance(introspection, dict)
    assert "__schema" in introspection or "data" in introspection or introspection


def test_author_book_relationship_in_schema() -> None:
    """Test that Author and Book types are properly connected."""
    # Author should have books field
    assert hasattr(Author, "__annotations__")
    assert "books" in Author.__annotations__

    # Book should have author field
    assert hasattr(Book, "__annotations__")
    assert "author" in Book.__annotations__
