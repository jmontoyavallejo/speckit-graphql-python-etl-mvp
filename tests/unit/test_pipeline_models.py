"""Unit tests for ETL Pipeline and PipelineRun models (T071)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from gql_learn.etl.models import ETLPipeline, PipelineRun, PipelineStatus


class TestETLPipelineModel:
    """Tests for ETLPipeline model validation."""

    def test_pipeline_creation_valid(self) -> None:
        """Test creating a valid ETLPipeline."""
        pipeline = ETLPipeline(
            id="sample_library_etl",
            name="Library ETL",
            description="Extract books from GraphQL",
            extract_query="query { books { id title } }",
            transform_function="gql_learn.etl.transforms.aggregate_by_genre",
            load_destination="json:output.json",
            is_builtin=True,
        )

        assert pipeline.id == "sample_library_etl"
        assert pipeline.name == "Library ETL"
        assert pipeline.is_builtin is True
        assert pipeline.created_at is not None

    def test_pipeline_creation_with_sqlite_destination(self) -> None:
        """Test pipeline with SQLite load destination."""
        pipeline = ETLPipeline(
            id="etl_sqlite",
            name="SQLite Pipeline",
            description="Load to SQLite",
            extract_query="query { books { id } }",
            transform_function="gql_learn.etl.transforms.passthrough",
            load_destination="sqlite:data.db",
            is_builtin=False,
        )

        assert "sqlite:" in pipeline.load_destination

    def test_pipeline_empty_extract_query_invalid(self) -> None:
        """Test that empty extract query raises validation error."""
        with pytest.raises(ValueError):
            ETLPipeline(
                id="invalid",
                name="Invalid",
                description="Bad",
                extract_query="",
                transform_function="func",
                load_destination="json:out.json",
            )

    def test_pipeline_invalid_destination_type(self) -> None:
        """Test that invalid destination type raises error."""
        with pytest.raises(ValueError):
            ETLPipeline(
                id="bad_dest",
                name="Bad Destination",
                description="Invalid destination",
                extract_query="query { books { id } }",
                transform_function="func",
                load_destination="s3://bucket/path",  # S3 not allowed
            )

    def test_pipeline_destination_formats(self) -> None:
        """Test valid destination format types."""
        valid_destinations = [
            "json:output.json",
            "csv:output.csv",
            "sqlite:data.db",
        ]

        for dest in valid_destinations:
            pipeline = ETLPipeline(
                id="test",
                name="Test",
                description="Test",
                extract_query="query { x }",
                transform_function="func",
                load_destination=dest,
            )
            assert pipeline.load_destination == dest


class TestPipelineRunModel:
    """Tests for PipelineRun model validation and state management."""

    def test_pipeline_run_creation_pending(self) -> None:
        """Test creating a pending PipelineRun."""
        run = PipelineRun(
            id="run_001",
            pipeline_id="sample_library_etl",
            status=PipelineStatus.PENDING,
            records_extracted=0,
            records_transformed=0,
            records_loaded=0,
        )

        assert run.id == "run_001"
        assert run.status == PipelineStatus.PENDING
        assert run.completed_at is None
        assert run.duration_seconds is None
        assert run.errors == []

    def test_pipeline_run_successful_completion(self) -> None:
        """Test marking a pipeline run as successful."""
        started = datetime.utcnow()
        completed = started + timedelta(seconds=17)

        run = PipelineRun(
            id="run_success",
            pipeline_id="sample_library_etl",
            status=PipelineStatus.SUCCESS,
            records_extracted=15,
            records_transformed=15,
            records_loaded=15,
            started_at=started,
            completed_at=completed,
        )

        assert run.status == PipelineStatus.SUCCESS
        assert run.records_extracted == 15
        assert run.records_loaded == 15
        assert run.duration_seconds == 17

    def test_pipeline_run_failed_with_errors(self) -> None:
        """Test pipeline run with failures and error messages."""
        run = PipelineRun(
            id="run_failed",
            pipeline_id="sample_library_etl",
            status=PipelineStatus.FAILED,
            records_extracted=15,
            records_transformed=10,
            records_loaded=8,
            errors=[
                "Record 11: ValidationError - missing required field 'title'",
                "Record 12: TypeError - cannot convert year to int",
            ],
        )

        assert run.status == PipelineStatus.FAILED
        assert len(run.errors) == 2
        assert run.records_extracted > run.records_loaded

    def test_pipeline_run_validation_completed_at_only_when_done(self) -> None:
        """Test that completed_at is only set when status is success or failed."""
        # Pending run should not have completed_at
        pending_run = PipelineRun(
            id="pending",
            pipeline_id="test",
            status=PipelineStatus.PENDING,
        )
        assert pending_run.completed_at is None

        # Running run should not have completed_at
        running_run = PipelineRun(
            id="running",
            pipeline_id="test",
            status=PipelineStatus.RUNNING,
        )
        assert running_run.completed_at is None

        # Failed run should have completed_at
        now = datetime.utcnow()
        failed_run = PipelineRun(
            id="failed",
            pipeline_id="test",
            status=PipelineStatus.FAILED,
            completed_at=now,
        )
        assert failed_run.completed_at == now

    def test_pipeline_run_records_counts_non_negative(self) -> None:
        """Test that record counts cannot be negative."""
        with pytest.raises(ValueError):
            PipelineRun(
                id="invalid",
                pipeline_id="test",
                status=PipelineStatus.PENDING,
                records_extracted=-1,  # Invalid
            )

        with pytest.raises(ValueError):
            PipelineRun(
                id="invalid",
                pipeline_id="test",
                status=PipelineStatus.PENDING,
                records_loaded=-1,  # Invalid
            )

    def test_pipeline_run_status_enum(self) -> None:
        """Test that all valid pipeline statuses are recognized."""
        valid_statuses = [
            PipelineStatus.PENDING,
            PipelineStatus.RUNNING,
            PipelineStatus.SUCCESS,
            PipelineStatus.FAILED,
        ]

        for status in valid_statuses:
            run = PipelineRun(
                id="test",
                pipeline_id="test",
                status=status,
            )
            assert run.status == status

    def test_pipeline_run_with_partial_success(self) -> None:
        """Test pipeline run where some records failed but others succeeded."""
        run = PipelineRun(
            id="partial",
            pipeline_id="sample_library_etl",
            status=PipelineStatus.SUCCESS,
            records_extracted=100,
            records_transformed=98,  # 2 failed transformation
            records_loaded=98,
            errors=["Record 45: Transform failed", "Record 72: Transform failed"],
        )

        assert run.status == PipelineStatus.SUCCESS
        assert run.records_extracted - run.records_transformed == 2
        assert len(run.errors) > 0
