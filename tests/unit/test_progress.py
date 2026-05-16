"""Unit tests for ProgressSession persistence."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from gql_learn.modules.progress import clear_progress
from gql_learn.modules.progress import load_progress
from gql_learn.modules.progress import save_progress
from gql_learn.modules.schemas import ProgressSession


def test_save_and_load_progress() -> None:
    """Test saving and loading progress to JSON."""
    session = ProgressSession(current_module="01_schema_types")
    session.add_response("01_schema_types", "q1", "GraphQL", True)
    session.add_response("01_schema_types", "q2", "Schema", False)

    save_progress(session)
    loaded = load_progress()

    assert loaded.current_module == "01_schema_types"
    assert len(loaded.responses) == 2
    assert loaded.responses[0].is_correct is True
    assert loaded.responses[1].is_correct is False

    clear_progress()


def test_empty_progress_file() -> None:
    """Test loading when no progress file exists."""
    clear_progress()
    session = load_progress()

    assert session.current_module is None
    assert len(session.modules) == 0
    assert len(session.responses) == 0


def test_progress_session_add_response() -> None:
    """Test adding responses to progress session."""
    session = ProgressSession()

    session.add_response("module1", "q1", "answer1", True)
    session.add_response("module1", "q2", "answer2", False)

    assert len(session.responses) == 2
    assert "module1" in session.modules
    assert len(session.modules["module1"].answers) == 2


def test_progress_session_get_module_progress() -> None:
    """Test getting progress for a specific module."""
    session = ProgressSession()

    session.add_response("module1", "q1", "answer", True)
    progress = session.get_module_progress("module1")

    assert progress is not None
    assert len(progress.answers) == 1

    new_module_progress = session.get_module_progress("module2")
    assert new_module_progress is not None
    assert len(new_module_progress.answers) == 0
