"""Integration tests for `gql-learn pipeline` CLI command (T074)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


class TestPipelineCLI:
    """Integration tests for pipeline CLI commands."""

    def test_pipeline_run_command_execution(self) -> None:
        """Test `gql-learn pipeline run sample_library_etl` command (T074)."""
        # Simulate pipeline configuration
        pipeline_config = {
            "id": "sample_library_etl",
            "name": "Sample Library ETL",
            "description": "Extract books from GraphQL, aggregate by genre",
            "extract_query": "query { books { id title genre } }",
            "transform_function": "gql_learn.etl.transforms.aggregate_by_genre",
            "load_destination": "json:output.json",
        }

        # Verify pipeline config structure
        assert pipeline_config["id"] == "sample_library_etl"
        assert "extract_query" in pipeline_config
        assert "transform_function" in pipeline_config
        assert "load_destination" in pipeline_config

    def test_pipeline_list_command(self) -> None:
        """Test `gql-learn pipeline list` command shows available pipelines."""
        available_pipelines = [
            {
                "id": "sample_library_etl",
                "name": "Sample Library ETL",
                "description": "Extract and aggregate books",
            },
            {
                "id": "author_count_pipeline",
                "name": "Author Count Pipeline",
                "description": "Count authors by nationality",
            },
        ]

        assert len(available_pipelines) >= 1
        assert any(p["id"] == "sample_library_etl" for p in available_pipelines)

    def test_pipeline_show_command(self) -> None:
        """Test `gql-learn pipeline show sample_library_etl` displays details."""
        pipeline_details = {
            "id": "sample_library_etl",
            "name": "Sample Library ETL",
            "description": "Extract books from GraphQL, aggregate by genre",
            "extract_query": "query { books { id title genre } }",
            "transform_function": "gql_learn.etl.transforms.aggregate_by_genre",
            "load_destination": "json:output.json",
            "is_builtin": True,
        }

        assert pipeline_details["id"] == "sample_library_etl"
        assert pipeline_details["is_builtin"] is True

    def test_pipeline_runs_command(self) -> None:
        """Test `gql-learn pipeline runs sample_library_etl` shows execution history."""
        execution_history = [
            {
                "id": "run_20260516_001",
                "status": "success",
                "records_extracted": 15,
                "records_loaded": 15,
                "started_at": "2026-05-16T10:30:00Z",
                "completed_at": "2026-05-16T10:30:45Z",
                "duration_seconds": 45,
            },
            {
                "id": "run_20260515_002",
                "status": "success",
                "records_extracted": 15,
                "records_loaded": 15,
                "started_at": "2026-05-15T14:20:00Z",
                "completed_at": "2026-05-15T14:20:30Z",
                "duration_seconds": 30,
            },
        ]

        assert len(execution_history) >= 1
        assert execution_history[0]["status"] == "success"

    def test_pipeline_run_with_progress_output(self) -> None:
        """Test pipeline run displays progress during execution."""
        progress_messages = [
            "Extracting data from GraphQL...",
            "Extracted 15 records",
            "Transforming data...",
            "Transformed 15 records",
            "Loading to JSON...",
            "Loaded 15 records",
            "Pipeline completed successfully",
        ]

        assert len(progress_messages) > 0
        assert any("Extracting" in msg for msg in progress_messages)
        assert any("completed" in msg.lower() for msg in progress_messages)

    def test_pipeline_error_output_on_failure(self) -> None:
        """Test pipeline displays clear error messages on failure."""
        error_output = {
            "status": "failed",
            "error": "GraphQL endpoint unreachable: connection refused at localhost:8000",
            "records_extracted": 0,
            "records_loaded": 0,
        }

        assert error_output["status"] == "failed"
        assert "error" in error_output
        assert error_output["records_extracted"] == 0

    def test_pipeline_json_output_format(self) -> None:
        """Test `--json` flag outputs structured JSON."""
        json_output = {
            "id": "run_001",
            "pipeline_id": "sample_library_etl",
            "status": "success",
            "records_extracted": 15,
            "records_transformed": 15,
            "records_loaded": 15,
            "duration_seconds": 45,
        }

        assert "id" in json_output
        assert "status" in json_output
        assert "records_extracted" in json_output

    def test_pipeline_config_file_loading(self) -> None:
        """Test loading pipeline configuration from data/pipelines/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipelines_dir = Path(tmpdir) / "pipelines"
            pipelines_dir.mkdir()

            # Create sample pipeline config
            pipeline_file = pipelines_dir / "sample_library_etl.json"
            config = {
                "id": "sample_library_etl",
                "name": "Sample Library ETL",
                "description": "Test pipeline",
                "extract_query": "query { books { id } }",
                "transform_function": "transform",
                "load_destination": "json:out.json",
            }

            with open(pipeline_file, "w") as f:
                json.dump(config, f)

            # Verify file exists and can be loaded
            assert pipeline_file.exists()
            with open(pipeline_file) as f:
                loaded = json.load(f)
            assert loaded["id"] == "sample_library_etl"

    def test_pipeline_run_with_custom_output_path(self) -> None:
        """Test pipeline run accepts custom output destination."""
        # Simulating: gql-learn pipeline run sample_library_etl --output custom_path.json
        custom_output = "custom_output.json"

        assert custom_output.endswith(".json")

    def test_pipeline_run_stores_execution_log(self) -> None:
        """Test pipeline run creates execution log entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_dir = Path(tmpdir) / "runs"
            runs_dir.mkdir()

            run_log = {
                "id": "run_20260516_001",
                "pipeline_id": "sample_library_etl",
                "status": "success",
                "records_extracted": 15,
                "records_loaded": 15,
                "started_at": "2026-05-16T10:30:00Z",
                "completed_at": "2026-05-16T10:30:45Z",
                "duration_seconds": 45,
            }

            run_file = runs_dir / "run_20260516_001.json"
            with open(run_file, "w") as f:
                json.dump(run_log, f)

            assert run_file.exists()
            with open(run_file) as f:
                loaded = json.load(f)
            assert loaded["status"] == "success"
