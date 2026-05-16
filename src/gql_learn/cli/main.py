"""Main CLI entry point for gql-learn."""

from __future__ import annotations

import click


@click.group()
def cli() -> None:
    """GraphQL Learning Platform - Learn GraphQL with interactive Q&A and local ETL."""
    pass


if __name__ == "__main__":
    cli()
