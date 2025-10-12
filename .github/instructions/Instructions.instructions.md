---
applyTo: '**'
---
# GitHub Copilot Instructions - Video Genius Project

## 🎯 PRIMARY OBJECTIVE
You are an expert code generator for the Video Genius project. Your PRIMARY FOCUS is generating precise, production-ready code and GitHub CLI commands. Always prioritize code generation over explanations unless explicitly asked.

---

## 📋 PROJECT CONTEXT

### Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await patterns)
- **Cloud**: Google Cloud Platform (Vertex AI, BigQuery, Cloud Run, Cloud Storage)
- **Containerization**: Docker (multi-stage builds)
- **Version Control**: Git + GitHub CLI (gh)
- **Testing**: Pytest with coverage
- **Linting**: Ruff + MyPy + Black

### Project Structure
```
video-genius/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── services/         # Business logic (Vertex AI, video processing)
│   ├── models/           # Pydantic models
│   ├── database/         # BigQuery client & queries
│   └── storage/          # Cloud Storage operations
├── tests/                # Test suite
├── scripts/              # Automation scripts
└── .github/              # GitHub workflows & configs
```

---

## 🔧 GITHUB CLI (gh) - COMPLETE COMMAND REFERENCE

### Authentication & Configuration
```bash
# Authentication
gh auth login                           # Interactive login
gh auth logout                          # Logout
gh auth refresh -s <scopes>            # Refresh with additional scopes (e.g., copilot, workflow)
gh auth status                          # Check authentication status
gh auth token                           # Get auth token

# Configuration
gh config set editor <editor>           # Set default editor (vim, code, nano)
gh config set git_protocol <protocol>   # Set protocol (https, ssh)
gh config get <key>                     # Get config value
gh config list                          # List all configurations
```

### Repository Operations
```bash
# Repository Management
gh repo create <name> --public|--private    # Create new repository
gh repo clone <repo>                        # Clone repository
gh repo fork <repo>                         # Fork repository
gh repo view [repo]                         # View repository details
gh repo delete <repo> --yes                 # Delete repository
gh repo sync                                # Sync fork with upstream
gh repo set-default                         # Set default repo for commands

# Repository Settings
gh repo edit --description "desc"           # Update description
gh repo edit --homepage "url"               # Set homepage
gh repo edit --visibility <public|private>  # Change visibility
gh repo archive                             # Archive repository
gh repo unarchive                           # Unarchive repository
```

### Issues Management
```bash
# Creating & Viewing
gh issue create --title "title" --body "body"     # Create issue
gh issue create --title "title" --web             # Create in browser
gh issue list --state <open|closed|all>           # List issues
gh issue list --assignee @me                      # My assigned issues
gh issue list --label "bug,priority"              # Filter by labels
gh issue view <number>                            # View issue details
gh issue view <number> --web                      # Open in browser

# Managing Issues
gh issue edit <number> --add-label "label"        # Add label
gh issue edit <number> --remove-label "label"     # Remove label
gh issue edit <number> --add-assignee @user       # Assign user
gh issue edit <number> --add-project "project"    # Add to project
gh issue close <number>                           # Close issue
gh issue reopen <number>                          # Reopen issue
gh issue pin <number>                             # Pin issue
gh issue unpin <number>                           # Unpin issue
gh issue delete <number>                          # Delete issue

# Commenting
gh issue comment <number> --body "comment"        # Add comment
gh issue comment <number> --edit                  # Edit last comment

# Development
gh issue develop <number> --checkout              # Create branch from issue
gh issue develop <number> --base main             # Specify base branch
```

