"""Integration tests for server CLI commands."""

from __future__ import annotations

import asyncio
import subprocess
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestServerCLI:
    """Test server CLI commands."""

    async def test_health_endpoint(self, client: AsyncClient) -> None:
        """Test that health endpoint is available and working."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_graphql_endpoint_available(self, client: AsyncClient) -> None:
        """Test that GraphQL endpoint is available."""
        query = """
        {
            __schema {
                queryType {
                    name
                }
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    async def test_graphql_introspection(self, client: AsyncClient) -> None:
        """Test that GraphQL introspection works."""
        query = """
        {
            __schema {
                types {
                    name
                }
            }
        }
        """
        response = await client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        types = [t["name"] for t in data["data"]["__schema"]["types"]]
        # Check for our custom types
        assert "Author" in types or any("Author" in t for t in types)
        assert "Book" in types or any("Book" in t for t in types)
