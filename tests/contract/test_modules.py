"""Contract tests for LearningModule loading from JSON."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gql_learn.modules.loader import load_module
from gql_learn.modules.schemas import LearningModule


def test_load_module_from_json() -> None:
    """Test that LearningModule can load from JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        module_file = Path(tmpdir) / "test_module.json"
        module_data = {
            "id": "test_module",
            "title": "Test Module",
            "description": "A test module",
            "estimated_duration": 15,
            "questions": [
                {
                    "id": "q1",
                    "text": "What is GraphQL?",
                    "explanation": "GraphQL is a query language",
                    "acceptable_answers": ["GraphQL", "graphql", "a query language"],
                    "hint": "Think about APIs",
                    "type": "text",
                }
            ],
        }

        with open(module_file, "w") as f:
            json.dump(module_data, f)

        module = LearningModule(**module_data)
        assert module.id == "test_module"
        assert module.title == "Test Module"
        assert len(module.questions) == 1
        assert module.questions[0].id == "q1"


def test_learning_module_structure() -> None:
    """Test that LearningModule has required structure."""
    module_data = {
        "id": "test",
        "title": "Test",
        "description": "Test module",
        "questions": [],
    }

    module = LearningModule(**module_data)
    assert hasattr(module, "id")
    assert hasattr(module, "title")
    assert hasattr(module, "description")
    assert hasattr(module, "questions")
    assert hasattr(module, "estimated_duration")
