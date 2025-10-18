"""Supabase PostgreSQL Client"""
import os
import sys
import logging
from typing import Any, Optional, List, Dict
from datetime import datetime
from pathlib import Path

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)

# Load .env from project root if available
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://khkiebkjaqncqpjsknup.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

class SupabaseClient:
    def __init__(self):
        self._client: Optional[Any] = None

    @property
    def client(self) -> Optional[Any]:
        if not self._client and SUPABASE_AVAILABLE:
            try:
                self._client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                logger.info("✓ Supabase client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Supabase: {e}")
                self._client = None
        return self._client

    def is_connected(self) -> bool:
        return self._client is not None

    async def get_tasks(self, phase: Optional[str] = None, task_status: Optional[str] = None, priority: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            # Ensure client is initialized
            _ = self.client
            if not self.is_connected():
                logger.warning("Supabase not connected")
                return []
            query = self.client.table("video_tasks").select("*")
            if phase:
                query = query.eq("phase", phase)
            if task_status:
                query = query.eq("status", task_status)
            if priority:
                query = query.eq("priority", priority)
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        try:
            _ = self.client  # Ensure initialized
            if not self.is_connected():
                return None
            response = self.client.table("video_tasks").select("*").eq("id", task_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching task: {e}")
            return None

    async def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            _ = self.client  # Ensure initialized
            if not self.is_connected():
                return None
            task_data["created_at"] = datetime.utcnow().isoformat()
            task_data["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("video_tasks").insert(task_data).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            _ = self.client  # Ensure initialized
            if not self.is_connected():
                return None
            updates["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("video_tasks").update(updates).eq("id", task_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return None

    async def delete_task(self, task_id: str) -> bool:
        try:
            _ = self.client  # Ensure initialized
            if not self.is_connected():
                return False
            self.client.table("video_tasks").delete().eq("id", task_id).execute()
            logger.info(f"Task {task_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False

    async def get_task_stats(self) -> Dict[str, Any]:
        try:
            _ = self.client  # Ensure initialized
            if not self.is_connected():
                return {"error": "Not connected"}
            response = self.client.table("video_tasks").select("*").execute()
            tasks = response.data or []
            total = len(tasks)
            completed = sum(1 for t in tasks if t.get("status") == "completed")
            in_progress = sum(1 for t in tasks if t.get("status") == "in-progress")
            todo = sum(1 for t in tasks if t.get("status") == "todo")
            blocked = sum(1 for t in tasks if t.get("status") == "blocked")
            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "in_progress_tasks": in_progress,
                "todo_tasks": todo,
                "blocked_tasks": blocked,
                "completion_percentage": round((completed / total * 100) if total > 0 else 0, 1),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {"error": str(e)}

supabase = SupabaseClient()
