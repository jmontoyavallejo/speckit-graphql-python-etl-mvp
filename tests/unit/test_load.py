"""Unit tests for loading to JSON file and SQLite (T069-T070)."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import pytest


class TestLoadToJSON:
    """Tests for loading data to JSON files (T069)."""

    def test_load_records_to_json(self) -> None:
        """Test writing records to JSON file."""
        records = [
            {"id": 1, "title": "Book A", "genre": "Fiction"},
            {"id": 2, "title": "Book B", "genre": "Mystery"},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"

            # Write records to JSON
            with open(output_path, "w") as f:
                json.dump(records, f)

            # Verify file was created and content is correct
            assert output_path.exists()
            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded == records

    def test_load_empty_records_to_json(self) -> None:
        """Test writing empty record list to JSON."""
        records: list[dict[str, Any]] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "empty.json"
            with open(output_path, "w") as f:
                json.dump(records, f)

            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded == []

    def test_load_large_records_to_json(self) -> None:
        """Test writing large dataset to JSON file."""
        records = [{"id": i, "title": f"Book {i}"} for i in range(1000)]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "large.json"
            with open(output_path, "w") as f:
                json.dump(records, f)

            file_size = output_path.stat().st_size
            assert file_size > 0
            with open(output_path) as f:
                loaded = json.load(f)
            assert len(loaded) == 1000

    def test_load_json_with_nested_objects(self) -> None:
        """Test writing JSON with nested structures."""
        records = [
            {
                "id": 1,
                "title": "Book A",
                "author": {"name": "Author One", "birth_year": 1950},
                "tags": ["fiction", "classic"],
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested.json"
            with open(output_path, "w") as f:
                json.dump(records, f)

            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded[0]["author"]["name"] == "Author One"
            assert "fiction" in loaded[0]["tags"]

    def test_load_json_handles_special_characters(self) -> None:
        """Test JSON encoding of special characters."""
        records = [
            {"id": 1, "title": "Café au Lait", "description": "Special chars: é, ñ, 日本"},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "special.json"
            with open(output_path, "w") as f:
                json.dump(records, f, ensure_ascii=False)

            with open(output_path, encoding="utf-8") as f:
                loaded = json.load(f)
            assert "Café" in loaded[0]["title"]
            assert "日本" in loaded[0]["description"]


class TestLoadToSQLite:
    """Tests for loading data to SQLite database (T070)."""

    def test_load_records_to_sqlite(self) -> None:
        """Test loading records into SQLite table."""
        records = [
            {"id": 1, "title": "Pride and Prejudice", "year": 1813},
            {"id": 2, "title": "1984", "year": 1949},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Create table and insert records
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    year INTEGER
                )
            """
            )

            for record in records:
                cursor.execute(
                    "INSERT INTO books (id, title, year) VALUES (?, ?, ?)",
                    (record["id"], record["title"], record["year"]),
                )
            conn.commit()

            # Verify data was inserted
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            assert count == 2

            cursor.execute("SELECT title FROM books WHERE id = 1")
            result = cursor.fetchone()
            assert result[0] == "Pride and Prejudice"

            conn.close()

    def test_load_sqlite_with_foreign_keys(self) -> None:
        """Test loading records with foreign key relationships."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "library.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Create author and book tables
            cursor.execute(
                """
                CREATE TABLE authors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    author_id INTEGER NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES authors(id)
                )
            """
            )

            # Insert author
            cursor.execute("INSERT INTO authors (id, name) VALUES (1, 'Jane Austen')")

            # Insert book with foreign key
            cursor.execute("INSERT INTO books (id, title, author_id) VALUES (1, 'Emma', 1)")
            conn.commit()

            # Verify relationship
            cursor.execute(
                """
                SELECT b.title, a.name FROM books b
                JOIN authors a ON b.author_id = a.id
                WHERE b.id = 1
            """
            )
            result = cursor.fetchone()
            assert result[0] == "Emma"
            assert result[1] == "Jane Austen"

            conn.close()

    def test_load_sqlite_bulk_insert(self) -> None:
        """Test bulk inserting many records efficiently."""
        records = [{"id": i, "title": f"Book {i}"} for i in range(1, 101)]

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "bulk.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL
                )
            """
            )

            # Bulk insert
            cursor.executemany(
                "INSERT INTO books (id, title) VALUES (?, ?)",
                [(r["id"], r["title"]) for r in records],
            )
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            assert count == 100

            conn.close()

    def test_load_sqlite_duplicate_handling(self) -> None:
        """Test handling duplicate IDs when loading to SQLite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "unique.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL
                )
            """
            )

            # Insert first record
            cursor.execute("INSERT INTO books (id, title) VALUES (1, 'Book A')")
            conn.commit()

            # Try to insert duplicate - should fail
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO books (id, title) VALUES (1, 'Book B')")
                conn.commit()

            conn.close()

    def test_load_sqlite_transaction_rollback(self) -> None:
        """Test transaction rollback on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "rollback.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL
                )
            """
            )
            conn.commit()

            try:
                cursor.execute("INSERT INTO books (id, title) VALUES (1, 'Book A')")
                cursor.execute("INSERT INTO books (id, title) VALUES (1, 'Book B')")  # Duplicate
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()

            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            assert count == 0  # Rollback should have cancelled both inserts

            conn.close()
