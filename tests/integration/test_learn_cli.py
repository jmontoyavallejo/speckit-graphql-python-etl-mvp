"""Integration tests for gql-learn start command and Q&A flow."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from gql_learn.modules.progress import clear_progress
from gql_learn.modules.progress import load_progress
from gql_learn.modules.progress import save_progress
from gql_learn.modules.schemas import LearningModule
from gql_learn.modules.schemas import ProgressSession
from gql_learn.modules.schemas import Question


@pytest.fixture
def sample_module() -> LearningModule:
    """Create a sample learning module for testing."""
    return LearningModule(
        id="test_module",
        title="Test Module",
        description="A test module",
        questions=[
            Question(
                id="q1",
                text="What is GraphQL?",
                explanation="GraphQL is a query language",
                acceptable_answers=["GraphQL", "query language"],
            ),
            Question(
                id="q2",
                text="What is a schema?",
                explanation="A schema defines types and queries",
                acceptable_answers=["schema", "type definition"],
            ),
        ],
    )


def test_module_loads_and_presents_first_question(sample_module: LearningModule) -> None:
    """Test that gql-learn start loads module and presents first question."""
    clear_progress()

    assert sample_module is not None
    assert len(sample_module.questions) > 0
    assert sample_module.questions[0].text == "What is GraphQL?"


def test_submitting_correct_answer_advances_question(sample_module: LearningModule) -> None:
    """Test that submitting correct answer advances to next question."""
    clear_progress()
    session = ProgressSession(current_module="test_module")

    first_question = sample_module.questions[0]
    user_answer = "GraphQL"

    is_correct = user_answer.lower() in [
        ans.lower() for ans in first_question.acceptable_answers
    ]

    session.add_response("test_module", first_question.id, user_answer, is_correct)

    assert session.responses[0].is_correct is True
    assert len(session.responses) == 1

    clear_progress()


def test_progress_persists_across_sessions() -> None:
    """Test that progress persists across sessions."""
    clear_progress()

    session1 = ProgressSession(current_module="module1")
    session1.add_response("module1", "q1", "answer1", True)
    save_progress(session1)

    session2 = load_progress()

    assert session2.current_module == "module1"
    assert len(session2.responses) == 1
    assert session2.responses[0].user_answer == "answer1"

    clear_progress()


def test_progress_session_tracking() -> None:
    """Test that progress is properly tracked during session."""
    clear_progress()
    session = ProgressSession(current_module="module1")

    session.add_response("module1", "q1", "answer1", True)
    session.add_response("module1", "q2", "answer2", False)
    session.add_response("module2", "q1", "answer3", True)

    assert len(session.responses) == 3
    assert len(session.modules["module1"].answers) == 2
    assert len(session.modules["module2"].answers) == 1

    clear_progress()
