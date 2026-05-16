"""Module loading from JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gql_learn.modules.schemas import LearningModule


def load_module(module_id: str) -> LearningModule:
    """Load a learning module from JSON file.

    Args:
        module_id: Module identifier (e.g., '01_schema_types')

    Returns:
        Loaded LearningModule instance

    Raises:
        FileNotFoundError: If module file not found
        ValueError: If module JSON is invalid
    """
    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "modules"
    module_file = data_dir / f"{module_id}.json"

    if not module_file.exists():
        raise FileNotFoundError(f"Module file not found: {module_file}")

    try:
        with open(module_file) as f:
            data: dict[str, Any] = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {module_file}: {e}")

    return LearningModule(**data)


def list_modules() -> list[str]:
    """List all available module IDs."""
    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "modules"

    if not data_dir.exists():
        return []

    modules = []
    for file in sorted(data_dir.glob("*.json")):
        modules.append(file.stem)

    return modules
