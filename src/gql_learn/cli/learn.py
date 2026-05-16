"""CLI commands for interactive learning."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from gql_learn.modules import load_module
from gql_learn.modules import load_progress
from gql_learn.modules import list_modules
from gql_learn.modules import save_progress
from gql_learn.modules.evaluator import evaluate_answer

console = Console()


def _start_learning(module_id: str | None) -> None:
    """Internal function to start learning with Q&A modules."""
    session = load_progress()

    if not module_id:
        available = list_modules()
        if not available:
            console.print("[red]No modules available[/red]")
            return

        if session.current_module and session.current_module in available:
            module_id = session.current_module
        else:
            module_id = available[0]

    try:
        module = load_module(module_id)
    except FileNotFoundError:
        console.print(f"[red]Module not found: {module_id}[/red]")
        return

    session.current_module = module_id
    module_progress = session.get_module_progress(module_id)

    console.print(f"\n[bold blue]{module.title}[/bold blue]")
    console.print(f"[dim]{module.description}[/dim]\n")

    start_idx = module_progress.current_question
    correct_count = sum(
        1 for r in module_progress.answers if r.is_correct
    )

    for idx, question in enumerate(module.questions[start_idx:], start=start_idx):
        question_num = idx + 1
        console.print(f"[bold]Question {question_num} of {len(module.questions)}:[/bold]")
        console.print(f"{question.text}\n")

        if question.hint:
            console.print(f"[dim]Hint: {question.hint}[/dim]")

        user_answer = console.input("[bold cyan]Your answer: [/bold cyan]")

        is_correct = evaluate_answer(user_answer, question.acceptable_answers)
        session.add_response(module_id, question.id, user_answer, is_correct)

        if is_correct:
            console.print("[green]✓ Correct![/green]")
            correct_count += 1
        else:
            console.print("[red]✗ Incorrect[/red]")

        console.print(f"[dim]{question.explanation}[/dim]\n")

        module_progress.current_question = idx + 1

    module_progress.completed = True
    module_progress.score = int((correct_count / len(module.questions)) * 100)

    save_progress(session)

    console.print(f"\n[bold green]Module Complete![/bold green]")
    console.print(f"Score: {module_progress.score}% ({correct_count}/{len(module.questions)})")


@click.command()
@click.argument("module_id", required=False)
def start(module_id: str | None) -> None:
    """Start learning with Q&A modules."""
    _start_learning(module_id)


@click.command()
@click.argument("module_id", required=False)
def resume(module_id: str | None) -> None:
    """Resume learning from where you left off."""
    session = load_progress()

    if not module_id:
        if not session.current_module:
            console.print("[yellow]No previous module in progress. Starting fresh.[/yellow]")
            _start_learning(None)
            return
        module_id = session.current_module

    try:
        module = load_module(module_id)
    except FileNotFoundError:
        console.print(f"[red]Module not found: {module_id}[/red]")
        return

    module_progress = session.get_module_progress(module_id)

    if module_progress.completed:
        console.print(f"[bold green]✓ {module.title} completed![/bold green]")
        console.print(f"Final score: {module_progress.score}%")
        return

    console.print(f"[yellow]Resuming {module.title}...[/yellow]")
    _start_learning(module_id)


@click.command()
def status() -> None:
    """Show learning progress summary."""
    session = load_progress()

    if not session.modules:
        console.print("[yellow]No progress yet. Start learning with: gql-learn start[/yellow]")
        return

    table = Table(title="Learning Progress")
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Score", justify="right")
    table.add_column("Progress")

    for module_id, progress in session.modules.items():
        status_text = "✓ Completed" if progress.completed else "→ In Progress"
        score_text = f"{progress.score}%" if progress.completed else "-"
        progress_text = (
            f"{progress.current_question}/{sum(1 for _ in [1] if progress.answers)}"
        )

        table.add_row(module_id, status_text, score_text, progress_text)

    console.print(table)

    completed = sum(1 for p in session.modules.values() if p.completed)
    total = len(session.modules)
    console.print(f"\n[bold]Overall: {completed}/{total} modules completed[/bold]")
