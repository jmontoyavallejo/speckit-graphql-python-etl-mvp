"""Data loading functions for ETL pipelines (T078)."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any


def load_json(records: list[dict[str, Any]], filepath: str | Path) -> int:
    """Load records to a JSON file.

    Args:
        records: List of records to load
        filepath: Path where JSON file will be written

    Returns:
        Number of records written

    Raises:
        IOError: If file cannot be written
        TypeError: If records are not JSON-serializable
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return len(records)


def load_csv(
    records: list[dict[str, Any]],
    filepath: str | Path,
    fieldnames: list[str] | None = None,
) -> int:
    """Load records to a CSV file.

    Args:
        records: List of records to load
        filepath: Path where CSV file will be written
        fieldnames: List of field names (defaults to keys from first record)

    Returns:
        Number of records written

    Raises:
        IOError: If file cannot be written
        ValueError: If records are empty and fieldnames not provided
    """
    if not records:
        raise ValueError("Cannot write empty records to CSV")

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if fieldnames is None:
        fieldnames = list(records[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return len(records)


def load_sqlite(
    records: list[dict[str, Any]], db_path: str | Path, table_name: str
) -> int:
    """Load records to a SQLite database table.

    Args:
        records: List of records to load
        db_path: Path to SQLite database file
        table_name: Name of table to insert into

    Returns:
        Number of records inserted

    Raises:
        sqlite3.Error: If database operation fails
        ValueError: If records are empty
    """
    if not records:
        raise ValueError("Cannot load empty records")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Get column names from first record
        columns = list(records[0].keys())
        placeholders = ",".join(["?"] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        # Insert all records
        rows = [[r.get(col) for col in columns] for r in records]
        cursor.executemany(insert_sql, rows)
        conn.commit()

        return cursor.rowcount
    finally:
        conn.close()


def load_sqlite_with_schema(
    records: list[dict[str, Any]],
    db_path: str | Path,
    table_name: str,
    schema: dict[str, str],
) -> int:
    """Load records to a SQLite database, creating table if needed.

    Args:
        records: List of records to load
        db_path: Path to SQLite database file
        table_name: Name of table to create/insert into
        schema: Dict mapping column names to SQL types (e.g., {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'})

    Returns:
        Number of records inserted

    Raises:
        sqlite3.Error: If database operation fails
        ValueError: If records are empty
    """
    if not records:
        raise ValueError("Cannot load empty records")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Create table if it doesn't exist
        columns_def = ", ".join([f"{col} {type_}" for col, type_ in schema.items()])
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        cursor.execute(create_sql)

        # Insert records
        columns = list(records[0].keys())
        placeholders = ",".join(["?"] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        rows = [[r.get(col) for col in columns] for r in records]
        cursor.executemany(insert_sql, rows)
        conn.commit()

        return cursor.rowcount
    finally:
        conn.close()


def append_sqlite(
    records: list[dict[str, Any]], db_path: str | Path, table_name: str
) -> int:
    """Append records to existing SQLite table without duplicates.

    Args:
        records: List of records to append
        db_path: Path to SQLite database file
        table_name: Name of existing table

    Returns:
        Number of records inserted

    Raises:
        sqlite3.Error: If database operation fails
    """
    if not records:
        return 0

    db_path = Path(db_path)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        columns = list(records[0].keys())
        placeholders = ",".join(["?"] * len(columns))
        insert_sql = f"INSERT OR IGNORE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        rows = [[r.get(col) for col in columns] for r in records]
        cursor.executemany(insert_sql, rows)
        conn.commit()

        return cursor.rowcount
    finally:
        conn.close()