### Pull Requests
```bash
# Creating PRs
gh pr create --title "title" --body "body"        # Create PR
gh pr create --fill                               # Auto-fill from commits
gh pr create --draft                              # Create draft PR
gh pr create --web                                # Create in browser
gh pr create --base <branch> --head <branch>      # Specify branches

# Listing & Viewing
gh pr list --state <open|closed|merged|all>       # List PRs
gh pr list --author @me                           # My PRs
gh pr list --assignee @me                         # Assigned to me
gh pr list --label "bug"                          # Filter by label
gh pr view <number>                               # View PR details
gh pr view <number> --web                         # Open in browser
gh pr diff <number>                               # View diff
gh pr status                                      # Status of relevant PRs

# Managing PRs
gh pr checkout <number>                           # Checkout PR branch
gh pr edit <number> --add-label "label"           # Add label
gh pr edit <number> --add-reviewer @user          # Add reviewer
gh pr edit <number> --milestone "milestone"       # Set milestone
gh pr ready <number>                              # Mark draft as ready
gh pr close <number>                              # Close PR
gh pr reopen <number>                             # Reopen PR

# Reviews
gh pr review <number> --approve                   # Approve PR
gh pr review <number> --request-changes           # Request changes
gh pr review <number> --comment --body "text"     # Comment review
gh pr comment <number> --body "comment"           # Add comment

# Merging
gh pr merge <number> --merge                      # Merge commit
gh pr merge <number> --squash                     # Squash merge
gh pr merge <number> --rebase                     # Rebase merge
gh pr merge <number> --auto                       # Auto-merge when ready
gh pr merge <number> --delete-branch              # Delete branch after merge

# Checks & CI
gh pr checks <number>                             # View CI status
gh pr checks <number> --watch                     # Watch CI in real-time
```

### Workflows & Actions
```bash
# Workflows
gh workflow list                                  # List workflows
gh workflow view <workflow>                       # View workflow details
gh workflow run <workflow>                        # Trigger workflow
gh workflow run <workflow> --ref <branch>         # Run on specific branch
gh workflow enable <workflow>                     # Enable workflow
gh workflow disable <workflow>                    # Disable workflow

# Runs
gh run list                                       # List workflow runs
gh run list --workflow <workflow>                 # Filter by workflow
gh run view <run-id>                              # View run details
gh run watch <run-id>                             # Watch run in real-time
gh run download <run-id>                          # Download artifacts
gh run rerun <run-id>                             # Rerun workflow
gh run rerun <run-id> --failed                    # Rerun only failed jobs
gh run cancel <run-id>                            # Cancel run
gh run delete <run-id>                            # Delete run
```

### Secrets & Variables
```bash
# Repository Secrets
gh secret list                                    # List secrets
gh secret set <name> < secret.txt                 # Set from file
gh secret set <name> --body "value"               # Set directly
gh secret delete <name>                           # Delete secret

# Repository Variables
gh variable list                                  # List variables
gh variable set <name> --body "value"             # Set variable
gh variable delete <name>                         # Delete variable

# Organization & Environment
gh secret set <name> --org <org>                  # Org-level secret
gh secret set <name> --env <environment>          # Environment secret
gh variable set <name> --env <environment>        # Environment variable
```

### Releases
```bash
# Creating Releases
gh release create <tag> --title "title"           # Create release
gh release create <tag> --notes "notes"           # With release notes
gh release create <tag> --generate-notes          # Auto-generate notes
gh release create <tag> <files>                   # With assets
gh release create <tag> --draft                   # Create draft
gh release create <tag> --prerelease              # Mark as prerelease

# Managing Releases
gh release list                                   # List releases
gh release view <tag>                             # View release
gh release edit <tag> --notes "new notes"         # Edit release
gh release delete <tag> --yes                     # Delete release
gh release download <tag>                         # Download assets
gh release upload <tag> <files>                   # Upload assets
```

### Search
```bash
# Search Repositories
gh search repos <query>                           # Search repos
gh search repos <query> --language python         # Filter by language
gh search repos <query> --stars ">1000"          # Filter by stars
gh search repos <query> --topic "machine-learning" # By topic

# Search Issues & PRs
gh search issues <query>                          # Search issues
gh search issues <query> --state open             # Open issues only
gh search issues <query> --label bug              # By label
gh search prs <query>                             # Search PRs
gh search prs <query> --review-requested @me      # PRs needing review

# Search Code
gh search code <query>                            # Search code
gh search code <query> --language python          # In Python files
gh search code <query> --repo owner/repo          # In specific repo
```

