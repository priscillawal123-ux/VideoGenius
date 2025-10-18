"""
Task Management Routes for Dashboard Integration
Supabase real-time synchronized tasks
"""

from fastapi import APIRouter, HTTPException, status, Query
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

@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    phase: Optional[str] = Query(None, description="Filter by phase"),
    status: Optional[str] = Query(None, description="Filter by status"),
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
        
        logger.info(f"Fetching tasks - phase={phase}, status={status}")
        
        query = supabase.table("video_tasks").select("*")
        
        # Apply filters
        if phase:
            query = query.eq("phase", phase)
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
        if assignee:
            query = query.eq("assignee", assignee)
        
        response = query.order("created_at", desc=True).execute()
        
        logger.info(f"Retrieved {len(response.data)} tasks")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}"
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate) -> dict:
    """Create a new task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Creating task: {task_data.title}")
        
        task_dict = task_data.dict(exclude_unset=True)
        response = supabase.table("video_tasks").insert(task_dict).execute()
        
        if not response.data:
            raise ValueError("Failed to create task")
        
        logger.info(f"Task created: {response.data[0]['id']}")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> dict:
    """Get a specific task by ID"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Fetching task: {task_id}")
        
        response = supabase.table("video_tasks").select("*").eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate) -> dict:
    """Update a task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Updating task: {task_id}")
        
        # Only include fields that were provided
        update_dict = task_data.dict(exclude_unset=True)
        
        if not update_dict:
            raise ValueError("No fields to update")
        
        response = supabase.table("video_tasks").update(update_dict).eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        logger.info(f"Task updated: {task_id}")
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating task: {str(e)}"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str) -> None:
    """Delete a task"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info(f"Deleting task: {task_id}")
        
        response = supabase.table("video_tasks").delete().eq("id", task_id).execute()
        
        if not response.data:
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


@router.get("/stats/summary", response_model=dict)
async def get_task_stats() -> dict:
    """Get task statistics"""
    try:
        from backend.database.supabase_client import supabase
        
        logger.info("Fetching task statistics")
        
        response = supabase.table("video_tasks").select("*").execute()
        tasks = response.data
        
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == "completed")
        in_progress = sum(1 for t in tasks if t["status"] == "in-progress")
        blocked = sum(1 for t in tasks if t["status"] == "blocked")
        todo = sum(1 for t in tasks if t["status"] == "todo")
        
        progress = (completed / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "todo": todo,
            "progress_percentage": round(progress, 2),
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )
