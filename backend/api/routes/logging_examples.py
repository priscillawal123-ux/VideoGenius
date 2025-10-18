"""
Example usage of structured logging in Video Genius API routes.

This demonstrates how to use the structured logging system for
tracking operations, errors, and performance metrics.
"""

from fastapi import APIRouter, HTTPException
from backend.core.logging_config import logger

router = APIRouter(prefix="/api/v1/logging-examples", tags=["examples"])


@router.get("/log-info")
async def log_info_example():
    """Example: Log information message."""
    logger.info(
        "Processing request",
        extra={
            "endpoint": "/log-info",
            "request_type": "GET",
        },
    )
    return {"message": "Info logged successfully"}


@router.get("/log-warning")
async def log_warning_example():
    """Example: Log warning message."""
    logger.warning(
        "Unusual behavior detected",
        extra={
            "behavior": "high_request_rate",
            "requests_per_second": 1000,
        },
    )
    return {"message": "Warning logged successfully"}


@router.get("/log-error")
async def log_error_example():
    """Example: Log error message."""
    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error(
            "Arithmetic error occurred",
            extra={
                "operation": "division",
                "divisor": 0,
            },
            exc_info=True,
        )
    return {"message": "Error logged successfully"}


@router.get("/log-task-operation/{task_id}")
async def log_task_operation_example(task_id: str):
    """Example: Log task operation."""
    logger.log_task_operation(
        operation="update",
        task_id=task_id,
        status="success",
        duration_ms=245.5,
        user_id="user_123",
    )
    return {"message": f"Task {task_id} operation logged"}


@router.get("/log-database-query")
async def log_database_query_example():
    """Example: Log database query."""
    logger.log_database_query(
        query_type="SELECT",
        table="tasks",
        duration_ms=45.3,
        rows_affected=21,
    )
    return {"message": "Database query logged successfully"}


@router.get("/log-request-example")
async def log_request_example():
    """Example: Log HTTP request."""
    logger.log_request(
        method="GET",
        path="/api/v1/tasks",
        status_code=200,
        duration_ms=100.5,
        user_id="user_456",
    )
    return {"message": "Request logged successfully"}


@router.get("/log-context-error")
async def log_context_error_example():
    """Example: Log error with context."""
    try:
        raise ValueError("Invalid task status")
    except ValueError as e:
        logger.log_error_with_context(
            e,
            {
                "task_id": "task_abc123",
                "attempted_status": "invalid_status",
                "valid_statuses": ["open", "in_progress", "closed"],
            },
        )
    return {"message": "Error with context logged successfully"}


@router.get("/performance-test")
async def performance_test():
    """Example: Log performance metrics."""
    import time

    start = time.time()

    # Simulate processing
    time.sleep(0.1)

    duration_ms = (time.time() - start) * 1000

    logger.info(
        "Performance test completed",
        extra={
            "operation": "heavy_computation",
            "duration_ms": duration_ms,
            "status": "completed",
        },
    )

    return {
        "message": "Performance test completed",
        "duration_ms": duration_ms,
    }


@router.get("/structured-log-test")
async def structured_log_test():
    """Example: Multiple structured log entries."""

    # Log operation start
    logger.info(
        "Starting complex operation",
        extra={
            "operation": "data_processing",
            "phase": "start",
        },
    )

    # Simulate work
    import time
    time.sleep(0.05)

    # Log progress
    logger.info(
        "Operation progress",
        extra={
            "operation": "data_processing",
            "phase": "in_progress",
            "progress_percent": 50,
        },
    )

    # Simulate more work
    time.sleep(0.05)

    # Log completion
    logger.info(
        "Operation completed",
        extra={
            "operation": "data_processing",
            "phase": "complete",
            "records_processed": 1000,
            "duration_ms": 100,
        },
    )

    return {
        "message": "Complex operation completed",
        "records_processed": 1000,
    }
