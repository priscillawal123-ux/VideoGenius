"""
Task Management Routes for Dashboard Integration
Supabase real-time synchronized tasks
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# MODELS
# ============================================================================

class TaskCreate(BaseModel):
    """Model for creating a new task"""
    title: str
    phase: str
    status: str = "todo"
    priority: str = "medium"
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Model for updating a task"""
    title: Optional[str] = None
    phase: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    description: Optional[str] = None


class TaskResponse(BaseModel):
    """Model for task response"""
    id: str
    title: str
    phase: str
    status: str
    priority: str
    assignee: Optional[str]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("")
async def get_tasks(
    phase: Optional[str] = Query(None, description="Filter by phase"),
    task_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
) -> List[dict]:
    """
    Get all tasks with optional filters
    
    - **phase**: Filter by phase (phase-1, phase-2, etc)
    - **status**: Filter by status (todo, in-progress, completed, blocked)
    - **priority**: Filter by priority (low, medium, high, critical)
    - **assignee**: Filter by assignee name
    """
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Fetching tasks - phase={phase}, status={task_status}")
        
        # Use SupabaseClient methods (async)
        tasks = await supabase.get_tasks(phase=phase, task_status=task_status, priority=priority)
        
        logger.info(f"Retrieved {len(tasks) if tasks else 0} tasks")
        return tasks or []
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}"
        )


@router.post("")
async def create_task(task_data: TaskCreate) -> dict:
    """Create a new task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Creating task: {task_data.title}")
        
        task_dict = task_data.dict(exclude_unset=True)
        result = await supabase.create_task(task_dict)
        
        if not result:
            raise ValueError("Failed to create task")
        
        logger.info(f"Task created: {result['id']}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/stats/summary")
async def get_task_stats() -> dict:
    """Get task statistics"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info("Fetching task statistics")
        
        stats = await supabase.get_task_stats()
        
        if "error" in stats:
            raise Exception(stats.get("error"))
        
        return {
            "total": stats.get("total_tasks", 0),
            "completed": stats.get("completed_tasks", 0),
            "in_progress": stats.get("in_progress_tasks", 0),
            "blocked": stats.get("blocked_tasks", 0),
            "todo": stats.get("todo_tasks", 0),
            "progress_percentage": stats.get("completion_percentage", 0),
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )


@router.get("/{task_id}")
async def get_task(task_id: str) -> dict:
    """Get a specific task by ID"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Fetching task: {task_id}")
        
        result = await supabase.get_task(task_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task: {str(e)}"
        )


@router.put("/{task_id}")
async def update_task(task_id: str, task_data: TaskUpdate) -> dict:
    """Update a task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Updating task: {task_id}")
        
        # Only include fields that were provided
        update_dict = task_data.dict(exclude_unset=True)
        
        if not update_dict:
            raise ValueError("No fields to update")
        
        result = await supabase.update_task(task_id, update_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        logger.info(f"Task updated: {task_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating task: {str(e)}"
        )


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> None:
    """Delete a task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Deleting task: {task_id}")
        
        success = await supabase.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        logger.info(f"Task deleted: {task_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting task: {str(e)}"
        )


@router.get("/stats/summary")
async def get_task_stats() -> dict:
    """Get task statistics"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info("Fetching task statistics")
        
        stats = await supabase.get_task_stats()
        
        if "error" in stats:
            raise Exception(stats.get("error"))
        
        return {
            "total": stats.get("total_tasks", 0),
            "completed": stats.get("completed_tasks", 0),
            "in_progress": stats.get("in_progress_tasks", 0),
            "blocked": stats.get("blocked_tasks", 0),
            "todo": stats.get("todo_tasks", 0),
            "progress_percentage": stats.get("completion_percentage", 0),
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )
