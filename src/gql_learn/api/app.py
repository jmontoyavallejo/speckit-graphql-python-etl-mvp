"""FastAPI application factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from gql_learn.config import settings
from gql_learn.db.session import SessionLocal
from gql_learn.gql.context import GraphQLContext
from gql_learn.gql.schema import schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_context(request: Request) -> GraphQLContext:
    """Get GraphQL context with database session from request state."""
    session: AsyncSession | None = getattr(request.state, "db_session", None)
    if session is None:
        session = SessionLocal()
    return GraphQLContext(session=session)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="GraphQL Learning Platform",
        description="Interactive GraphQL learning with Q&A modules and ETL pipelines",
        version="0.1.0",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    graphql_app = GraphQLRouter(schema, context_getter=get_context)
    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_app()
