"""Main CLI entry point for gql-learn."""

from __future__ import annotations

import click

from gql_learn.cli.learn import resume
from gql_learn.cli.learn import start
from gql_learn.cli.learn import status


@click.group()
def cli() -> None:
    """GraphQL Learning Platform - Learn GraphQL with interactive Q&A and local ETL."""
    pass


cli.add_command(start)
cli.add_command(resume)
cli.add_command(status)


if __name__ == "__main__":
    cli()