### Labels & Projects
```bash
# Labels
gh label list                                     # List labels
gh label create <name> --color <hex>              # Create label
gh label create <name> --description "desc"       # With description
gh label edit <name> --color <hex>                # Edit label
gh label delete <name>                            # Delete label
gh label clone <source-repo>                      # Clone from repo

# Projects
gh project list --owner <owner>                   # List projects
gh project view <number>                          # View project
gh project create --title "title"                 # Create project
gh project close <number>                         # Close project
gh project field-list <number>                    # List fields
```

### Aliases
```bash
# Manage Aliases
gh alias list                                     # List aliases
gh alias set <alias> <expansion>                  # Create alias
gh alias set prc 'pr create --fill'              # Example alias
gh alias delete <alias>                           # Delete alias

# Useful Alias Examples
gh alias set co 'pr checkout'                     # Checkout PR
gh alias set bugs 'issue list --label bug'        # List bugs
gh alias set work 'issue list --assignee @me'     # My work
gh alias set ci 'pr checks'                       # Check CI
```

### Extensions
```bash
# Extension Management
gh extension list                                 # List installed
gh extension install <repo>                       # Install extension
gh extension upgrade <extension>                  # Upgrade extension
gh extension upgrade --all                        # Upgrade all
gh extension remove <extension>                   # Remove extension

# Essential Extensions
gh extension install github/gh-copilot            # Copilot CLI
gh extension install dlvhdr/gh-dash               # Dashboard
gh extension install seachicken/gh-poi            # Clean branches
gh extension install mislav/gh-branch             # Branch utils
```

### Copilot CLI (Extension)
```bash
# Command Suggestions
gh copilot suggest                                # Interactive suggest
gh copilot suggest -t shell "description"         # Shell command
gh copilot suggest -t git "description"           # Git command
gh copilot suggest -t gh "description"            # GH CLI command

# Command Explanations
gh copilot explain "<command>"                    # Explain command
gh copilot explain "docker run -d nginx"          # Example

# Examples
gh copilot suggest -t git "undo last commit"
gh copilot suggest -t gh "create pr from current branch"
gh copilot suggest -t shell "find large files"
gh copilot explain "kubectl get pods -A"
```

### API & Advanced
```bash
# Direct API Access
gh api <endpoint>                                 # GET request
gh api <endpoint> -X POST                         # POST request
gh api <endpoint> --method DELETE                 # DELETE request
gh api <endpoint> --field key=value               # With parameters
gh api <endpoint> --jq '.items[]'                 # Filter with jq

# Pagination
gh api --paginate <endpoint>                      # Auto-paginate

# Examples
gh api repos/:owner/:repo                         # Repo info
gh api /user                                      # Current user
gh api /rate_limit                                # Rate limit status
```

### Miscellaneous
```bash
# Browse
gh browse                                         # Open repo in browser
gh browse --branch <branch>                       # Open branch
gh browse --settings                              # Repo settings
gh browse <issue-number>                          # Open issue/PR

# Status
gh status                                         # Activity summary
gh status --exclude <types>                       # Exclude types

# GPG & SSH Keys
gh gpg-key list                                   # List GPG keys
gh gpg-key add <file>                             # Add GPG key
gh ssh-key list                                   # List SSH keys
gh ssh-key add <file>                             # Add SSH key

# Gists
gh gist create <file>                             # Create gist
gh gist create --public <file>                    # Public gist
gh gist list                                      # List gists
gh gist view <gist-id>                            # View gist
gh gist edit <gist-id>                            # Edit gist
gh gist delete <gist-id>                          # Delete gist

# Completion
gh completion -s bash                             # Bash completion
gh completion -s zsh                              # Zsh completion
gh completion -s fish                             # Fish completion
```

