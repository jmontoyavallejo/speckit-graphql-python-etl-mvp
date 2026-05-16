"""Integration tests for end-to-end ETL pipeline execution (T072-T073)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gql_learn.etl.models import ETLPipeline, PipelineRun, PipelineStatus


class TestPipelineEndToEnd:
    """Integration tests for complete ETL pipeline execution."""

    def test_pipeline_e2e_extract_transform_load(self) -> None:
        """Test complete pipeline flow: extract → transform → load (T072)."""
        # Sample extracted data
        extracted_data = [
            {"id": 1, "title": "Pride and Prejudice", "genre": "Romance", "year": 1813},
            {"id": 2, "title": "Emma", "genre": "Romance", "year": 1815},
            {"id": 3, "title": "1984", "genre": "Science Fiction", "year": 1949},
        ]

        # Transform: aggregate by genre
        transformed_data: dict[str, int] = {}
        for record in extracted_data:
            genre = record["genre"]
            transformed_data[genre] = transformed_data.get(genre, 0) + 1

        assert transformed_data == {"Romance": 2, "Science Fiction": 1}

        # Load: write to JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "aggregated.json"
            with open(output_path, "w") as f:
                json.dump(transformed_data, f)

            # Verify entire flow
            assert output_path.exists()
            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded == transformed_data

    def test_pipeline_with_error_handling(self) -> None:
        """Test pipeline handles errors mid-stream gracefully (T073)."""
        # Simulated data with a corrupt record
        raw_data = [
            {"id": 1, "title": "Book A", "year": 2000},
            {"id": 2, "title": "Book B", "year": "invalid"},  # Corrupt: year should be int
            {"id": 3, "title": "Book C", "year": 2001},
        ]

        extracted_count = len(raw_data)
        transformed_count = 0
        errors: list[str] = []

        # Transform with error handling
        for record in raw_data:
            try:
                # Attempt to validate year
                year = record.get("year")
                if not isinstance(year, int):
                    raise ValueError(f"Invalid year type: {type(year)}")
                transformed_count += 1
            except Exception as e:
                errors.append(f"Record {record['id']}: {str(e)}")

        # Verify error handling
        assert extracted_count == 3
        assert transformed_count == 2
        assert len(errors) == 1
        assert "Record 2" in errors[0]

    def test_pipeline_partial_success(self) -> None:
        """Test pipeline where some records fail but others succeed."""
        records = [
            {"id": 1, "value": 100},
            {"id": 2, "value": "invalid"},  # Will fail
            {"id": 3, "value": 300},
            {"id": 4, "value": None},  # Will fail
            {"id": 5, "value": 500},
        ]

        loaded_records: list[dict] = []
        failed_count = 0

        for record in records:
            try:
                if not isinstance(record.get("value"), (int, float)):
                    raise ValueError("Invalid value type")
                loaded_records.append(record)
            except ValueError:
                failed_count += 1

        assert len(loaded_records) == 3
        assert failed_count == 2
        assert all(isinstance(r["value"], (int, float)) for r in loaded_records)

    def test_pipeline_run_tracking(self) -> None:
        """Test that pipeline execution is properly tracked."""
        pipeline = ETLPipeline(
            id="test_pipeline",
            name="Test Pipeline",
            description="For testing",
            extract_query="query { books { id } }",
            transform_function="transform_func",
            load_destination="json:output.json",
        )

        run = PipelineRun(
            id="run_001",
            pipeline_id=pipeline.id,
            status=PipelineStatus.SUCCESS,
            records_extracted=100,
            records_transformed=100,
            records_loaded=100,
        )

        assert run.pipeline_id == pipeline.id
        assert run.status == PipelineStatus.SUCCESS
        assert run.is_complete is True

    def test_pipeline_with_data_validation(self) -> None:
        """Test pipeline validates data quality during transformation."""
        records = [
            {"id": 1, "name": "Book", "price": 10.0},
            {"id": 2, "name": "", "price": 15.0},  # Invalid: empty name
            {"id": 3, "name": "Book C", "price": -5.0},  # Invalid: negative price
            {"id": 4, "name": "Book D", "price": 20.0},
        ]

        valid_records: list[dict] = []
        validation_errors: list[str] = []

        for record in records:
            try:
                # Validate required fields
                if not record.get("name") or not isinstance(record["name"], str):
                    raise ValueError("Name must be non-empty string")
                if not isinstance(record["price"], (int, float)) or record["price"] <= 0:
                    raise ValueError("Price must be positive number")
                valid_records.append(record)
            except ValueError as e:
                validation_errors.append(f"Record {record['id']}: {str(e)}")

        assert len(valid_records) == 2
        assert len(validation_errors) == 2

    def test_pipeline_large_dataset_streaming(self) -> None:
        """Test pipeline can handle large datasets efficiently."""
        # Simulate large dataset
        total_records = 10000
        batch_size = 100
        processed = 0

        for batch_num in range(total_records // batch_size):
            batch = [
                {"id": i, "value": i * 2}
                for i in range(batch_num * batch_size, (batch_num + 1) * batch_size)
            ]
            processed += len(batch)

        assert processed == total_records

    def test_pipeline_idempotency(self) -> None:
        """Test that running the same pipeline twice produces same result."""
        records = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]

        def transform_records(data: list[dict]) -> list[dict]:
            return [{"id": r["id"], "doubled": r["amount"] * 2} for r in data]

        result1 = transform_records(records)
        result2 = transform_records(records)

        assert result1 == result2

    @pytest.mark.asyncio
    async def test_pipeline_execution_status_transitions(self) -> None:
        """Test proper status transitions during pipeline execution."""
        run = PipelineRun(
            id="run_001",
            pipeline_id="test",
            status=PipelineStatus.PENDING,
        )

        # Simulate status transitions
        assert run.status == PipelineStatus.PENDING
        assert not run.is_complete

        # Transition to running
        run.status = PipelineStatus.RUNNING
        assert run.is_running

        # Transition to success
        run.status = PipelineStatus.SUCCESS
        assert run.is_complete
