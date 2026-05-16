"""Pydantic models for Q&A modules and learning progress."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class Question(BaseModel):
    """Single question in a learning module."""

    id: str
    text: str
    explanation: str
    acceptable_answers: list[str]
    hint: str | None = None
    type: str = "multiple_choice"


class LearningModule(BaseModel):
    """Learning module containing questions."""

    id: str
    title: str
    description: str
    questions: list[Question]
    estimated_duration: int = Field(default=15, description="Duration in minutes")


class ProgressRecord(BaseModel):
    """Record of a single answer to a question."""

    module_id: str
    question_id: str
    user_answer: str
    is_correct: bool


class ModuleProgress(BaseModel):
    """Progress tracking for a module."""

    completed: bool = False
    score: int = 0
    current_question: int = 0
    answers: list[ProgressRecord] = Field(default_factory=list)


class ProgressSession(BaseModel):
    """Overall learning progress session."""

    current_module: str | None = None
    modules: dict[str, ModuleProgress] = Field(default_factory=dict)
    responses: list[ProgressRecord] = Field(default_factory=list)

    def add_response(
        self, module_id: str, question_id: str, user_answer: str, is_correct: bool
    ) -> None:
        """Add a response record to session."""
        record = ProgressRecord(
            module_id=module_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
        )
        self.responses.append(record)

        if module_id not in self.modules:
            self.modules[module_id] = ModuleProgress()

        self.modules[module_id].answers.append(record)

    def get_module_progress(self, module_id: str) -> ModuleProgress:
        """Get progress for a specific module."""
        if module_id not in self.modules:
            self.modules[module_id] = ModuleProgress()
        return self.modules[module_id]
