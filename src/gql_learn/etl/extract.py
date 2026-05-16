"""GraphQL extraction module for ETL pipelines (T076)."""

from __future__ import annotations

from typing import Any

import httpx


async def extract_graphql(endpoint: str, query: str) -> list[dict[str, Any]]:
    """Extract data from a GraphQL endpoint using httpx.

    Args:
        endpoint: URL to GraphQL endpoint (e.g., http://localhost:8000/graphql)
        query: GraphQL query string

    Returns:
        List of records extracted from the GraphQL response

    Raises:
        httpx.RequestError: If the HTTP request fails
        ValueError: If the GraphQL response contains errors
    """
    if not endpoint or not endpoint.startswith("http"):
        raise ValueError(f"Invalid endpoint URL: {endpoint}")

    if not query or not query.strip():
        raise ValueError("GraphQL query cannot be empty")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={"query": query},
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()

        # Check for GraphQL errors
        if "errors" in data and data["errors"]:
            errors = data["errors"]
            error_msg = (
                "; ".join(e.get("message", str(e)) for e in errors)
                if isinstance(errors, list)
                else str(errors)
            )
            raise ValueError(f"GraphQL error: {error_msg}")

        # Extract data from response
        if "data" not in data:
            raise ValueError("No data field in GraphQL response")

        # Convert response data to list of records
        response_data = data["data"]

        # If response is a dict with a single key that's a list, use that list
        if isinstance(response_data, dict) and len(response_data) == 1:
            records = list(response_data.values())[0]
        else:
            records = response_data

        if not isinstance(records, list):
            records = [records] if records else []

        return records


async def extract_graphql_with_pagination(
    endpoint: str,
    query: str,
    page_size: int = 100,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    """Extract data from a GraphQL endpoint with pagination support.

    Args:
        endpoint: URL to GraphQL endpoint
        query: GraphQL query string (should include $offset and $limit variables)
        page_size: Number of records per page
        max_pages: Maximum number of pages to fetch (None = all pages)

    Returns:
        List of all records extracted across all pages

    Raises:
        httpx.RequestError: If any HTTP request fails
        ValueError: If the GraphQL response contains errors
    """
    all_records: list[dict[str, Any]] = []
    page = 0

    async with httpx.AsyncClient() as client:
        while max_pages is None or page < max_pages:
            offset = page * page_size

            response = await client.post(
                endpoint,
                json={
                    "query": query,
                    "variables": {"offset": offset, "limit": page_size},
                },
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data and data["errors"]:
                errors = data["errors"]
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if isinstance(errors, list)
                    else str(errors)
                )
                raise ValueError(f"GraphQL error: {error_msg}")

            if "data" not in data:
                raise ValueError("No data field in GraphQL response")

            response_data = data["data"]
            if isinstance(response_data, dict) and len(response_data) == 1:
                records = list(response_data.values())[0]
            else:
                records = response_data

            if not isinstance(records, list):
                records = [records] if records else []

            if not records:
                break  # No more data

            all_records.extend(records)
            page += 1

    return all_records
