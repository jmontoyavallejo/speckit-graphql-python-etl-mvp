"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from gql_learn.config import settings
from gql_learn.db.session import get_db
from gql_learn.gql.context import GraphQLContext
from gql_learn.gql.schema import schema


async def get_context() -> GraphQLContext:
    """Get GraphQL context with database session."""
    async for session in get_db():
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
