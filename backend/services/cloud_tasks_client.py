"""Cloud Tasks client for asynchronous job queuing."""

from typing import Dict, Any, Optional, cast
import logging
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import json

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CloudTasksClient:
    """Client for Google Cloud Tasks operations."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        queue_name: str = "video-generation-queue",
    ):
        """Initialize Cloud Tasks client.

        Args:
            project_id: GCP project ID
            location: GCP region for the queue
            queue_name: Name of the Cloud Tasks queue
        """
        self.project_id = project_id
        self.location = location
        self.queue_name = queue_name
        self._client: Optional[tasks_v2.CloudTasksClient] = None
        self._queue_path: Optional[str] = None

    @property
    def client(self) -> tasks_v2.CloudTasksClient:
        """Lazy initialize Cloud Tasks client."""
        if self._client is None:
            self._client = tasks_v2.CloudTasksClient()
        return self._client

    @property
    def queue_path(self) -> str:
        """Lazy initialize queue path."""
        if self._queue_path is None:
            self._queue_path = self.client.queue_path(
                self.project_id, self.location, self.queue_name
            )
        return self._queue_path

    async def create_task(
        self,
        payload: Dict[str, Any],
        task_name: Optional[str] = None,
        delay_seconds: int = 0,
    ) -> str:
        """Create a task in the Cloud Tasks queue.

        Args:
            payload: JSON-serializable payload for the task
            task_name: Optional unique task name
            delay_seconds: Delay before task execution

        Returns:
            Task name/ID

        Raises:
            ValueError: If task creation fails
        """
        try:
            # Convert payload to JSON
            payload_json = json.dumps(payload).encode()

            # Create task
            task = tasks_v2.Task()
            task.http_request = tasks_v2.HttpRequest(
                http_method=tasks_v2.HttpMethod.POST,
                url=settings.worker_url,
                body=payload_json,
                headers={"Content-Type": "application/json"},
            )

            if task_name:
                task.name = self.client.task_path(
                    self.project_id, self.location, self.queue_name, task_name
                )

            if delay_seconds > 0:
                # Set schedule time
                import datetime

                schedule_time = datetime.datetime.utcnow() + datetime.timedelta(
                    seconds=delay_seconds
                )
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(schedule_time)
                task.schedule_time = timestamp

            # Create the task
            response = self.client.create_task(
                request={"parent": self.queue_path, "task": task}
            )

            task_id = str(response.name.split("/")[-1])
            logger.info(f"Task created successfully: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise ValueError(f"Task creation failed: {e}") from e

    async def delete_task(self, task_name: str) -> None:
        """Delete a task from the queue.

        Args:
            task_name: Full task name

        Raises:
            ValueError: If deletion fails
        """
        try:
            task_path = self.client.task_path(
                self.project_id, self.location, self.queue_name, task_name
            )
            self.client.delete_task(name=task_path)
            logger.info(f"Task deleted: {task_name}")
        except Exception as e:
            logger.error(f"Failed to delete task {task_name}: {e}")
            raise ValueError(f"Task deletion failed: {e}") from e

    async def get_task(self, task_name: str) -> Dict[str, Any]:
        """Get task details.

        Args:
            task_name: Task name

        Returns:
            Task details

        Raises:
            ValueError: If retrieval fails
        """
        try:
            task_path = self.client.task_path(
                self.project_id, self.location, self.queue_name, task_name
            )
            task = self.client.get_task(name=task_path)

            return {
                "name": task.name,
                "create_time": task.create_time,
                "schedule_time": task.schedule_time,
                "dispatch_count": task.dispatch_count,
                "response_count": task.response_count,
                "first_attempt": task.first_attempt,
                "last_attempt": task.last_attempt,
            }
        except Exception as e:
            logger.error(f"Failed to get task {task_name}: {e}")
            raise ValueError(f"Task retrieval failed: {e}") from e
