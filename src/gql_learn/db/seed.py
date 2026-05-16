"""Database seeding with sample Author and Book data."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from gql_learn.db.models import Author
from gql_learn.db.models import Book
from gql_learn.db.session import SessionLocal
from gql_learn.db.session import engine

if TYPE_CHECKING:
    pass


async def seed_database() -> None:
    """Populate database with sample data."""
    async with SessionLocal() as session:
        await session.query(Book).delete()
        await session.query(Author).delete()

        authors = [
            Author(name="George Orwell", birth_year=1903, nationality="British"),
            Author(name="Jane Austen", birth_year=1775, nationality="British"),
            Author(name="F. Scott Fitzgerald", birth_year=1896, nationality="American"),
            Author(name="Harper Lee", birth_year=1926, nationality="American"),
            Author(name="Gabriel García Márquez", birth_year=1927, nationality="Colombian"),
            Author(name="Leo Tolstoy", birth_year=1828, nationality="Russian"),
            Author(name="Fyodor Dostoevsky", birth_year=1821, nationality="Russian"),
            Author(name="Mark Twain", birth_year=1835, nationality="American"),
            Author(name="Agatha Christie", birth_year=1890, nationality="British"),
            Author(name="Virginia Woolf", birth_year=1882, nationality="British"),
            Author(name="Franz Kafka", birth_year=1883, nationality="Czech"),
            Author(name="James Joyce", birth_year=1882, nationality="Irish"),
            Author(name="Ernest Hemingway", birth_year=1899, nationality="American"),
            Author(name="Gustave Flaubert", birth_year=1821, nationality="French"),
            Author(name="Honoré de Balzac", birth_year=1799, nationality="French"),
            Author(name="Charles Dickens", birth_year=1812, nationality="British"),
            Author(name="Oscar Wilde", birth_year=1854, nationality="Irish"),
            Author(name="Bram Stoker", birth_year=1847, nationality="Irish"),
            Author(name="Mary Shelley", birth_year=1797, nationality="British"),
            Author(name="Charlotte Brontë", birth_year=1816, nationality="British"),
        ]

        session.add_all(authors)
        await session.flush()

        books_data = [
            ("1984", authors[0], 1949, "Dystopian"),
            ("Animal Farm", authors[0], 1945, "Satire"),
            ("Pride and Prejudice", authors[1], 1813, "Romance"),
            ("Emma", authors[1], 1815, "Romance"),
            ("The Great Gatsby", authors[2], 1925, "Fiction"),
            ("To Kill a Mockingbird", authors[3], 1960, "Fiction"),
            ("One Hundred Years of Solitude", authors[4], 1967, "Magical Realism"),
            ("War and Peace", authors[5], 1869, "Historical Fiction"),
            ("Crime and Punishment", authors[6], 1866, "Psychological Thriller"),
            ("The Brothers Karamazov", authors[6], 1879, "Philosophical Fiction"),
            ("The Adventures of Huckleberry Finn", authors[7], 1884, "Adventure"),
            ("Murder on the Orient Express", authors[8], 1934, "Mystery"),
            ("Mrs. Dalloway", authors[9], 1925, "Modernist Fiction"),
            ("The Metamorphosis", authors[10], 1915, "Psychological"),
            ("Ulysses", authors[11], 1922, "Modernist Fiction"),
            ("The Old Man and the Sea", authors[12], 1952, "Adventure"),
            ("Madame Bovary", authors[13], 1856, "Literary Fiction"),
            ("Dracula", authors[17], 1897, "Gothic Horror"),
            ("Frankenstein", authors[18], 1818, "Science Fiction"),
            ("Jane Eyre", authors[19], 1847, "Romance"),
        ]

        books = [
            Book(title=title, author=author, year=year, genre=genre)
            for title, author, year, genre in books_data
        ]

        for _ in range(4):
            for title, author, year, genre in books_data:
                books.append(
                    Book(title=title, author=author, year=year, genre=genre)
                )

        session.add_all(books)
        await session.commit()


async def main() -> None:
    """Entry point for seed script."""
    from gql_learn.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_database()
    print("✓ Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(main())
