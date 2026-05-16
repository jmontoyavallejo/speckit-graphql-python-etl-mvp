"""ETL pipeline execution orchestrator (T079-T080)."""

from __future__ import annotations

import importlib
import logging
from datetime import datetime
from typing import Any, Callable

from gql_learn.etl.extract import extract_graphql
from gql_learn.etl.models import ETLPipeline, PipelineRun, PipelineStatus

logger = logging.getLogger(__name__)


def load_transform_function(function_path: str) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    """Dynamically load a transform function from a module path.

    Args:
        function_path: Module path to callable (e.g., 'gql_learn.etl.transform.aggregate_by_genre')

    Returns:
        The loaded callable

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If function cannot be found in module
    """
    parts = function_path.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid function path: {function_path}")

    module_name, function_name = parts

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        if not callable(func):
            raise AttributeError(f"{function_path} is not callable")
        return func
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot load transform function {function_path}: {e}")


async def execute_pipeline(
    pipeline: ETLPipeline,
    graphql_endpoint: str,
    load_function: Callable[[list[dict[str, Any]], str], int],
) -> PipelineRun:
    """Execute a complete ETL pipeline: extract → transform → load.

    Args:
        pipeline: ETLPipeline configuration
        graphql_endpoint: URL to GraphQL server
        load_function: Function to handle loading (maps destination type to load function)

    Returns:
        PipelineRun with execution results

    Raises:
        Various: Based on extraction, transformation, or loading failures
    """
    run = PipelineRun(
        pipeline_id=pipeline.id,
        status=PipelineStatus.RUNNING,
        started_at=datetime.utcnow(),
    )

    try:
        # EXTRACT
        logger.info(f"Extracting data from {graphql_endpoint}")
        extracted_records = await extract_graphql(graphql_endpoint, pipeline.extract_query)
        run.records_extracted = len(extracted_records)
        logger.info(f"Extracted {run.records_extracted} records")

        # TRANSFORM
        logger.info(f"Transforming records using {pipeline.transform_function}")
        transform_func = load_transform_function(pipeline.transform_function)
        transformed_records = await transform_records_with_error_handling(
            extracted_records, transform_func, run
        )
        run.records_transformed = len(transformed_records)
        logger.info(f"Transformed {run.records_transformed} records")

        # LOAD
        logger.info(f"Loading {len(transformed_records)} records to {pipeline.load_destination}")
        records_loaded = load_function(transformed_records, pipeline.load_destination)
        run.records_loaded = records_loaded
        logger.info(f"Loaded {run.records_loaded} records")

        # Update status
        run.status = PipelineStatus.SUCCESS
        run.completed_at = datetime.utcnow()

        logger.info(f"Pipeline {pipeline.id} completed successfully")
        return run

    except Exception as e:
        logger.exception(f"Pipeline {pipeline.id} failed: {e}")
        run.status = PipelineStatus.FAILED
        run.completed_at = datetime.utcnow()
        run.errors.append(f"Pipeline execution failed: {str(e)}")
        return run


async def transform_records_with_error_handling(
    records: list[dict[str, Any]],
    transform_func: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    run: PipelineRun,
    stop_on_error: bool = False,
) -> list[dict[str, Any]]:
    """Transform records with per-record error handling.

    Args:
        records: Records to transform
        transform_func: Transformation function
        run: PipelineRun to log errors to
        stop_on_error: If True, stop on first error; if False, continue and log

    Returns:
        List of successfully transformed records

    Raises:
        Exception: If stop_on_error is True and an error occurs
    """
    try:
        # Try to transform all records at once
        transformed = transform_func(records)
        return transformed
    except Exception as e:
        if stop_on_error:
            logger.error(f"Transformation failed (stop_on_error=True): {e}")
            run.errors.append(f"Transformation failed: {str(e)}")
            raise

        # Fall back to per-record transformation
        logger.warning(
            f"Bulk transformation failed, attempting per-record: {e}"
        )
        transformed = []
        for i, record in enumerate(records):
            try:
                result = transform_func([record])
                if result:
                    transformed.extend(result)
            except Exception as record_error:
                error_msg = (
                    f"Record {i}: transformation failed: {str(record_error)}"
                )
                logger.warning(error_msg)
                run.errors.append(error_msg)

        return transformed


def get_load_function(
    destination: str,
) -> Callable[[list[dict[str, Any]], str], int]:
    """Get appropriate load function based on destination type.

    Args:
        destination: Destination string (e.g., 'json:output.json', 'sqlite:data.db')

    Returns:
        Load function appropriate for destination

    Raises:
        ValueError: If destination type is not supported
    """
    dest_type, dest_path = destination.split(":", 1)

    if dest_type == "json":
        from gql_learn.etl.load import load_json
        return lambda records, path: load_json(records, path)
    elif dest_type == "csv":
        from gql_learn.etl.load import load_csv
        return lambda records, path: load_csv(records, path)
    elif dest_type == "sqlite":
        from gql_learn.etl.load import load_sqlite
        return lambda records, path: load_sqlite(records, path, "records")
    else:
        raise ValueError(f"Unsupported load destination type: {dest_type}")
