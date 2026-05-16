"""GraphQL request context."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GraphQLContext:
    """Context for GraphQL requests with database session."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize context with optional database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session
