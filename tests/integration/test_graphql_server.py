"""Integration tests for GraphQL server."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGraphQLQueries:
    """Test GraphQL Query operations."""

    async def test_query_all_authors(self, client: AsyncClient, sample_authors) -> None:
        """Test querying all authors."""
        query = """
        query {
            authors {
                id
                name
                birthYear
                nationality
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        authors = data["data"]["authors"]
        assert len(authors) == 3
        assert authors[0]["name"] == "George Orwell"

    async def test_query_single_author(
        self, client: AsyncClient, sample_authors
    ) -> None:
        """Test querying a single author by ID."""
        author_id = str(sample_authors[0].id)
        query = f"""
        query {{
            author(id: "{author_id}") {{
                id
                name
                birthYear
                nationality
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["author"]["name"] == "George Orwell"

    async def test_query_all_books(self, client: AsyncClient, sample_books) -> None:
        """Test querying all books."""
        query = """
        query {
            books {
                id
                title
                year
                genre
                isbn
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        books = data["data"]["books"]
        assert len(books) >= 1
        assert books[0]["title"] == "1984"

    async def test_query_books_with_author_relationship(
        self, client: AsyncClient, sample_books
    ) -> None:
        """Test querying books with nested author information."""
        query = """
        query {
            books {
                id
                title
                author {
                    id
                    name
                }
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        books = data["data"]["books"]
        assert len(books) >= 1
        assert books[0]["author"]["name"] == "George Orwell"

    async def test_query_single_book(
        self, client: AsyncClient, sample_books
    ) -> None:
        """Test querying a single book by ID."""
        book_id = str(sample_books[0].id)
        query = f"""
        query {{
            book(id: "{book_id}") {{
                id
                title
                year
                genre
                isbn
                author {{
                    id
                    name
                }}
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["book"]["title"] == "1984"
        assert data["data"]["book"]["author"]["name"] == "George Orwell"

    async def test_query_author_with_books(
        self, client: AsyncClient, sample_authors
    ) -> None:
        """Test querying author with nested books."""
        author_id = str(sample_authors[0].id)
        query = f"""
        query {{
            author(id: "{author_id}") {{
                id
                name
                books {{
                    id
                    title
                    genre
                }}
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        author = data["data"]["author"]
        assert author["name"] == "George Orwell"
        assert len(author["books"]) == 2

    async def test_query_books_with_limit(
        self, client: AsyncClient, sample_books
    ) -> None:
        """Test querying books with limit parameter."""
        query = """
        query {
            books(limit: 2) {
                id
                title
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        books = data["data"]["books"]
        assert len(books) <= 2


@pytest.mark.asyncio
class TestGraphQLMutations:
    """Test GraphQL Mutation operations."""

    async def test_mutation_add_book(
        self, client: AsyncClient, sample_authors
    ) -> None:
        """Test mutation to add a new book."""
        author_id = str(sample_authors[2].id)
        mutation = f"""
        mutation {{
            addBook(
                title: "I, Robot"
                authorId: "{author_id}"
                year: 1950
                genre: "Science Fiction"
                isbn: "978-0553382563"
            ) {{
                id
                title
                year
                genre
                author {{
                    id
                    name
                }}
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        new_book = data["data"]["addBook"]
        assert new_book["title"] == "I, Robot"
        assert new_book["author"]["name"] == "Isaac Asimov"

    async def test_mutation_update_book(
        self, client: AsyncClient, sample_books
    ) -> None:
        """Test mutation to update an existing book."""
        book_id = str(sample_books[0].id)
        mutation = f"""
        mutation {{
            updateBook(
                id: "{book_id}"
                title: "Nineteen Eighty-Four"
                genre: "Political Fiction"
            ) {{
                id
                title
                genre
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        updated_book = data["data"]["updateBook"]
        assert updated_book["title"] == "Nineteen Eighty-Four"
        assert updated_book["genre"] == "Political Fiction"

    async def test_mutation_delete_book(
        self, client: AsyncClient, sample_books
    ) -> None:
        """Test mutation to delete a book."""
        book_id = str(sample_books[3].id)
        mutation = f"""
        mutation {{
            deleteBook(id: "{book_id}")
        }}
        """
        response = await client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteBook"] is True

        # Verify book is deleted
        query = f"""
        query {{
            book(id: "{book_id}") {{
                id
                title
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": query})
        data = response.json()
        assert data["data"]["book"] is None

    async def test_mutation_add_author(self, client: AsyncClient) -> None:
        """Test mutation to add a new author."""
        mutation = """
        mutation {
            addAuthor(
                name: "Douglas Adams"
                birthYear: 1952
                nationality: "British"
            ) {
                id
                name
                birthYear
                nationality
            }
        }
        """
        response = await client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        new_author = data["data"]["addAuthor"]
        assert new_author["name"] == "Douglas Adams"
        assert new_author["birthYear"] == 1952


@pytest.mark.asyncio
class TestGraphQLErrors:
    """Test GraphQL error handling."""

    async def test_malformed_query(self, client: AsyncClient) -> None:
        """Test that malformed queries return GraphQL errors."""
        query = """
        query {
            books {
                invalidField
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200  # GraphQL returns 200 with errors in body
        data = response.json()
        assert "errors" in data

    async def test_missing_required_field_in_mutation(
        self, client: AsyncClient, sample_authors
    ) -> None:
        """Test that missing required fields in mutation cause errors."""
        author_id = str(sample_authors[0].id)
        mutation = f"""
        mutation {{
            addBook(
                title: "Missing Year"
                authorId: "{author_id}"
                genre: "Fiction"
            ) {{
                id
                title
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": mutation})
        data = response.json()
        assert "errors" in data

    async def test_query_nonexistent_book(self, client: AsyncClient) -> None:
        """Test querying a book that doesn't exist returns None."""
        query = """
        query {
            book(id: "99999") {
                id
                title
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["book"] is None