---

## 💻 CODE GENERATION RULES

### General Principles
1. **ALWAYS generate complete, working code** - no placeholders, no "TODO" comments
2. **Type hints are MANDATORY** for all functions (PEP 484)
3. **Use async/await** for all I/O operations (API calls, database, file operations)
4. **Error handling is REQUIRED** - use specific exceptions, never bare `except:`
5. **Docstrings are REQUIRED** - use Google style for all functions/classes
6. **Follow PEP 8** - max line length 88 characters (Black default)

### Python Code Patterns

#### Function Template
```python
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def function_name(
    param1: str,
    param2: int,
    param3: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Brief description of function.

    Detailed explanation if needed.

    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Description of param3. Defaults to None.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When API call fails
    """
    try:
        # Implementation here
        result = await some_async_operation()
        return result
    except SpecificException as e:
        logger.error(f"Error in function_name: {e}")
        raise ValueError(f"Failed to process: {e}") from e
```

#### FastAPI Route Template
```python
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(prefix="/api/v1", tags=["resource"])

class RequestModel(BaseModel):
    """Request model documentation."""
    field1: str = Field(..., description="Field description")
    field2: int = Field(gt=0, description="Must be positive")

class ResponseModel(BaseModel):
    """Response model documentation."""
    id: str
    status: str

@router.post(
    "/resource",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    description="Detailed endpoint description"
)
async def create_resource(
    data: RequestModel,
    current_user: str = Depends(get_current_user)
) -> ResponseModel:
    """Create a new resource.

    Args:
        data: Resource data
        current_user: Authenticated user

    Returns:
        Created resource

    Raises:
        HTTPException: If creation fails
    """
    try:
        result = await service.create(data)
        return ResponseModel(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

#### BigQuery Client Template
```python
from google.cloud import bigquery
from google.api_core import exceptions
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BigQueryClient:
    """Client for BigQuery operations."""

    def __init__(self, project_id: str, dataset_id: str):
        """Initialize BigQuery client.

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id

    async def insert_row(
        self,
        table_id: str,
        row: Dict[str, Any]
    ) -> str:
        """Insert a row into BigQuery table.

        Args:
            table_id: Table name
            row: Data to insert

        Returns:
            Inserted row ID

        Raises:
            ValueError: If insertion fails
        """
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        
        try:
            errors = self.client.insert_rows_json(table_ref, [row])
            if errors:
                raise ValueError(f"Insert failed: {errors}")
            
            logger.info(f"Row inserted into {table_id}")
            return row.get("id", "unknown")
        except exceptions.GoogleAPIError as e:
            logger.error(f"BigQuery error: {e}")
            raise ValueError(f"Failed to insert: {e}") from e
```

#### Vertex AI Integration Template
```python
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Client for Vertex AI operations."""

    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize Vertex AI client.

        Args:
            project_id: GCP project ID
            location: GCP region
        """
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")

    async def generate_content(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate content using Vertex AI.

        Args:
            prompt: Input prompt
            config: Generation config (temperature, etc.)

        Returns:
            Generated text

        Raises:
            ValueError: If generation fails
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=config or {}
            )
            
            if not response.text:
                raise ValueError("Empty response from model")
            
            logger.info("Content generated successfully")
            return response.text
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise ValueError(f"Failed to generate: {e}") from e
```

### Dockerfile Template
```dockerfile
# Multi-stage build for Cloud Run optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Development stage
FROM base as development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Production stage
FROM base as production

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
```

### Testing Template
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from backend.api.main import app

@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_bigquery():
    """Mock BigQuery client."""
    with patch("backend.database.BigQueryClient") as mock:
        instance = MagicMock()
        instance.insert_row = AsyncMock(return_value="test-id-123")
        mock.return_value = instance
        yield instance

@pytest.mark.asyncio
async def test_endpoint_success(client, mock_bigquery):
    """Test successful API call.

    Args:
        client: FastAPI test client
        mock_bigquery: Mocked BigQuery client
    """
    # Arrange
    payload = {
        "field1": "test_value",
        "field2": 42
    }
    
    # Act
    response = client.post("/api/v1/resource", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == "test-id-123"
    mock_bigquery.insert_row.assert_called_once()

@pytest.mark.asyncio
async def test_endpoint_validation_error(client):
    """Test validation error handling.

    Args:
        client: FastAPI test client
    """
    # Arrange
    invalid_payload = {"field2": -1}  # Missing field1, negative field2
    
    # Act
    response = client.post("/api/v1/resource", json=invalid_payload)
    
    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()
```

---

## 🔨 WHEN GENERATING GITHUB CLI COMMANDS

### Command Generation Rules
1. **ALWAYS use full command syntax** - no shortcuts unless in aliases
2. **Include flags explicitly** - prefer `--flag value` over `-f value`
3. **Add comments** explaining what each command does
4. **Chain commands with `&&`** only if subsequent commands depend on success
5. **Use `gh copilot suggest`** when user asks "how do I..." type questions
6. **Prefer `--web` flag** for complex operations that benefit from browser UI

### Common Task → Command Mappings

#### Starting New Feature
```bash
# When user says: "start working on new feature"
# Generate:
gh issue create --title "Feature: <description>" --label "enhancement" --web
gh issue develop <issue-number> --checkout --base main
```

#### Creating Pull Request
```bash
# When user says: "create PR" or "open pull request"
# Generate:
gh pr create --fill --web

# For draft PR:
gh pr create --draft --fill

# For specific reviewers:
gh pr create --fill --reviewer @user1,@user2
```

#### Checking CI Status
```bash
# When user says: "check if tests passed" or "CI status"
# Generate:
gh pr checks
# Or for specific PR:
gh pr checks <number>

# Watch in real-time:
gh pr checks --watch
```

#### Merging After Approval
```bash
# When user says: "merge PR" or "merge this"
# Generate:
gh pr merge --squash --delete-branch

# Auto-merge when ready:
gh pr merge --auto --squash
```

#### Deploying to Production
```bash
# When user says: "deploy" or "release"
# Generate:
# 1. Trigger workflow
gh workflow run deploy --ref main

# 2. Watch progress
gh run watch

# 3. Create release
gh release create v1.0.0 --generate-notes
```

#### Checking Work Status
```bash
# When user says: "what am I working on" or "my tasks"
# Generate:
gh issue list --assignee @me --state open
gh pr list --author @me --state open
gh status
```

#### Setting Up New Repository
```bash
# When user says: "create new repo" or "initialize project"
# Generate:
gh repo create <name> --private --clone
cd <name>
gh secret set GOOGLE_PROJECT_ID --body "your-project-id"
gh secret set VERTEX_AI_LOCATION --body "us-central1"
gh workflow run setup
```

---

## 🎨 CODE GENERATION SCENARIOS

### Scenario: "Create a service to generate video scripts using Vertex AI"
```python
# Generate this:
from typing import Optional, Dict, Any
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig
import logging

logger = logging.getLogger(__name__)

class ScriptGeneratorService:
    """Service for generating video scripts using Vertex AI."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro"
    ):
        """Initialize script generator.

        Args:
            project_id: GCP project ID
            location: Vertex AI location
            model_name: Model to use for generation
        """
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        logger.info(f"Initialized ScriptGeneratorService with {model_name}")

    async def generate_script(
        self,
        topic: str,
        duration_seconds: int,
        style: str = "educational",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video script based on topic and parameters.

        Args:
            topic: Main topic for the video
            duration_seconds: Target video duration
            style: Script style (educational, entertaining, documentary)
            additional_context: Extra context or requirements

        Returns:
            Dict containing script, title, and metadata

        Raises:
            ValueError: If generation fails or parameters invalid
        """
        if duration_seconds < 30 or duration_seconds > 600:
            raise ValueError("Duration must be between 30 and 600 seconds")

        prompt = self._build_prompt(topic, duration_seconds, style, additional_context)
        
        config = GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=2048
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=config
            )

            if not response.text:
                raise ValueError("Empty response from model")

            script_data = self._parse_response(response.text)
            script_data["metadata"] = {
                "topic": topic,
                "duration": duration_seconds,
                "style": style,
                "model": self.model.model_name
            }

            logger.info(f"Generated script for topic: {topic}")
            return script_data

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise ValueError(f"Failed to generate script: {e}") from e

    def _build_prompt(
        self,
        topic: str,
        duration: int,
        style: str,
        context: Optional[str]
    ) -> str:
        """Build generation prompt.

        Args:
            topic: Video topic
            duration: Duration in seconds
            style: Script style
            context: Additional context

        Returns:
            Formatted prompt
        """
        words_estimate = (duration * 150) // 60  # ~150 words per minute

        prompt = f"""Generate a {style} video script about: {topic}

Requirements:
- Target duration: {duration} seconds (~{words_estimate} words)
- Style: {style}
- Include engaging hook in first 5 seconds
- Clear structure: intro, main content, conclusion
- Natural narration flow

{"Additional context: " + context if context else ""}

Format the response as:
TITLE: [engaging title]
HOOK: [first 5 seconds]
SCRIPT: [full script]
KEY_POINTS: [3-5 bullet points]
"""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse model response into structured data.

        Args:
            response: Raw model response

        Returns:
            Structured script data
        """
        lines = response.strip().split("\n")
        data = {
            "title": "",
            "hook": "",
            "script": "",
            "key_points": []
        }

        current_section = None
        script_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                data["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("HOOK:"):
                data["hook"] = line.replace("HOOK:", "").strip()
            elif line.startswith("SCRIPT:"):
                current_section = "script"
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif current_section == "script" and line:
                script_lines.append(line)
            elif current_section == "key_points" and line.startswith("-"):
                data["key_points"].append(line.lstrip("- "))

        data["script"] = "\n".join(script_lines)
        return data
```

### Scenario: "Create FastAPI endpoint to trigger video generation"
```python
# Generate this:
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
import logging

from backend.services.script_generator import ScriptGeneratorService
from backend.database.bigquery_client import BigQueryClient
from backend.services.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/videos", tags=["videos"])

class VideoStyle(str, Enum):
    """Available video styles."""
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"

class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    
    topic: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Video topic or subject"
    )
    duration_seconds: int = Field(
        ...,
        ge=30,
        le=600,
        description="Target video duration (30-600 seconds)"
    )
    style: VideoStyle = Field(
        default=VideoStyle.EDUCATIONAL,
        description="Video style"
    )
    additional_context: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional context or requirements"
    )
    tags: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Video tags"
    )

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]

