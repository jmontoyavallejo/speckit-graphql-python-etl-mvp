"""Initialize application environment (T096)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
from rich.console import Console

from gql_learn.cli.utils import print_success, print_error
from gql_learn.db.models import Base
from gql_learn.db.seed import seed_database
from gql_learn.db.session import engine
from gql_learn.modules.progress import ProgressSession, save_progress

console = Console()


@click.command()
def init() -> None:
    """Initialize the application.

    - Creates ~/.gql-learn directory
    - Seeds database with sample data
    - Initializes progress tracking file
    """
    try:
        app_dir = Path.home() / ".gql-learn"
        app_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Created application directory: {app_dir}")

        asyncio.run(_init_database())
        print_success("Database initialized and seeded")

        progress_file = app_dir / "progress.json"
        if not progress_file.exists():
            session = ProgressSession()
            save_progress(session)
            print_success(f"Created progress file: {progress_file}")
        else:
            console.print("[dim]Progress file already exists[/dim]")

        print_success("Application initialized successfully!")
        console.print(
            "\n[bold]Next steps:[/bold]"
        )
        console.print("  1. Run [cyan]gql-learn start[/cyan] to begin learning")
        console.print("  2. Run [cyan]gql-learn server start[/cyan] to start the GraphQL server")
        console.print("  3. Run [cyan]gql-learn pipeline run sample_library_etl[/cyan] to run a pipeline")

    except Exception as e:
        print_error(f"Initialization failed: {e}")
        raise


async def _init_database() -> None:
    """Initialize database with schema and sample data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_database()
