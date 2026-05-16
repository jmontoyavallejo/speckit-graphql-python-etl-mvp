"""Main CLI entry point for gql-learn."""

from __future__ import annotations

import click

from gql_learn.cli.learn import resume, start, status
from gql_learn.cli import server as server_module
from gql_learn.cli import pipeline as pipeline_module


@click.group()
@click.version_option("0.1.0")
def cli() -> None:
    """GraphQL Learning Platform - Learn GraphQL with interactive Q&A and local ETL."""
    pass


@click.group()
def server() -> None:
    """GraphQL server management commands."""
    pass


@click.group()
def pipeline() -> None:
    """ETL pipeline management commands."""
    pass


cli.add_command(start)
cli.add_command(resume)
cli.add_command(status)
cli.add_command(server)
cli.add_command(pipeline)

server.add_command(server_module.start, name="start")
server.add_command(server_module.stop, name="stop")
server.add_command(server_module.logs, name="logs")

pipeline.add_command(pipeline_module.run, name="run")
pipeline.add_command(pipeline_module.list, name="list")
pipeline.add_command(pipeline_module.show, name="show")
pipeline.add_command(pipeline_module.runs, name="runs")


if __name__ == "__main__":
    cli()