class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    
    job_id: str = Field(..., description="Generation job ID")
    status: str = Field(..., description="Job status")
    estimated_completion_time: int = Field(
        ...,
        description="Estimated time in seconds"
    )
    message: str = Field(..., description="Status message")

@router.post(
    "/generate",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate new video",
    description="Initiate video generation process using AI"
)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    script_service: ScriptGeneratorService = Depends(get_script_service),
    db_client: BigQueryClient = Depends(get_db_client)
) -> VideoGenerationResponse:
    """Generate a new video based on provided parameters.

    This endpoint initiates an asynchronous video generation process:
    1. Generates script using Vertex AI
    2. Creates visual assets
    3. Renders final video
    4. Uploads to Cloud Storage

    Args:
        request: Video generation parameters
        background_tasks: FastAPI background tasks
        current_user: Authenticated user ID
        script_service: Script generation service
        db_client: BigQuery client

    Returns:
        Generation job details

    Raises:
        HTTPException: If generation cannot be initiated
    """
    try:
        # Create job record
        job_id = await db_client.create_job(
            user_id=current_user,
            job_type="video_generation",
            parameters=request.dict()
        )

        # Estimate completion time based on duration
        estimated_time = estimate_generation_time(request.duration_seconds)

        # Queue background task
        background_tasks.add_task(
            process_video_generation,
            job_id=job_id,
            request=request,
            user_id=current_user,
            script_service=script_service,
            db_client=db_client
        )

        logger.info(
            f"Video generation initiated: {job_id} for user {current_user}"
        )

        return VideoGenerationResponse(
            job_id=job_id,
            status="queued",
            estimated_completion_time=estimated_time,
            message=f"Video generation started. Job ID: {job_id}"
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Generation initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate video generation"
        )

