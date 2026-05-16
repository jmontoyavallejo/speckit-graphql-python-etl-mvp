"""GraphQL request context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strawberry.fastapi import BaseContext

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GraphQLContext(BaseContext):
    """Context for GraphQL requests with database session."""

    session: AsyncSession | None = None

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize context with optional database session.

        Args:
            session: AsyncSession for database operations
        """
        super().__init__()
        self.session = session
