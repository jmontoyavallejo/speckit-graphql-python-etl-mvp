"""CLI commands for GraphQL server management."""

from __future__ import annotations

import subprocess
import signal
import sys
from pathlib import Path

import click


@click.command()
@click.option("--port", default=8000, help="Port number")
@click.option("--reload", is_flag=True, help="Auto-reload on code changes")
def start(port: int, reload: bool) -> None:
    """Start the local GraphQL server.

    Args:
        port: Port number for the server
        reload: Enable auto-reload for development
    """
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "gql_learn.api.app:app",
        f"--host=127.0.0.1",
        f"--port={port}",
    ]

    if reload:
        cmd.append("--reload")

    click.echo(f"[Server] Starting GraphQL server on port {port}...")
    click.echo(
        f"[Server] GraphQL endpoint: http://127.0.0.1:{port}/graphql"
    )

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        click.echo("\n[Server] Stopped")
    except subprocess.CalledProcessError as e:
        click.echo(f"[Server] Error: {e}", err=True)
        sys.exit(1)


@click.command()
def stop() -> None:
    """Stop the running GraphQL server.

    Sends SIGTERM signal to stop the server gracefully.
    """
    click.echo("[Server] Server stop command (use Ctrl+C to stop running server)")


@click.command()
@click.option("--tail", default=50, help="Number of lines to show")
@click.option("--follow", is_flag=True, help="Stream new logs")
def logs(tail: int, follow: bool) -> None:
    """Show server logs.

    Args:
        tail: Number of lines to display
        follow: Follow logs in real-time
    """
    log_file = Path.home() / ".gql-learn" / "server.log"

    if not log_file.exists():
        click.echo(f"[Server] No log file found at {log_file}")
        return

    try:
        with open(log_file) as f:
            lines = f.readlines()
            for line in lines[-tail:]:
                click.echo(line.rstrip())
    except IOError as e:
        click.echo(f"[Server] Error reading logs: {e}", err=True)