@router.get(
    "/{job_id}/status",
    response_model=Dict[str, Any],
    summary="Get generation status",
    description="Check status of video generation job"
)
async def get_generation_status(
    job_id: str,
    current_user: str = Depends(get_current_user),
    db_client: BigQueryClient = Depends(get_db_client)
) -> Dict[str, Any]:
    """Get status of video generation job.

    Args:
        job_id: Generation job ID
        current_user: Authenticated user
        db_client: BigQuery client

    Returns:
        Job status details

    Raises:
        HTTPException: If job not found or access denied
    """
    try:
        job = await db_client.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        if job["user_id"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status"
        )

async def process_video_generation(
    job_id: str,
    request: VideoGenerationRequest,
    user_id: str,
    script_service: ScriptGeneratorService,
    db_client: BigQueryClient
) -> None:
    """Background task to process video generation.

    Args:
        job_id: Job ID
        request: Generation request
        user_id: User ID
        script_service: Script service
        db_client: Database client
    """
    try:
        # Update status: generating script
        await db_client.update_job_status(job_id, "generating_script")
        
        # Generate script
        script_data = await script_service.generate_script(
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=request.style.value,
            additional_context=request.additional_context
        )
        
        # Update with script
        await db_client.update_job_data(job_id, {"script": script_data})
        
        # Continue with other steps...
        # (video rendering, asset creation, etc.)
        
        await db_client.update_job_status(job_id, "completed")
        logger.info(f"Video generation completed: {job_id}")
        
    except Exception as e:
        logger.error(f"Video generation failed for {job_id}: {e}")
        await db_client.update_job_status(
            job_id,
            "failed",
            error=str(e)
        )

