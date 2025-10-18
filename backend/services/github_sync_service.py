"""GitHub Sync Service for Dashboard

Synchronizes GitHub Issues with Supabase dashboard tasks.
Bidirectional sync: GitHub Issues ↔ Supabase Tasks
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass

import httpx
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class GitHubIssueState(str, Enum):
    """GitHub issue states."""
    OPEN = "open"
    CLOSED = "closed"


class TaskStatus(str, Enum):
    """Task status mapping."""
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority mapping."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GitHubIssue:
    """GitHub issue representation."""
    id: int
    number: int
    title: str
    description: str
    state: str
    labels: List[str]
    assignee: Optional[str]
    milestone: Optional[str]
    created_at: str
    updated_at: str
    html_url: str


@dataclass
class DashboardTask:
    """Dashboard task representation."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    phase: str
    assignee: Optional[str]
    due_date: Optional[str]
    github_issue_id: Optional[int]
    github_issue_url: Optional[str]
    created_at: str
    updated_at: str


class GitHubSyncService:
    """Service for syncing GitHub Issues with Supabase dashboard tasks."""

    def __init__(
        self,
        github_token: str,
        github_owner: str,
        github_repo: str,
        supabase_url: str,
        supabase_key: str,
    ):
        """Initialize GitHub Sync Service.

        Args:
            github_token: GitHub API token
            github_owner: Repository owner
            github_repo: Repository name
            supabase_url: Supabase project URL
            supabase_key: Supabase API key

        Raises:
            ValueError: If required parameters are missing
        """
        if not all([github_token, github_owner, github_repo, supabase_url, supabase_key]):
            raise ValueError("Missing required parameters for GitHub sync service")

        self.github_token = github_token
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.github_base_url = "https://api.github.com"

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.http_client = httpx.AsyncClient(
            headers={"Authorization": f"token {github_token}"}
        )

        logger.info(
            f"GitHub Sync Service initialized for {github_owner}/{github_repo}"
        )

    async def sync_github_to_dashboard(self) -> Dict[str, Any]:
        """Sync GitHub issues to dashboard tasks.

        Returns:
            Sync result with counts (created, updated, deleted)

        Raises:
            httpx.HTTPError: If GitHub API call fails
            Exception: If Supabase sync fails
        """
        try:
            logger.info("Starting GitHub to Dashboard sync...")

            # Fetch GitHub issues
            issues = await self._fetch_github_issues()
            logger.info(f"Fetched {len(issues)} issues from GitHub")

            created_count = 0
            updated_count = 0

            for issue in issues:
                task = self._map_github_issue_to_task(issue)

                # Check if task already exists
                existing = await self._get_existing_task(issue.id)

                if existing:
                    # Update existing task
                    await self._update_task(existing["id"], task)
                    updated_count += 1
                    logger.debug(f"Updated task for issue #{issue.number}")
                else:
                    # Create new task
                    await self._create_task(task)
                    created_count += 1
                    logger.info(f"Created task for issue #{issue.number}")

            logger.info(
                f"Sync completed: {created_count} created, {updated_count} updated"
            )

            return {
                "status": "success",
                "created": created_count,
                "updated": updated_count,
                "total": len(issues),
            }

        except Exception as e:
            logger.error(f"GitHub to Dashboard sync failed: {e}")
            raise

    async def sync_dashboard_to_github(self, task_id: str) -> Dict[str, Any]:
        """Sync dashboard task update to GitHub issue.

        Args:
            task_id: Dashboard task ID

        Returns:
            Sync result with updated issue number

        Raises:
            ValueError: If task has no linked GitHub issue
            httpx.HTTPError: If GitHub API call fails
        """
        try:
            # Get task from dashboard
            task = await self._get_task_by_id(task_id)

            if not task or not task.get("github_issue_id"):
                raise ValueError(f"Task {task_id} has no linked GitHub issue")

            issue_number = task["github_issue_id"]

            # Update GitHub issue state based on task status
            new_state = self._map_task_status_to_github_state(task["status"])
            await self._update_github_issue_state(issue_number, new_state)

            # Update GitHub issue labels based on task priority
            labels = self._map_task_priority_to_labels(task["priority"])
            await self._update_github_issue_labels(issue_number, labels)

            logger.info(f"Synced task {task_id} to GitHub issue #{issue_number}")

            return {"status": "success", "issue_number": issue_number}

        except Exception as e:
            logger.error(f"Dashboard to GitHub sync failed: {e}")
            raise

    async def _fetch_github_issues(self) -> List[GitHubIssue]:
        """Fetch all GitHub issues.

        Returns:
            List of GitHub issues

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = (
            f"{self.github_base_url}/repos/{self.github_owner}/"
            f"{self.github_repo}/issues?state=all&per_page=100"
        )

        try:
            response = await self.http_client.get(url)
            response.raise_for_status()

            issues_data = response.json()
            issues = []

            for data in issues_data:
                if "pull_request" not in data:  # Skip PRs
                    issue = GitHubIssue(
                        id=data["id"],
                        number=data["number"],
                        title=data["title"],
                        description=data["body"] or "",
                        state=data["state"],
                        labels=[label["name"] for label in data.get("labels", [])],
                        assignee=data.get("assignee", {}).get("login"),
                        milestone=data.get("milestone", {}).get("title"),
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        html_url=data["html_url"],
                    )
                    issues.append(issue)

            return issues
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch GitHub issues: {e}")
            raise

    def _map_github_issue_to_task(self, issue: GitHubIssue) -> Dict[str, Any]:
        """Map GitHub issue to dashboard task.

        Args:
            issue: GitHub issue

        Returns:
            Task dictionary
        """
        # Determine priority from labels
        priority = self._extract_priority_from_labels(issue.labels)

        # Determine phase from milestone
        phase = self._extract_phase_from_milestone(issue.milestone)

        # Determine status from issue state
        status = (
            TaskStatus.COMPLETED.value
            if issue.state == GitHubIssueState.CLOSED.value
            else TaskStatus.TODO.value
        )

        return {
            "title": issue.title,
            "description": issue.description,
            "status": status,
            "priority": priority,
            "phase": phase,
            "assignee": issue.assignee,
            "due_date": None,  # GitHub doesn't have due dates in issues
            "github_issue_id": issue.id,
            "github_issue_url": issue.html_url,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
        }

    def _extract_priority_from_labels(self, labels: List[str]) -> str:
        """Extract priority from GitHub labels.

        Args:
            labels: GitHub issue labels

        Returns:
            Priority string
        """
        priority_map = {
            "priority:critical": TaskPriority.CRITICAL.value,
            "priority:high": TaskPriority.HIGH.value,
            "priority:medium": TaskPriority.MEDIUM.value,
            "priority:low": TaskPriority.LOW.value,
        }

        for label in labels:
            if label.lower() in priority_map:
                return priority_map[label.lower()]

        return TaskPriority.MEDIUM.value

    def _extract_phase_from_milestone(self, milestone: Optional[str]) -> str:
        """Extract phase from GitHub milestone.

        Args:
            milestone: GitHub milestone name

        Returns:
            Phase identifier
        """
        if not milestone:
            return "phase-1"

        phase_map = {
            "phase 1": "phase-1",
            "phase 2": "phase-2",
            "phase 3": "phase-3",
            "phase 4": "phase-4",
            "mvp": "phase-1",
            "ai integration": "phase-2",
            "production": "phase-3",
            "analytics": "phase-4",
        }

        normalized = milestone.lower()
        return phase_map.get(normalized, "phase-1")

    def _map_task_status_to_github_state(self, status: str) -> str:
        """Map task status to GitHub issue state.

        Args:
            status: Task status

        Returns:
            GitHub issue state (open/closed)
        """
        if status == TaskStatus.COMPLETED.value:
            return GitHubIssueState.CLOSED.value
        return GitHubIssueState.OPEN.value

    def _map_task_priority_to_labels(self, priority: str) -> List[str]:
        """Map task priority to GitHub labels.

        Args:
            priority: Task priority

        Returns:
            GitHub labels list
        """
        label_map = {
            TaskPriority.CRITICAL.value: "priority:critical",
            TaskPriority.HIGH.value: "priority:high",
            TaskPriority.MEDIUM.value: "priority:medium",
            TaskPriority.LOW.value: "priority:low",
        }

        return [label_map.get(priority, "priority:medium")]

    async def _get_existing_task(self, github_issue_id: int) -> Optional[Dict[str, Any]]:
        """Get existing task by GitHub issue ID.

        Args:
            github_issue_id: GitHub issue ID

        Returns:
            Task data or None if not found
        """
        try:
            response = (
                self.supabase.table("video_tasks")
                .select("*")
                .eq("github_issue_id", github_issue_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except Exception as e:
            logger.debug(f"Task not found for issue {github_issue_id}: {e}")
            return None

    async def _get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task data or None if not found
        """
        try:
            response = (
                self.supabase.table("video_tasks")
                .select("*")
                .eq("id", task_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except Exception as e:
            logger.debug(f"Task not found: {e}")
            return None

    async def _create_task(self, task_data: Dict[str, Any]) -> str:
        """Create new task in dashboard.

        Args:
            task_data: Task data

        Returns:
            Created task ID

        Raises:
            Exception: If creation fails
        """
        try:
            response = (
                self.supabase.table("video_tasks")
                .insert(task_data)
                .execute()
            )
            return response.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise

    async def _update_task(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> None:
        """Update task in dashboard.

        Args:
            task_id: Task ID
            task_data: Updated task data

        Raises:
            Exception: If update fails
        """
        try:
            self.supabase.table("video_tasks").update(task_data).eq(
                "id", task_id
            ).execute()
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise

    async def _update_github_issue_state(
        self, issue_number: int, state: str
    ) -> None:
        """Update GitHub issue state.

        Args:
            issue_number: Issue number
            state: New state (open/closed)

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = (
            f"{self.github_base_url}/repos/{self.github_owner}/"
            f"{self.github_repo}/issues/{issue_number}"
        )

        try:
            response = await self.http_client.patch(url, json={"state": state})
            response.raise_for_status()
            logger.debug(f"Updated issue #{issue_number} state to {state}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to update GitHub issue state: {e}")
            raise

    async def _update_github_issue_labels(
        self, issue_number: int, labels: List[str]
    ) -> None:
        """Update GitHub issue labels.

        Args:
            issue_number: Issue number
            labels: New labels

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = (
            f"{self.github_base_url}/repos/{self.github_owner}/"
            f"{self.github_repo}/issues/{issue_number}/labels"
        )

        try:
            response = await self.http_client.put(url, json=labels)
            response.raise_for_status()
            logger.debug(f"Updated issue #{issue_number} labels to {labels}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to update GitHub issue labels: {e}")
            raise

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.http_client.aclose()
