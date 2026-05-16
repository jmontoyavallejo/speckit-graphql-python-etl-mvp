"""Data transformation functions for ETL pipelines (T077)."""

from __future__ import annotations

from typing import Any, Callable


def aggregate_by_genre(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate book records by genre with count and list.

    Args:
        records: List of book records with 'genre' field

    Returns:
        List of aggregated records: [{genre, count, books: [...]}]

    Raises:
        ValueError: If records is empty or missing genre field
    """
    if not records:
        raise ValueError("Cannot aggregate empty record list")

    aggregated: dict[str, dict[str, Any]] = {}

    for record in records:
        if "genre" not in record:
            raise ValueError(f"Record missing 'genre' field: {record}")

        genre = record["genre"]
        if genre not in aggregated:
            aggregated[genre] = {"genre": genre, "count": 0, "books": []}

        aggregated[genre]["count"] += 1
        aggregated[genre]["books"].append(record)

    return list(aggregated.values())


def filter_by_field(
    records: list[dict[str, Any]], field: str, value: Any
) -> list[dict[str, Any]]:
    """Filter records by field value.

    Args:
        records: List of records
        field: Field name to filter by
        value: Value to match

    Returns:
        Filtered list of records
    """
    return [r for r in records if r.get(field) == value]


def filter_by_predicate(
    records: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]
) -> list[dict[str, Any]]:
    """Filter records using a custom predicate function.

    Args:
        records: List of records
        predicate: Function that returns True for records to keep

    Returns:
        Filtered list of records
    """
    return [r for r in records if predicate(r)]


def enrich_records(
    records: list[dict[str, Any]], enrichments: dict[str, Callable[[dict[str, Any]], Any]]
) -> list[dict[str, Any]]:
    """Enrich records by adding computed fields.

    Args:
        records: List of records
        enrichments: Dict mapping field names to functions that compute field value

    Returns:
        List of enriched records with new fields added
    """
    enriched = []
    for record in records:
        enriched_record = record.copy()
        for field_name, compute_fn in enrichments.items():
            enriched_record[field_name] = compute_fn(record)
        enriched.append(enriched_record)
    return enriched


def deduplicate_by_field(
    records: list[dict[str, Any]], field: str
) -> list[dict[str, Any]]:
    """Deduplicate records by keeping first occurrence of each field value.

    Args:
        records: List of records
        field: Field to use for deduplication

    Returns:
        List of unique records
    """
    seen = set()
    deduplicated = []
    for record in records:
        field_value = record.get(field)
        if field_value not in seen:
            seen.add(field_value)
            deduplicated.append(record)
    return deduplicated


def sort_records(
    records: list[dict[str, Any]], field: str, reverse: bool = False
) -> list[dict[str, Any]]:
    """Sort records by field value.

    Args:
        records: List of records
        field: Field to sort by
        reverse: If True, sort in descending order

    Returns:
        Sorted list of records
    """
    return sorted(records, key=lambda r: r.get(field, ""), reverse=reverse)


def group_by_field(
    records: list[dict[str, Any]], field: str
) -> dict[Any, list[dict[str, Any]]]:
    """Group records by field value.

    Args:
        records: List of records
        field: Field to group by

    Returns:
        Dictionary mapping field values to lists of records
    """
    grouped: dict[Any, list[dict[str, Any]]] = {}
    for record in records:
        field_value = record.get(field)
        if field_value not in grouped:
            grouped[field_value] = []
        grouped[field_value].append(record)
    return grouped


def transform_field_values(
    records: list[dict[str, Any]], transformations: dict[str, Callable[[Any], Any]]
) -> list[dict[str, Any]]:
    """Transform field values in records using mapping functions.

    Args:
        records: List of records
        transformations: Dict mapping field names to transformation functions

    Returns:
        List of records with transformed field values
    """
    transformed = []
    for record in records:
        transformed_record = record.copy()
        for field, transform_fn in transformations.items():
            if field in transformed_record:
                transformed_record[field] = transform_fn(transformed_record[field])
        transformed.append(transformed_record)
    return transformed


def validate_records(
    records: list[dict[str, Any]], required_fields: list[str]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate records have required fields, separating valid from invalid.

    Args:
        records: List of records
        required_fields: List of field names that must be present

    Returns:
        Tuple of (valid_records, error_messages)
    """
    valid = []
    errors = []

    for i, record in enumerate(records):
        missing_fields = [f for f in required_fields if f not in record]
        if missing_fields:
            errors.append(
                f"Record {i}: missing required fields: {', '.join(missing_fields)}"
            )
        else:
            valid.append(record)

    return valid, errors


def passthrough(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identity transformation - returns records unchanged.

    Args:
        records: List of records

    Returns:
        Same list of records
    """
    return records
