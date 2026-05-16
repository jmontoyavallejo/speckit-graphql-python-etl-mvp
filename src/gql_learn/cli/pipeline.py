"""CLI commands for ETL pipeline management (T081-T084)."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from gql_learn.config import Settings
from gql_learn.etl.models import ETLPipeline
from gql_learn.etl.runner import execute_pipeline, get_load_function

console = Console()
logger = logging.getLogger(__name__)


def load_pipeline_config(pipeline_name: str) -> ETLPipeline:
    """Load pipeline configuration from data/pipelines/ directory.

    Args:
        pipeline_name: Name of pipeline (without .json extension)

    Returns:
        ETLPipeline configuration

    Raises:
        FileNotFoundError: If pipeline config not found
        json.JSONDecodeError: If config is invalid JSON
    """
    pipelines_dir = Path("data/pipelines")
    if not pipelines_dir.exists():
        raise FileNotFoundError(f"Pipelines directory not found: {pipelines_dir}")

    config_file = pipelines_dir / f"{pipeline_name}.json"
    if not config_file.exists():
        raise FileNotFoundError(f"Pipeline configuration not found: {config_file}")

    with open(config_file) as f:
        config_data = json.load(f)

    return ETLPipeline(**config_data)


def get_runs_directory() -> Path:
    """Get the directory where pipeline runs are logged.

    Returns:
        Path to runs directory
    """
    runs_dir = Path.home() / ".gql-learn" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    return runs_dir


@click.group()
def pipeline() -> None:
    """Manage ETL pipelines."""
    pass


@pipeline.command()
@click.argument("name")
@click.option(
    "--json", "output_json", is_flag=True, help="Output run result as JSON"
)
def run(name: str, output_json: bool) -> None:
    """Run an ETL pipeline.

    NAME: Pipeline name (e.g., sample_library_etl)
    """
    try:
        # Load pipeline configuration
        pipeline_config = load_pipeline_config(name)
        settings = Settings()

        # Execute pipeline
        console.print(
            f"[blue]Running pipeline:[/blue] {pipeline_config.name}",
            style="bold",
        )
        console.print(f"Description: {pipeline_config.description}")

        # Run async execution
        run_result = asyncio.run(
            execute_pipeline(
                pipeline_config,
                settings.graphql_endpoint,
                get_load_function(pipeline_config.load_destination),
            )
        )

        # Save run log
        runs_dir = get_runs_directory()
        run_log_file = (
            runs_dir / f"{run_result.id}.json"
        )
        with open(run_log_file, "w") as f:
            json.dump(
                {
                    "id": run_result.id,
                    "pipeline_id": run_result.pipeline_id,
                    "status": run_result.status.value,
                    "records_extracted": run_result.records_extracted,
                    "records_transformed": run_result.records_transformed,
                    "records_loaded": run_result.records_loaded,
                    "errors": run_result.errors,
                    "started_at": run_result.started_at.isoformat(),
                    "completed_at": (
                        run_result.completed_at.isoformat()
                        if run_result.completed_at
                        else None
                    ),
                    "duration_seconds": run_result.duration_seconds,
                },
                f,
                indent=2,
            )

        # Output results
        if output_json:
            console.print_json(json.dumps({
                "id": run_result.id,
                "status": run_result.status.value,
                "records_extracted": run_result.records_extracted,
                "records_loaded": run_result.records_loaded,
                "duration_seconds": run_result.duration_seconds,
            }))
        else:
            if run_result.status.value == "success":
                console.print("[green]✓ Pipeline completed successfully[/green]")
            else:
                console.print("[red]✗ Pipeline failed[/red]")

            console.print(f"Extracted: {run_result.records_extracted}")
            console.print(f"Transformed: {run_result.records_transformed}")
            console.print(f"Loaded: {run_result.records_loaded}")

            if run_result.duration_seconds:
                console.print(
                    f"Duration: {run_result.duration_seconds:.2f}s"
                )

            if run_result.errors:
                console.print("[yellow]Errors:[/yellow]")
                for error in run_result.errors:
                    console.print(f"  • {error}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        logger.exception("Pipeline execution failed")
        raise click.ClickException(str(e))


@pipeline.command()
def list() -> None:
    """List all available pipelines."""
    pipelines_dir = Path("data/pipelines")
    if not pipelines_dir.exists():
        console.print("[yellow]No pipelines directory found[/yellow]")
        return

    pipeline_files = sorted(pipelines_dir.glob("*.json"))
    if not pipeline_files:
        console.print("[yellow]No pipelines found[/yellow]")
        return

    table = Table(title="Available Pipelines")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description")
    table.add_column("Built-in", style="green")

    for config_file in pipeline_files:
        with open(config_file) as f:
            config = json.load(f)
        table.add_row(
            config.get("id", "N/A"),
            config.get("name", "N/A"),
            config.get("description", "N/A"),
            "Yes" if config.get("is_builtin", True) else "No",
        )

    console.print(table)


@pipeline.command()
@click.argument("name")
def show(name: str) -> None:
    """Display pipeline details.

    NAME: Pipeline name
    """
    try:
        pipeline_config = load_pipeline_config(name)

        console.print(f"[bold]{pipeline_config.name}[/bold]")
        console.print(f"ID: {pipeline_config.id}")
        console.print(f"Description: {pipeline_config.description}")
        console.print(f"Extract Query: {pipeline_config.extract_query[:100]}...")
        console.print(f"Transform: {pipeline_config.transform_function}")
        console.print(f"Load Destination: {pipeline_config.load_destination}")
        console.print(f"Built-in: {'Yes' if pipeline_config.is_builtin else 'No'}")
        console.print(f"Created: {pipeline_config.created_at.isoformat()}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise click.ClickException(str(e))


@pipeline.command()
@click.argument("name")
@click.option("--limit", default=10, help="Number of runs to show")
def runs(name: str, limit: int) -> None:
    """Show execution history for a pipeline.

    NAME: Pipeline name
    """
    runs_dir = get_runs_directory()
    run_files = sorted(runs_dir.glob("*.json"), reverse=True)[:limit]

    if not run_files:
        console.print("[yellow]No pipeline runs found[/yellow]")
        return

    table = Table(title=f"Recent Runs for {name}")
    table.add_column("Run ID", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Extracted")
    table.add_column("Loaded")
    table.add_column("Duration (s)")
    table.add_column("Date", style="green")

    for run_file in run_files:
        with open(run_file) as f:
            run_data = json.load(f)

        if run_data.get("pipeline_id") != name:
            continue

        status_str = run_data.get("status", "unknown")
        status_color = "green" if status_str == "success" else "red"

        table.add_row(
            run_data.get("id", "N/A")[:8],
            f"[{status_color}]{status_str}[/{status_color}]",
            str(run_data.get("records_extracted", 0)),
            str(run_data.get("records_loaded", 0)),
            f"{run_data.get('duration_seconds', 0):.2f}",
            run_data.get("completed_at", "N/A")[:10],
        )

    console.print(table)
