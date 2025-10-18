"""
GitHub Integration Service for Video Genius

Bi-directional sync between Supabase video_tasks and GitHub Issues.
This service handles:
- Syncing GitHub issues to database tasks
- Syncing database tasks to GitHub issues
- Maintaining sync state and history
- Webhook handling for real-time updates

Usage:
    from backend.services.github_sync import GitHubSyncService
    service = GitHubSyncService(github_token, supabase_client)
    
    # Sync all issues to tasks
    await service.sync_issues_to_tasks()
    
    # Create GitHub issue from task
    await service.create_issue_from_task(task_id)
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ============================================================================
# Models
# ============================================================================


@dataclass
class GitHubIssue:
    """GitHub issue data model."""
    
    id: int
    number: int
    title: str
    body: str
    state: str  # 'open', 'closed'
    assignee: Optional[str] = None
    labels: List[str] = None
    created_at: str = None
    updated_at: str = None
    url: str = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class TaskCreateFromIssueModel(BaseModel):
    """Pydantic model for creating task from GitHub issue."""
    
    title: str
    description: str
    github_issue_id: int
    github_issue_url: str
    github_issue_number: int
    status: str = "todo"
    priority: str = "medium"
    phase: str = "phase-1"
    assignee: Optional[str] = None


class GitHubSyncService:
    """Service for syncing between GitHub Issues and Video Genius tasks."""
    
    # GitHub API constants
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_MEDIA_TYPE = "application/vnd.github+json"
    
    # Label mappings
    PRIORITY_LABELS = {
        "priority: low": "low",
        "priority: medium": "medium",
        "priority: high": "high",
        "priority: critical": "critical",
    }
    
    PHASE_LABELS = {
        "phase: 1": "phase-1",
        "phase: 2": "phase-2",
        "phase: 3": "phase-3",
        "phase: 4": "phase-4",
    }
    
    STATUS_LABELS = {
        "status: todo": "todo",
        "status: in-progress": "in-progress",
        "status: blocked": "blocked",
        "status: completed": "completed",
    }
    
    def __init__(self, github_token: str, supabase_client):
        """Initialize GitHub sync service.
        
        Args:
            github_token: GitHub personal access token
            supabase_client: Supabase client instance
        """
        self.github_token = github_token
        self.supabase = supabase_client
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "priscillawal123-ux")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "VideoGenius")
        self.repo_full_name = f"{self.repo_owner}/{self.repo_name}"
        
        logger.info(f"GitHubSyncService initialized for {self.repo_full_name}")
    
    async def sync_issues_to_tasks(self) -> Dict[str, Any]:
        """Sync all GitHub issues to database tasks.
        
        This method:
        1. Fetches all issues from the repository
        2. Maps GitHub labels to task properties (priority, phase, status)
        3. Creates/updates tasks in the database
        4. Maintains sync history
        
        Returns:
            Summary of sync operation with counts
            
        Raises:
            httpx.HTTPError: If GitHub API call fails
            Exception: If database operation fails
        """
        logger.info(f"Starting GitHub issues sync from {self.repo_full_name}")
        
        try:
            # Fetch all issues from GitHub
            issues = await self._fetch_all_issues()
            logger.info(f"Fetched {len(issues)} issues from GitHub")
            
            sync_results = {
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0,
            }
            
            # Process each issue
            for issue in issues:
                try:
                    result = await self._sync_issue_to_task(issue)
                    
                    if result == "created":
                        sync_results["created"] += 1
                    elif result == "updated":
                        sync_results["updated"] += 1
                    elif result == "skipped":
                        sync_results["skipped"] += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing issue #{issue.number}: {e}")
                    sync_results["errors"] += 1
            
            logger.info(
                f"Sync completed: "
                f"{sync_results['created']} created, "
                f"{sync_results['updated']} updated, "
                f"{sync_results['skipped']} skipped, "
                f"{sync_results['errors']} errors"
            )
            
            return sync_results
            
        except Exception as e:
            logger.error(f"GitHub sync failed: {e}")
            raise
    
    async def create_issue_from_task(
        self,
        task_id: str,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a GitHub issue from a video task.
        
        This method:
        1. Takes task data and creates a GitHub issue
        2. Maps task properties to GitHub labels
        3. Updates task with GitHub issue ID
        4. Records sync in database
        
        Args:
            task_id: ID of task in database
            task_data: Task data containing title, description, etc.
            
        Returns:
            Created GitHub issue data
            
        Raises:
            httpx.HTTPError: If GitHub API call fails
            ValueError: If task data is invalid
        """
        logger.info(f"Creating GitHub issue for task {task_id}")
        
        # Validate task data
        if not task_data.get("title"):
            raise ValueError("Task must have a title")
        
        # Build issue body with task metadata
        body = self._build_issue_body(task_data)
        
        # Build labels from task properties
        labels = self._build_issue_labels(task_data)
        
        # Create payload
        payload = {
            "title": task_data["title"],
            "body": body,
            "labels": labels,
        }
        
        if task_data.get("assignee"):
            payload["assignee"] = task_data["assignee"]
        
        try:
            # Create GitHub issue
            issue_url = f"{self.GITHUB_API_BASE}/repos/{self.repo_full_name}/issues"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    issue_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
            
            issue_data = response.json()
            logger.info(f"Created GitHub issue #{issue_data['number']}")
            
            # Update task with GitHub issue info
            await self._update_task_with_issue(task_id, issue_data)
            
            return issue_data
            
        except httpx.HTTPError as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    async def update_issue_from_task(
        self,
        github_issue_number: int,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update GitHub issue from task changes.
        
        When a task is updated, push changes to the corresponding GitHub issue.
        
        Args:
            github_issue_number: GitHub issue number
            task_data: Updated task data
            
        Returns:
            Updated GitHub issue data
            
        Raises:
            httpx.HTTPError: If GitHub API call fails
        """
        logger.info(f"Updating GitHub issue #{github_issue_number}")
        
        try:
            # Build issue body and labels
            body = self._build_issue_body(task_data)
            labels = self._build_issue_labels(task_data)
            
            # Build payload
            payload = {
                "title": task_data.get("title"),
                "body": body,
                "labels": labels,
                "state": "open" if task_data.get("status") != "completed" else "closed",
            }
            
            # Update GitHub issue
            issue_url = (
                f"{self.GITHUB_API_BASE}/repos/{self.repo_full_name}/"
                f"issues/{github_issue_number}"
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    issue_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
            
            logger.info(f"Updated GitHub issue #{github_issue_number}")
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    async def _fetch_all_issues(self) -> List[GitHubIssue]:
        """Fetch all issues from GitHub repository.
        
        Returns:
            List of GitHubIssue objects
        """
        issues = []
        page = 1
        
        try:
            async with httpx.AsyncClient() as client:
                while True:
                    # Fetch page of issues
                    url = (
                        f"{self.GITHUB_API_BASE}/repos/{self.repo_full_name}/"
                        f"issues?state=all&per_page=100&page={page}"
                    )
                    
                    response = await client.get(
                        url,
                        headers=self._get_headers(),
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    
                    page_data = response.json()
                    
                    if not page_data:
                        break
                    
                    # Convert to GitHubIssue objects
                    for issue_data in page_data:
                        issue = GitHubIssue(
                            id=issue_data["id"],
                            number=issue_data["number"],
                            title=issue_data["title"],
                            body=issue_data["body"] or "",
                            state=issue_data["state"],
                            assignee=issue_data.get("assignee", {}).get("login"),
                            labels=[label["name"] for label in issue_data["labels"]],
                            created_at=issue_data["created_at"],
                            updated_at=issue_data["updated_at"],
                            url=issue_data["html_url"],
                        )
                        issues.append(issue)
                    
                    page += 1
            
            return issues
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch GitHub issues: {e}")
            raise
    
    async def _sync_issue_to_task(self, issue: GitHubIssue) -> str:
        """Sync a single GitHub issue to a task.
        
        Returns:
            "created", "updated", or "skipped"
        """
        # Check if task already exists
        existing_task = await self._find_task_by_issue(issue.id)
        
        if existing_task:
            # Update existing task
            await self._update_existing_task(existing_task["id"], issue)
            return "updated"
        else:
            # Create new task
            await self._create_task_from_issue(issue)
            return "created"
    
    async def _find_task_by_issue(
        self,
        github_issue_id: int
    ) -> Optional[Dict[str, Any]]:
        """Find task in database by GitHub issue ID.
        
        Returns:
            Task data or None if not found
        """
        try:
            response = self.supabase.table("video_tasks").select(
                "*"
            ).eq("github_issue_id", github_issue_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error finding task by issue: {e}")
            return None
    
    async def _create_task_from_issue(self, issue: GitHubIssue) -> None:
        """Create a new task from GitHub issue."""
        try:
            # Extract task properties from labels
            priority = self._extract_priority_from_labels(issue.labels)
            phase = self._extract_phase_from_labels(issue.labels)
            status = self._extract_status_from_labels(issue.labels)
            
            # Create task object
            task = {
                "title": issue.title,
                "description": issue.body,
                "github_issue_id": issue.id,
                "github_issue_url": issue.url,
                "status": status,
                "priority": priority,
                "phase": phase,
                "assignee": issue.assignee,
                "github_issue_synced_at": datetime.utcnow().isoformat(),
            }
            
            # Insert into database
            response = self.supabase.table("video_tasks").insert(task).execute()
            logger.info(f"Created task from GitHub issue #{issue.number}")
            
        except Exception as e:
            logger.error(f"Error creating task from issue: {e}")
            raise
    
    async def _update_existing_task(
        self,
        task_id: str,
        issue: GitHubIssue
    ) -> None:
        """Update existing task with GitHub issue data."""
        try:
            # Extract task properties from labels
            priority = self._extract_priority_from_labels(issue.labels)
            phase = self._extract_phase_from_labels(issue.labels)
            status = self._extract_status_from_labels(issue.labels)
            
            # Build update object
            update_data = {
                "title": issue.title,
                "description": issue.body,
                "status": status,
                "priority": priority,
                "phase": phase,
                "assignee": issue.assignee,
                "github_issue_synced_at": datetime.utcnow().isoformat(),
            }
            
            # Update in database
            self.supabase.table("video_tasks").update(
                update_data
            ).eq("id", task_id).execute()
            
            logger.info(f"Updated task {task_id} from GitHub issue")
            
        except Exception as e:
            logger.error(f"Error updating task from issue: {e}")
            raise
    
    async def _update_task_with_issue(
        self,
        task_id: str,
        issue_data: Dict[str, Any]
    ) -> None:
        """Update task with GitHub issue information."""
        try:
            update_data = {
                "github_issue_id": issue_data["id"],
                "github_issue_url": issue_data["html_url"],
                "github_issue_synced_at": datetime.utcnow().isoformat(),
            }
            
            self.supabase.table("video_tasks").update(
                update_data
            ).eq("id", task_id).execute()
            
            logger.info(f"Updated task {task_id} with GitHub issue info")
            
        except Exception as e:
            logger.error(f"Error updating task with issue: {e}")
            raise
    
    def _build_issue_body(self, task_data: Dict[str, Any]) -> str:
        """Build GitHub issue body from task data."""
        body_parts = []
        
        if task_data.get("description"):
            body_parts.append(task_data["description"])
        
        # Add metadata section
        body_parts.append("\n---\n")
        body_parts.append("### Metadata\n")
        
        if task_data.get("priority"):
            body_parts.append(f"- **Priority**: {task_data['priority']}\n")
        
        if task_data.get("phase"):
            body_parts.append(f"- **Phase**: {task_data['phase']}\n")
        
        if task_data.get("due_date"):
            body_parts.append(f"- **Due Date**: {task_data['due_date']}\n")
        
        if task_data.get("assignee"):
            body_parts.append(f"- **Assignee**: {task_data['assignee']}\n")
        
        body_parts.append(
            "\n*This issue is synced with Video Genius Dashboard*\n"
        )
        
        return "".join(body_parts)
    
    def _build_issue_labels(self, task_data: Dict[str, Any]) -> List[str]:
        """Build GitHub labels from task data."""
        labels = []
        
        # Add priority label
        if task_data.get("priority"):
            labels.append(f"priority: {task_data['priority']}")
        
        # Add phase label
        if task_data.get("phase"):
            phase = task_data["phase"].replace("phase-", "")
            labels.append(f"phase: {phase}")
        
        # Add status label
        if task_data.get("status"):
            labels.append(f"status: {task_data['status']}")
        
        # Add type label
        labels.append("type: task")
        
        return labels
    
    def _extract_priority_from_labels(self, labels: List[str]) -> str:
        """Extract priority from GitHub labels."""
        for label in labels:
            if label in self.PRIORITY_LABELS:
                return self.PRIORITY_LABELS[label]
        return "medium"
    
    def _extract_phase_from_labels(self, labels: List[str]) -> str:
        """Extract phase from GitHub labels."""
        for label in labels:
            if label in self.PHASE_LABELS:
                return self.PHASE_LABELS[label]
        return "phase-1"
    
    def _extract_status_from_labels(self, labels: List[str]) -> str:
        """Extract status from GitHub labels."""
        for label in labels:
            if label in self.STATUS_LABELS:
                return self.STATUS_LABELS[label]
        return "todo"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get GitHub API headers."""
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": self.GITHUB_MEDIA_TYPE,
            "X-GitHub-Api-Version": "2022-11-28",
        }