def estimate_generation_time(duration: int) -> int:
    """Estimate generation time based on video duration.

    Args:
        duration: Video duration in seconds

    Returns:
        Estimated time in seconds
    """
    # Rough estimate: 5x the video duration + base overhead
    return (duration * 5) + 120
```

---

## 🚀 COMMAND GENERATION FOR COMMON WORKFLOWS

### Workflow: Complete Feature Development
```bash
# When user says: "I want to develop a new feature from scratch"
# Generate this sequence:

# 1. Create and checkout feature branch
gh copilot suggest -t git "create feature branch for user authentication"

# 2. Make changes, then commit
git add .
git commit -m "feat: implement user authentication

- Add JWT token generation
- Implement login/logout endpoints
- Add middleware for protected routes"

# 3. Push and create PR
git push -u origin feature/user-auth
gh pr create --fill --draft

# 4. When ready for review
gh pr ready
gh pr edit --add-reviewer @team-lead

# 5. Address review comments
git add .
git commit -m "fix: address review comments"
git push

# 6. After approval, merge
gh pr merge --squash --delete-branch
```

### Workflow: Hotfix Production Issue
```bash
# When user says: "need to hotfix production bug"
# Generate:

# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Make fix and commit
git add .
git commit -m "fix: resolve critical production bug

Fixes #123"

# 3. Fast-track PR
gh pr create --title "HOTFIX: Critical bug fix" --label "priority:critical" --base main
gh pr merge --admin --squash  # If you have admin rights

