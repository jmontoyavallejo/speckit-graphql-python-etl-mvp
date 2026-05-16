"""Main CLI entry point for gql-learn."""

from __future__ import annotations

import click

from gql_learn.cli.learn import resume
from gql_learn.cli.learn import start
from gql_learn.cli.learn import status
from gql_learn.cli import server as server_module


@click.group()
def cli() -> None:
    """GraphQL Learning Platform - Learn GraphQL with interactive Q&A and local ETL."""
    pass


@click.group()
def server() -> None:
    """GraphQL server management commands."""
    pass


cli.add_command(start)
cli.add_command(resume)
cli.add_command(status)
cli.add_command(server)

server.add_command(server_module.start, name="start")
server.add_command(server_module.stop, name="stop")
server.add_command(server_module.logs, name="logs")


if __name__ == "__main__":
    cli()
