"""CLI utility functions for Rich output formatting."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"[red]✗ {message}[/red]")


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[green]✓ {message}[/green]")


def print_info(message: str) -> None:
    """Print informational message in blue."""
    console.print(f"[blue]ℹ {message}[/blue]")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"[yellow]⚠ {message}[/yellow]")


def print_table(title: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Print a formatted table using Rich.

    Args:
        title: Table title
        rows: List of dicts with column data
        columns: List of column names to display
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")

    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)
