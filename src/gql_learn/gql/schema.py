"""Strawberry GraphQL schema definition."""

from __future__ import annotations

from typing import TYPE_CHECKING

import strawberry
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from gql_learn.db.models import Author as AuthorModel
from gql_learn.db.models import Book as BookModel
from gql_learn.gql.context import GraphQLContext


def _author_to_strawberry(author: AuthorModel) -> Author:
    """Convert ORM Author to Strawberry Author type."""
    return Author(
        id=strawberry.ID(str(author.id)),
        name=author.name,
        birth_year=author.birth_year,
        nationality=author.nationality,
        books=[_book_to_strawberry(book) for book in author.books],
    )


def _book_to_strawberry(book: BookModel) -> Book:
    """Convert ORM Book to Strawberry Book type."""
    author = None
    if book.author:
        author = _author_to_strawberry(book.author)
    return Book(
        id=strawberry.ID(str(book.id)),
        title=book.title,
        author_id=strawberry.ID(str(book.author_id)),
        year=book.year,
        genre=book.genre,
        isbn=book.isbn,
        author=author,
    )


@strawberry.type
class Author:
    """Author type for GraphQL."""

    id: strawberry.ID
    name: str
    birth_year: int | None = None
    nationality: str | None = None
    books: list[Book] = strawberry.field(default_factory=list)


@strawberry.type
class Book:
    """Book type for GraphQL."""

    id: strawberry.ID
    title: str
    author_id: strawberry.ID
    year: int
    genre: str
    isbn: str | None = None
    author: Author | None = None


@strawberry.type
class Query:
    """GraphQL Query root type."""

    @strawberry.field
    async def books(
        self, info: strawberry.types.Info[GraphQLContext], limit: int = 10
    ) -> list[Book]:
        """Get all books with optional limit."""
        session: AsyncSession = info.context.session
        stmt = select(BookModel).limit(limit)
        result = await session.scalars(stmt)
        books = result.all()
        return [_book_to_strawberry(book) for book in books]

    @strawberry.field
    async def book(
        self, info: strawberry.types.Info[GraphQLContext], id: strawberry.ID
    ) -> Book | None:
        """Get a single book by ID."""
        session: AsyncSession = info.context.session
        book = await session.get(BookModel, int(id))
        if book is None:
            return None
        await session.refresh(book, ["author"])
        return _book_to_strawberry(book)

    @strawberry.field
    async def authors(
        self, info: strawberry.types.Info[GraphQLContext]
    ) -> list[Author]:
        """Get all authors."""
        session: AsyncSession = info.context.session
        stmt = select(AuthorModel)
        result = await session.scalars(stmt)
        authors = result.all()
        return [_author_to_strawberry(author) for author in authors]

    @strawberry.field
    async def author(
        self, info: strawberry.types.Info[GraphQLContext], id: strawberry.ID
    ) -> Author | None:
        """Get a single author by ID."""
        session: AsyncSession = info.context.session
        author = await session.get(AuthorModel, int(id))
        if author is None:
            return None
        await session.refresh(author, ["books"])
        return _author_to_strawberry(author)

    @strawberry.field
    async def search_books(
        self, info: strawberry.types.Info[GraphQLContext], title: str
    ) -> list[Book]:
        """Search books by title (case-insensitive)."""
        session: AsyncSession = info.context.session
        stmt = select(BookModel).where(
            BookModel.title.ilike(f"%{title}%")
        )
        result = await session.scalars(stmt)
        books = result.all()
        return [_book_to_strawberry(book) for book in books]

    @strawberry.field
    async def books_by_genre(
        self, info: strawberry.types.Info[GraphQLContext], genre: str
    ) -> list[Book]:
        """Get books by genre."""
        session: AsyncSession = info.context.session
        stmt = select(BookModel).where(BookModel.genre == genre)
        result = await session.scalars(stmt)
        books = result.all()
        return [_book_to_strawberry(book) for book in books]


@strawberry.type
class Mutation:
    """GraphQL Mutation root type."""

    @strawberry.mutation
    async def add_book(
        self,
        info: strawberry.types.Info[GraphQLContext],
        title: str,
        author_id: strawberry.ID,
        year: int,
        genre: str,
        isbn: str | None = None,
    ) -> Book:
        """Add a new book."""
        session: AsyncSession = info.context.session
        book = BookModel(
            title=title,
            author_id=int(author_id),
            year=year,
            genre=genre,
            isbn=isbn,
        )
        session.add(book)
        await session.commit()
        await session.refresh(book, ["author"])
        return _book_to_strawberry(book)

    @strawberry.mutation
    async def update_book(
        self,
        info: strawberry.types.Info[GraphQLContext],
        id: strawberry.ID,
        title: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> Book | None:
        """Update an existing book."""
        session: AsyncSession = info.context.session
        book = await session.get(BookModel, int(id))
        if book is None:
            return None
        if title is not None:
            book.title = title
        if year is not None:
            book.year = year
        if genre is not None:
            book.genre = genre
        await session.commit()
        await session.refresh(book, ["author"])
        return _book_to_strawberry(book)

    @strawberry.mutation
    async def delete_book(
        self, info: strawberry.types.Info[GraphQLContext], id: strawberry.ID
    ) -> bool:
        """Delete a book by ID."""
        session: AsyncSession = info.context.session
        book = await session.get(BookModel, int(id))
        if book is None:
            return False
        await session.delete(book)
        await session.commit()
        return True

    @strawberry.mutation
    async def add_author(
        self,
        info: strawberry.types.Info[GraphQLContext],
        name: str,
        birth_year: int | None = None,
        nationality: str | None = None,
    ) -> Author:
        """Add a new author."""
        session: AsyncSession = info.context.session
        author = AuthorModel(
            name=name,
            birth_year=birth_year,
            nationality=nationality,
        )
        session.add(author)
        await session.commit()
        await session.refresh(author, ["books"])
        return _author_to_strawberry(author)

    @strawberry.mutation
    async def update_author(
        self,
        info: strawberry.types.Info[GraphQLContext],
        id: strawberry.ID,
        name: str | None = None,
        birth_year: int | None = None,
        nationality: str | None = None,
    ) -> Author | None:
        """Update an existing author."""
        session: AsyncSession = info.context.session
        author = await session.get(AuthorModel, int(id))
        if author is None:
            return None
        if name is not None:
            author.name = name
        if birth_year is not None:
            author.birth_year = birth_year
        if nationality is not None:
            author.nationality = nationality
        await session.commit()
        await session.refresh(author, ["books"])
        return _author_to_strawberry(author)

    @strawberry.mutation
    async def delete_author(
        self, info: strawberry.types.Info[GraphQLContext], id: strawberry.ID
    ) -> bool:
        """Delete an author (cascade deletes all books)."""
        session: AsyncSession = info.context.session
        author = await session.get(AuthorModel, int(id))
        if author is None:
            return False
        await session.delete(author)
        await session.commit()
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
