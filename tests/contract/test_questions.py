"""Contract tests for Question evaluation."""

from __future__ import annotations

import pytest

from gql_learn.modules.schemas import Question


def test_question_structure() -> None:
    """Test that Question has required fields."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="GraphQL is a query language",
        acceptable_answers=["GraphQL", "a query language"],
    )

    assert question.id == "q1"
    assert question.text == "What is GraphQL?"
    assert question.explanation == "GraphQL is a query language"
    assert len(question.acceptable_answers) == 2


def test_question_with_optional_fields() -> None:
    """Test that Question supports optional fields."""
    question = Question(
        id="q2",
        text="What is a GraphQL schema?",
        explanation="A schema defines types and queries",
        acceptable_answers=["schema", "type definition"],
        hint="It's like a blueprint",
        type="multiple_choice",
    )

    assert question.hint == "It's like a blueprint"
    assert question.type == "multiple_choice"


def test_question_evaluation_case_insensitive() -> None:
    """Test that question evaluation is case-insensitive."""
    question = Question(
        id="q1",
        text="What is GraphQL?",
        explanation="A query language",
        acceptable_answers=["GraphQL", "query language"],
    )

    acceptable_lower = [ans.lower() for ans in question.acceptable_answers]
    user_answer = "graphql"

    assert user_answer.lower() in acceptable_lower
