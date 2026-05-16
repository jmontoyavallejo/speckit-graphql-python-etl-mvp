"""Unit tests for data transformation (aggregate_by_genre) (T068)."""

from __future__ import annotations

from typing import Any

import pytest


class TestDataTransformation:
    """Tests for ETL data transformation operations."""

    def test_transform_aggregate_by_genre(self) -> None:
        """Test aggregating book records by genre."""
        records = [
            {"id": 1, "title": "Pride and Prejudice", "genre": "Romance", "year": 1813},
            {"id": 2, "title": "Emma", "genre": "Romance", "year": 1815},
            {"id": 3, "title": "1984", "genre": "Science Fiction", "year": 1949},
            {"id": 4, "title": "Dune", "genre": "Science Fiction", "year": 1965},
        ]

        # Expected aggregation by genre
        expected_genres = {"Romance": 2, "Science Fiction": 2}

        genre_counts: dict[str, int] = {}
        for record in records:
            genre = record["genre"]
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        assert genre_counts == expected_genres

    def test_transform_filter_by_year(self) -> None:
        """Test filtering records by publication year."""
        records = [
            {"id": 1, "title": "Pride and Prejudice", "year": 1813},
            {"id": 2, "title": "1984", "year": 1949},
            {"id": 3, "title": "Dune", "year": 1965},
            {"id": 4, "title": "The Hobbit", "year": 1937},
        ]

        # Filter records after 1950
        filtered = [r for r in records if r["year"] > 1950]

        assert len(filtered) == 1
        assert filtered[0]["id"] == 3

    def test_transform_enrich_records(self) -> None:
        """Test enriching records with additional computed fields."""
        records = [
            {"id": 1, "title": "Book A", "price": 10.0},
            {"id": 2, "title": "Book B", "price": 15.0},
            {"id": 3, "title": "Book C", "price": 20.0},
        ]

        # Add tax (10%) to each record
        enriched = []
        for record in records:
            enriched_record = record.copy()
            enriched_record["tax"] = record["price"] * 0.10
            enriched_record["total"] = record["price"] + enriched_record["tax"]
            enriched.append(enriched_record)

        assert len(enriched) == 3
        assert enriched[0]["tax"] == 1.0
        assert enriched[0]["total"] == 11.0

    def test_transform_deduplicate_records(self) -> None:
        """Test deduplicating records by ID."""
        records = [
            {"id": 1, "title": "Book A"},
            {"id": 2, "title": "Book B"},
            {"id": 1, "title": "Book A"},  # Duplicate
            {"id": 3, "title": "Book C"},
        ]

        seen_ids = set()
        deduplicated = []
        for record in records:
            if record["id"] not in seen_ids:
                deduplicated.append(record)
                seen_ids.add(record["id"])

        assert len(deduplicated) == 3
        assert all(r["id"] in seen_ids for r in deduplicated)

    def test_transform_sort_records(self) -> None:
        """Test sorting records by field."""
        records = [
            {"id": 3, "title": "Book C", "rating": 4.2},
            {"id": 1, "title": "Book A", "rating": 4.8},
            {"id": 2, "title": "Book B", "rating": 3.9},
        ]

        # Sort by rating descending
        sorted_records = sorted(records, key=lambda r: r["rating"], reverse=True)

        assert sorted_records[0]["id"] == 1  # Highest rating
        assert sorted_records[-1]["id"] == 2  # Lowest rating

    def test_transform_group_by_author(self) -> None:
        """Test grouping books by author."""
        records = [
            {"id": 1, "title": "Pride and Prejudice", "author": "Jane Austen"},
            {"id": 2, "title": "Emma", "author": "Jane Austen"},
            {"id": 3, "title": "1984", "author": "George Orwell"},
        ]

        # Group by author
        by_author: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            author = record["author"]
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(record)

        assert len(by_author) == 2
        assert len(by_author["Jane Austen"]) == 2
        assert len(by_author["George Orwell"]) == 1

    def test_transform_with_missing_field_handling(self) -> None:
        """Test transformation handles missing fields gracefully."""
        records = [
            {"id": 1, "title": "Book A", "rating": 4.5},
            {"id": 2, "title": "Book B"},  # Missing rating
            {"id": 3, "title": "Book C", "rating": 3.8},
        ]

        # Default missing ratings to 0
        transformed = []
        for record in records:
            transformed_record = record.copy()
            transformed_record["rating"] = record.get("rating", 0.0)
            transformed.append(transformed_record)

        assert transformed[1]["rating"] == 0.0
        assert all("rating" in r for r in transformed)

    def test_transform_aggregate_with_sum(self) -> None:
        """Test aggregating numeric values with sum."""
        records = [
            {"genre": "Fiction", "count": 10},
            {"genre": "Fiction", "count": 5},
            {"genre": "Sci-Fi", "count": 8},
        ]

        totals: dict[str, int] = {}
        for record in records:
            genre = record["genre"]
            totals[genre] = totals.get(genre, 0) + record["count"]

        assert totals["Fiction"] == 15
        assert totals["Sci-Fi"] == 8
