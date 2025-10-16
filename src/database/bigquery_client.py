"""
BigQuery client for backward compatibility.
"""

import time
import uuid
from typing import Any, Dict, List, Optional

from src.database.constants import QueryType
from src.database.dependencies import get_database_config, get_database_service
from src.database.schemas import QueryRequest
from src.database.service import DatabaseService


class BigQueryClient:
    """BigQuery client wrapper for backward compatibility."""

    def __init__(
        self, project_id: str = "default-project", dataset_id: str = "default-dataset"
    ):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self._service: Optional[DatabaseService] = None

    async def get_service(self) -> DatabaseService:
        """Get database service instance."""
        if self._service is None:
            config = get_database_config()
            self._service = get_database_service(config)
        return self._service

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a BigQuery query."""
        service = await self.get_service()
        request = QueryRequest(
            query=query, parameters=parameters or {}, query_type=QueryType.SELECT
        )
        result = await service.execute_query(request)

        if result.success and result.data:
            return result.data
        return []

    async def insert_row(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a row into BigQuery table."""
        # This would construct an INSERT query
        # For now, return mock success
        return True

    async def update_row(
        self, table: str, data: Dict[str, Any], where_clause: str
    ) -> bool:
        """Update a row in BigQuery table."""
        # This would construct an UPDATE query
        # For now, return mock success
        return True

    async def get_video_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get video job by ID."""
        query = f"SELECT * FROM video_jobs WHERE job_id = '{job_id}'"
        results = await self.execute_query(query)
        return results[0] if results else None

    async def create_video_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new video job."""
        # Mock job creation
        job_id = f"job_{len(job_data)}"
        return job_id

    async def query_single_row(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute query and return single row."""
        results = await self.execute_query(query, parameters)
        return results[0] if results else None

    async def create_job_record(self, job_data: Dict[str, Any]) -> str:
        """Create a new job record."""
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"

        # Add job_id to data
        job_data["job_id"] = job_id
        job_data["created_at"] = time.time()
        job_data["updated_at"] = time.time()

        # Insert into database (mock for now)
        await self.insert_row("video_jobs", job_data)
        return job_id

    async def update_job_status(
        self, job_id: str, status: str, error: Optional[str] = None
    ) -> bool:
        """Update job status."""
        update_data = {"status": status, "updated_at": time.time()}
        if error:
            update_data["error"] = error

        where_clause = f"job_id = '{job_id}'"
        return await self.update_row("video_jobs", update_data, where_clause)

    async def update_job_data(self, job_id: str, data: Dict[str, Any]) -> bool:
        """Update job data."""
        data["updated_at"] = time.time()
        where_clause = f"job_id = '{job_id}'"
        return await self.update_row("video_jobs", data, where_clause)
