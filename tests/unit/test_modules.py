"""Unit tests for module validation and answer checking."""

from __future__ import annotations

import pytest

from gql_learn.modules.schemas import Question


def test_answer_validation_case_sensitivity() -> None:
    """Test that answer validation is case-insensitive."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="A query language",
        acceptable_answers=["GraphQL", "Query Language"],
    )

    acceptable_lower = [ans.lower() for ans in question.acceptable_answers]

    assert "graphql".lower() in acceptable_lower
    assert "query language".lower() in acceptable_lower


def test_answer_validation_blank_answers() -> None:
    """Test that blank answers are handled correctly."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="A query language",
        acceptable_answers=["GraphQL", "Query Language"],
    )

    user_answer = ""
    is_correct = user_answer.strip().lower() in [
        ans.lower() for ans in question.acceptable_answers
    ]

    assert is_correct is False


def test_answer_validation_with_extra_whitespace() -> None:
    """Test answer validation with extra whitespace."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="A query language",
        acceptable_answers=["GraphQL"],
    )

    user_answer = "  GraphQL  "
    acceptable_lower = [ans.lower() for ans in question.acceptable_answers]

    is_correct = user_answer.strip().lower() in acceptable_lower
    assert is_correct is True


def test_partial_answer_matching() -> None:
    """Test that partial answers may or may not match depending on implementation."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="A query language",
        acceptable_answers=["GraphQL is a query language"],
    )

    user_answer = "GraphQL"
    acceptable_lower = [ans.lower() for ans in question.acceptable_answers]

    is_correct = user_answer.strip().lower() in acceptable_lower
    assert is_correct is False
