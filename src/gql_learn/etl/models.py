"""ETL Pipeline and PipelineRun Pydantic models (T075)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class PipelineStatus(str, Enum):
    """Valid pipeline execution statuses."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ETLPipeline(BaseModel):
    """Metadata for an ETL workflow."""

    id: str
    name: str
    description: str
    extract_query: str
    transform_function: str
    load_destination: str
    is_builtin: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("extract_query")
    @classmethod
    def extract_query_not_empty(cls, v: str) -> str:
        """Validate that extract_query is not empty."""
        if not v or not v.strip():
            raise ValueError("extract_query cannot be empty")
        return v

    @field_validator("load_destination")
    @classmethod
    def validate_load_destination(cls, v: str) -> str:
        """Validate that load_destination has valid format and type."""
        if not v or ":" not in v:
            raise ValueError(
                "load_destination must be in format 'type:path' (e.g., 'json:output.json')"
            )

        dest_type = v.split(":")[0]
        valid_types = {"json", "csv", "sqlite"}
        if dest_type not in valid_types:
            raise ValueError(
                f"load_destination type must be one of {valid_types}, got '{dest_type}'"
            )

        return v

    class Config:
        """Pydantic config."""

        use_enum_values = False


class PipelineRun(BaseModel):
    """Record of a single execution of an ETL pipeline."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    @field_validator("records_extracted", "records_transformed", "records_loaded")
    @classmethod
    def record_counts_non_negative(cls, v: int) -> int:
        """Validate that record counts are non-negative."""
        if v < 0:
            raise ValueError("Record counts cannot be negative")
        return v

    @model_validator(mode="after")
    def calculate_duration_after_init(self) -> PipelineRun:
        """Calculate duration_seconds from started_at and completed_at if not provided."""
        if self.duration_seconds is None and self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()
        return self

    @property
    def is_complete(self) -> bool:
        """Check if pipeline run has completed."""
        return self.status in (PipelineStatus.SUCCESS, PipelineStatus.FAILED)

    @property
    def is_running(self) -> bool:
        """Check if pipeline run is currently executing."""
        return self.status == PipelineStatus.RUNNING

    class Config:
        """Pydantic config."""

        use_enum_values = False
