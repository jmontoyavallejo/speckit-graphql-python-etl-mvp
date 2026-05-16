"""Learning modules system with Q&A, progress tracking, and loaders."""

from __future__ import annotations

from gql_learn.modules.loader import list_modules
from gql_learn.modules.loader import load_module
from gql_learn.modules.progress import clear_progress
from gql_learn.modules.progress import load_progress
from gql_learn.modules.progress import save_progress
from gql_learn.modules.schemas import LearningModule
from gql_learn.modules.schemas import ModuleProgress
from gql_learn.modules.schemas import ProgressRecord
from gql_learn.modules.schemas import ProgressSession
from gql_learn.modules.schemas import Question

__all__ = [
    "LearningModule",
    "Question",
    "ProgressSession",
    "ModuleProgress",
    "ProgressRecord",
    "load_module",
    "list_modules",
    "load_progress",
    "save_progress",
    "clear_progress",
]
