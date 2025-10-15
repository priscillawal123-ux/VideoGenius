"""
BigQuery client for data operations with Google Cloud best practices.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, cast

from google.api_core import exceptions, retry
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return (
            asyncio.get_event_loop().time() - self.last_failure_time
        ) > self.recovery_timeout

    def _on_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class BigQueryClient:
    """Client for BigQuery operations with optimization and resilience."""

    def __init__(self, project_id: str, dataset_id: str):
        """Initialize BigQuery client with optimized settings.

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self._client: Optional[bigquery.Client] = None
        self._circuit_breaker: Optional[CircuitBreaker] = None

    @property
    def client(self) -> bigquery.Client:
        """Lazy initialize BigQuery client."""
        if self._client is None:
            # Configure retry strategy for resilience
            retry_config = retry.Retry(
                initial=1.0,
                maximum=16.0,
                multiplier=2.0,
                deadline=60.0,
                predicate=retry.if_exception_type(
                    exceptions.ServiceUnavailable,
                    exceptions.TooManyRequests,
                    exceptions.InternalServerError,
                ),
            )

            self._client = bigquery.Client(project=self.project_id)
            self._client._http._retry = retry_config
        return self._client

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Lazy initialize circuit breaker."""
        if self._circuit_breaker is None:
            self._circuit_breaker = CircuitBreaker()
        return self._circuit_breaker

    async def insert_row(self, table_id: str, row: Dict[str, Any]) -> str:
        """Insert a row into BigQuery table with circuit breaker protection.

        Args:
            table_id: Table name
            row: Data to insert

        Returns:
            Inserted row ID

        Raises:
            ValueError: If insertion fails
        """

        async def _insert() -> str:
            table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"

            try:
                errors = self.client.insert_rows_json(table_ref, [row])
                if errors:
                    raise ValueError(f"Insert failed: {errors}")

                logger.info(f"Row inserted into {table_id}")
                return str(row.get("id", "unknown"))
            except exceptions.GoogleAPIError as e:
                logger.error(f"BigQuery error: {e}")
                raise ValueError(f"Failed to insert: {e}") from e

        return cast(str, await self.circuit_breaker.call(_insert))

    async def query_data(
        self,
        query: str,
        parameters: Optional[List[bigquery.ScalarQueryParameter]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results.

        Args:
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            ValueError: If query fails
        """
        try:
            job_config = bigquery.QueryJobConfig()
            if parameters:
                job_config.query_parameters = parameters

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            rows = []
            for row in results:
                rows.append(dict(row))

            logger.info(f"Query executed, returned {len(rows)} rows")
            return rows

        except exceptions.GoogleAPIError as e:
            logger.error(f"Query error: {e}")
            raise ValueError(f"Failed to execute query: {e}") from e

    async def create_job_record(
        self, job_type: str, parameters: Dict[str, Any], user_id: Optional[str] = None
    ) -> str:
        """Create a job record in BigQuery.

        Args:
            job_type: Type of job (video_generation, etc.)
            parameters: Job parameters
            user_id: User who initiated the job

        Returns:
            Job ID

        Raises:
            ValueError: If job creation fails
        """
        import uuid

        job_id = str(uuid.uuid4())

        # Extract parameters for individual fields
        topic = parameters.get("topic")
        duration_seconds = parameters.get("duration_seconds")
        style = parameters.get("style")

        job_record = {
            "job_id": job_id,
            "user_id": user_id or "anonymous",
            "status": "queued",
            "topic": topic,
            "duration_seconds": duration_seconds,
            "style": style,
            "created_at": "AUTO",
            "updated_at": "AUTO",
        }

        await self.insert_row("video_jobs", job_record)
        logger.info(f"Job record created: {job_id}")
        return job_id

    async def update_job_status(
        self, job_id: str, status: str, error: Optional[str] = None
    ) -> None:
        """Update job status.

        Args:
            job_id: Job ID to update
            status: New status
            error: Error message if status is 'failed'
        """
        update_data = {"status": status, "updated_at": "AUTO"}

        if error:
            update_data["error"] = error

        # Note: This would need a proper UPDATE query in production
        # For now, we'll log the update
        logger.info(f"Job {job_id} status updated to {status}")

    async def update_job_data(self, job_id: str, data: Dict[str, Any]) -> None:
        """Update job data.

        Args:
            job_id: Job ID to update
            data: Data to update
        """
        # Note: This would need a proper UPDATE query in production
        # For now, we'll log the update
        logger.info(f"Job {job_id} data updated: {list(data.keys())}")

    async def query_single_row(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row.

        Args:
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            Single result row or None if not found
        """
        try:
            # Convert dict parameters to ScalarQueryParameter list
            param_list = None
            if parameters:
                param_list = [
                    bigquery.ScalarQueryParameter(key, "STRING", value)
                    for key, value in parameters.items()
                ]

            results = await self.query_data(query, param_list)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Single row query failed: {e}")
            return None

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details by ID.

        Args:
            job_id: Job ID to retrieve

        Returns:
            Job data or None if not found
        """
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.video_jobs`
            WHERE job_id = @job_id
            LIMIT 1
            """

            parameters = [bigquery.ScalarQueryParameter("job_id", "STRING", job_id)]

            results = await self.query_data(query, parameters)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
