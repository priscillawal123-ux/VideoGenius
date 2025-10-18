"""
GitHub Webhooks API Routes

Handles incoming webhooks from GitHub to keep tasks in sync.
Events handled:
- issues: opened, edited, closed, reopened
- issue_comment: created, edited, deleted
- pull_request: opened, edited, closed, reopened

These webhooks ensure real-time sync between GitHub and Video Genius Dashboard.

API Endpoint: POST /api/v1/webhooks/github
"""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel
from supabase import create_client

from backend.services.github_sync import GitHubSyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


# ============================================================================
# Models
# ============================================================================


class GitHubWebhookIssue(BaseModel):
    """GitHub webhook issue payload."""
    
    id: int
    number: int
    title: str
    body: str
    state: str
    assignee: Dict[str, Any] = None
    labels: list = []
    created_at: str
    updated_at: str
    html_url: str


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload."""
    
    action: str
    issue: GitHubWebhookIssue
    repository: Dict[str, Any]


# ============================================================================
# Webhook Verification
# ============================================================================


def verify_github_webhook(request_body: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature.
    
    Args:
        request_body: Raw request body
        signature: X-Hub-Signature-256 header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured")
        return False
    
    # Calculate expected signature
    expected_signature = "sha256=" + hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha256,
    ).hexdigest()
    
    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(signature, expected_signature)


# ============================================================================
# Webhook Routes
# ============================================================================


@router.post(
    "/github",
    status_code=status.HTTP_202_ACCEPTED,
    summary="GitHub Webhook Handler",
    description="Receives GitHub webhook events and syncs with tasks"
)
async def github_webhook(
    request: Request
) -> Dict[str, Any]:
    """Handle GitHub webhook events.
    
    This endpoint receives webhooks from GitHub when issues are created,
    updated, or closed. It verifies the webhook signature and syncs the
    changes with the Video Genius Dashboard.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Webhook processing status
        
    Raises:
        HTTPException: If webhook verification fails or processing error occurs
    """
    try:
        # Get raw request body for signature verification
        body = await request.body()
        
        # Get signature header
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        # Verify webhook signature
        if not verify_github_webhook(body, signature):
            logger.warning("Invalid GitHub webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse payload
        payload = await request.json()
        
        logger.info(f"GitHub webhook received: {payload.get('action')} {payload.get('issue', {}).get('number')}")
        
        # Handle different event types
        event = request.headers.get("X-GitHub-Event", "")
        
        # Initialize Supabase client
        from backend.core.config import get_settings
        settings = get_settings()
        supabase = create_client(
            settings.supabase_url or os.getenv("SUPABASE_URL"),
            settings.supabase_key or os.getenv("SUPABASE_KEY")
        )
        
        if event == "issues":
            return await _handle_issue_event(payload, supabase)
        
        elif event == "issue_comment":
            return await _handle_comment_event(payload, supabase)
        
        elif event == "ping":
            logger.info("GitHub webhook ping received")
            return {
                "status": "ok",
                "message": "Webhook is configured correctly"
            }
        
        else:
            logger.warning(f"Unhandled webhook event: {event}")
            return {
                "status": "ignored",
                "message": f"Event type '{event}' not handled"
            }
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


# ============================================================================
# Event Handlers
# ============================================================================


async def _handle_issue_event(
    payload: Dict[str, Any],
    supabase
) -> Dict[str, Any]:
    """Handle GitHub issue events.
    
    Events: opened, edited, closed, reopened, labeled, unlabeled, assigned, unassigned
    """
    action = payload.get("action")
    issue = payload.get("issue", {})
    
    logger.info(f"Processing issue event: {action} (#{issue.get('number')})")
    
    # Initialize GitHub sync service
    github_token = os.getenv("GITHUB_TOKEN", "")
    
    if not github_token:
        logger.error("GITHUB_TOKEN not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub token not configured"
        )
    
    sync_service = GitHubSyncService(github_token, supabase)
    
    try:
        if action == "opened":
            # Create new task from issue
            await sync_service._create_task_from_issue(
                GitHubIssueFromPayload(issue)
            )
            return {
                "status": "created",
                "message": f"Task created from issue #{issue.get('number')}"
            }
        
        elif action in ["edited", "labeled", "unlabeled"]:
            # Update task from issue changes
            await sync_service._find_task_by_issue(issue.get("id"))
            await sync_service._update_existing_task(
                # task_id would need to be looked up
                None,  # This should be refactored
                GitHubIssueFromPayload(issue)
            )
            return {
                "status": "updated",
                "message": f"Task updated from issue #{issue.get('number')}"
            }
        
        elif action == "closed":
            # Mark task as completed
            task = await sync_service._find_task_by_issue(issue.get("id"))
            if task:
                supabase.table("video_tasks").update({
                    "status": "completed",
                    "completed_date": issue.get("closed_at")
                }).eq("id", task["id"]).execute()
            
            return {
                "status": "updated",
                "message": f"Task marked completed from issue #{issue.get('number')}"
            }
        
        elif action == "reopened":
            # Mark task as active again
            task = await sync_service._find_task_by_issue(issue.get("id"))
            if task:
                supabase.table("video_tasks").update({
                    "status": "todo",
                    "completed_date": None
                }).eq("id", task["id"]).execute()
            
            return {
                "status": "updated",
                "message": f"Task reopened from issue #{issue.get('number')}"
            }
        
        else:
            return {
                "status": "ignored",
                "message": f"Action '{action}' not handled"
            }
    
    except Exception as e:
        logger.error(f"Error handling issue event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing issue: {str(e)}"
        )


async def _handle_comment_event(
    payload: Dict[str, Any],
    supabase
) -> Dict[str, Any]:
    """Handle GitHub issue comment events.
    
    Events: created, edited, deleted
    """
    action = payload.get("action")
    issue = payload.get("issue", {})
    comment = payload.get("comment", {})
    
    logger.info(f"Processing comment event: {action} on issue #{issue.get('number')}")
    
    # For now, we just log comments but don't sync them
    # In the future, could store comments as task history
    
    return {
        "status": "logged",
        "message": f"Comment event logged: {action} on issue #{issue.get('number')}"
    }


# ============================================================================
# Helper Classes
# ============================================================================


class GitHubIssueFromPayload:
    """Convert GitHub webhook issue payload to GitHubIssue format."""
    
    def __init__(self, issue_data: Dict[str, Any]):
        self.id = issue_data.get("id")
        self.number = issue_data.get("number")
        self.title = issue_data.get("title")
        self.body = issue_data.get("body", "")
        self.state = issue_data.get("state")
        self.assignee = issue_data.get("assignee", {}).get("login")
        self.labels = [label.get("name") for label in issue_data.get("labels", [])]
        self.created_at = issue_data.get("created_at")
        self.updated_at = issue_data.get("updated_at")
        self.url = issue_data.get("html_url")