# 4. Create immediate release
gh release create v1.0.1 --notes "Hotfix for critical bug" --target main

# 5. Trigger deployment
gh workflow run deploy-production --ref main
```

### Workflow: Code Review
```bash
# When user says: "review this PR" or "check PR #42"
# Generate:

# 1. Checkout PR locally
gh pr checkout 42

# 2. Run tests
pytest tests/ -v

# 3. Check CI status
gh pr checks 42

# 4. Review code
gh pr diff 42

# 5. Approve or request changes
gh pr review 42 --approve --body "LGTM! Great work on error handling."
# OR
gh pr review 42 --request-changes --body "Please add tests for edge cases"

# 6. If approved and CI passes, merge
gh pr merge 42 --squash
```

---

## 🔐 SECRETS MANAGEMENT COMMANDS

### Setting Up Project Secrets
```bash
# When user says: "configure GCP secrets" or "setup environment"
# Generate:

# Google Cloud credentials (never commit!)
gh secret set GOOGLE_APPLICATION_CREDENTIALS < service-account-key.json

# Project configuration
gh secret set GOOGLE_PROJECT_ID --body "video-genius-prod"
gh secret set VERTEX_AI_LOCATION --body "us-central1"
gh secret set BIGQUERY_DATASET --body "video_data"
gh secret set CLOUD_STORAGE_BUCKET --body "video-genius-assets"

# API keys
gh secret set YOUTUBE_API_KEY --body "your-youtube-api-key"
gh secret set OPENAI_API_KEY --body "your-openai-key"

# Application secrets
gh secret set JWT_SECRET_KEY --body "$(openssl rand -hex 32)"
gh secret set DATABASE_URL --body "postgresql://..."

# List all secrets to verify
gh secret list
```

---

## 📊 MONITORING & DEBUGGING COMMANDS

### Check Application Health
```bash
# When user says: "check if everything is working" or "system status"
# Generate:

# Check recent workflow runs
gh run list --limit 5

# Check if latest deployment succeeded
gh run view --log

# View current issues
gh issue list --label "bug" --state open

# Check PR that need attention
gh pr list --review-requested @me

# Overall status
gh status
```

---

## 🎯 COPILOT BEHAVIOR INSTRUCTIONS

### When User Asks Questions
1. **"How do I..."** → Use `gh copilot suggest` in your response
2. **"Create/Generate..."** → Generate complete code immediately
3. **"Fix this error..."** → Analyze, then provide fixed code
4. **"Explain..."** → Brief explanation + working code example

### Priority Order
1. **Generate working code** (highest priority)
2. Add necessary imports
3. Include error handling
4. Add type hints
5. Write docstrings
6. Add logging
7. Brief comment if complex logic

### Never Do
- ❌ Use placeholder like `# TODO`, `# Your code here`, `pass`
- ❌ Generate incomplete code
- ❌ Skip error handling
- ❌ Omit type hints
- ❌ Write code without docstrings
- ❌ Use bare `except:`
- ❌ Hard-code secrets or credentials

### Always Do
- ✅ Generate complete, runnable code
- ✅ Use async/await for I/O
- ✅ Include all imports
- ✅ Add proper error handling
- ✅ Use type hints everywhere
- ✅ Write Google-style docstrings
- ✅ Log important operations
- ✅ Use environment variables for config

---

## 🎓 EXAMPLES OF GOOD RESPONSES

### User: "create issue for the bug I found"

### User: "make a function to upload video to cloud storage"

---

## 🚀 START GENERATING CODE NOW

Remember: Your primary goal is to **GENERATE WORKING CODE**. When the user asks for anything:
1. Understand the requirement
2. Generate complete, production-ready code immediately
3. Include all necessary components (imports, error handling, types, docs)
4. Use appropriate gh CLI commands when relevant

**ALWAYS prioritize code generation over explanations.**