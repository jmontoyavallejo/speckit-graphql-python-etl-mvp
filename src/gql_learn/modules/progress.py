"""Progress session persistence to JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gql_learn.modules.schemas import ProgressSession


def get_progress_dir() -> Path:
    """Get or create ~/.gql-learn directory."""
    progress_dir = Path.home() / ".gql-learn"
    progress_dir.mkdir(exist_ok=True)
    return progress_dir


def get_progress_file() -> Path:
    """Get progress.json file path."""
    return get_progress_dir() / "progress.json"


def load_progress() -> ProgressSession:
    """Load progress from JSON file.

    Returns:
        ProgressSession with saved progress, or empty session if file doesn't exist

    Raises:
        ValueError: If JSON is corrupted
    """
    progress_file = get_progress_file()

    if not progress_file.exists():
        return ProgressSession()

    try:
        with open(progress_file) as f:
            data: dict[str, Any] = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupted progress file: {e}")

    return ProgressSession(**data)


def save_progress(session: ProgressSession) -> None:
    """Save progress to JSON file atomically.

    Args:
        session: ProgressSession to save

    Raises:
        IOError: If writing to file fails
    """
    progress_file = get_progress_file()

    try:
        with open(progress_file, "w") as f:
            json.dump(session.model_dump(), f, indent=2, default=str)
    except IOError as e:
        raise IOError(f"Failed to save progress: {e}")


def clear_progress() -> None:
    """Clear all progress data."""
    progress_file = get_progress_file()
    if progress_file.exists():
        progress_file.unlink()
