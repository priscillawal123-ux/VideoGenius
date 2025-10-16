"""
Checkpoint service for tracking video generation progress.
"""

import logging
from typing import Any, Dict

from google.cloud import bigquery

logger = logging.getLogger(__name__)


async def save_progress_checkpoint(
    job_id: str,
    db_client: Any,
    progress_percentage: int,
    checkpoint_data: Dict[str, Any],
) -> None:
    """Save a progress checkpoint for video generation.

    Args:
        job_id: The job ID
        db_client: Database client instance
        progress_percentage: Progress percentage (0-100)
        checkpoint_data: Checkpoint data to save

    Raises:
        ValueError: If checkpoint cannot be saved
    """
    try:
        checkpoint_record = {
            "job_id": job_id,
            "progress_percentage": progress_percentage,
            "checkpoint_data": checkpoint_data,
            "timestamp": "AUTO",  # BigQuery will handle timestamp
        }

        # Save to checkpoints table
        await db_client.insert_row("checkpoints", checkpoint_record)

        logger.info(f"Checkpoint saved for job {job_id}: {progress_percentage}%")

    except Exception as e:
        logger.error(f"Failed to save checkpoint for job {job_id}: {e}")
        raise ValueError(f"Failed to save checkpoint: {e}") from e


async def get_latest_checkpoint(job_id: str, db_client: Any) -> Dict[str, Any]:
    """Get the latest checkpoint for a job.

    Args:
        job_id: The job ID

    Returns:
        Latest checkpoint data or empty dict if none found
    """
    try:
        query = f"""
        SELECT * FROM `{db_client.project_id}.{db_client.dataset_id}.checkpoints`
        WHERE job_id = @job_id
        ORDER BY timestamp DESC
        LIMIT 1
        """

        parameters = [bigquery.ScalarQueryParameter("job_id", "STRING", job_id)]

        results = await db_client.query_data(query, parameters)
        return results[0] if results else {}

    except Exception as e:
        logger.error(f"Failed to get checkpoint for job {job_id}: {e}")
        return {}


async def resume_from_checkpoint(job_id: str, db_client: Any) -> Dict[str, Any]:
    """Resume video generation from the latest checkpoint.

    Args:
        job_id: The job ID

    Returns:
        Checkpoint data for resuming, or empty dict if no checkpoint
    """
    checkpoint = await get_latest_checkpoint(job_id, db_client)

    if checkpoint:
        progress = checkpoint.get("progress_percentage", 0)
        logger.info(f"Resuming job {job_id} from {progress}%")
        return checkpoint

    logger.info(f"No checkpoint found for job {job_id}, starting fresh")
    return {}
