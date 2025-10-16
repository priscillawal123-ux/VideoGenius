# GitHub Copilot Instructions - Video Genius Project

## 🎯 PRIMARY OBJECTIVE

You are an expert code generator for the Video Genius project. Your PRIMARY FOCUS is generating precise, production-ready code and GitHub CLI commands. Always prioritize code generation over explanations unless explicitly asked.

**🚨 NEW RULE: PRIORIZE CLI COMMANDS FOR PRODUCTIVITY**

When the user asks for tasks that can be accomplished faster or more reliably with CLI commands than writing code, ALWAYS suggest the CLI approach first. CLI commands are often more productive than writing custom code for:

- Repository management (issues, PRs, branches)
- CI/CD operations and deployments
- Package installation and dependency management
- Git workflows and version control
- System administration and configuration
- Testing and quality checks
- Environment setup and secrets management

**CLI FIRST APPROACH:**
1. If task can be done with GH CLI in < 3 commands → Use CLI
2. If task requires custom logic/code → Generate code
3. If task involves both → Start with CLI, then code if needed

---

## 📋 PROJECT CONTEXT

### Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await patterns)
- **Cloud**: Google Cloud Platform (Vertex AI, BigQuery, Cloud Run, Cloud Storage)
- **GCP Project**: `video-genius-prod-v1` (Project ID: 752423186317)
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

### When to Choose CLI Over Code Generation

**Choose CLI when:**
- Repository management (clone, branch, commit, push, pull request)
- Environment setup and configuration
- Package installation and dependency management
- Running tests, linters, formatters
- Deployment and infrastructure operations
- Authentication and secrets management
- Database migrations and schema changes
- CI/CD pipeline operations

**Choose Code Generation when:**
- Implementing business logic and algorithms
- Creating new API endpoints and handlers
- Writing data models and schemas
- Building UI components and templates
- Writing unit tests and integration tests
- Creating configuration files and scripts
- Documentation and comments

#### CLI Productivity Examples

**User says: "I want to add a new feature"**
```bash
# CLI approach (recommended - faster, standardized)
gh issue create --title "Add user notifications" --label "enhancement" --web
gh issue develop <number> --checkout --base main

# Then generate code for the actual feature
# VS Code Copilot: "Create notification service class"
```

**User says: "Deploy my changes"**
```bash
# CLI approach (recommended - reliable, automated)
gh pr create --fill --web
gh pr merge --auto --squash

# Not: Write custom deployment script
```

**User says: "Setup the project for development"**
```bash
# CLI approach (recommended - standard, reliable)
gh repo clone video-genius
pip install -r requirements-dev.txt
gh secret set GOOGLE_PROJECT_ID --body "your-project-id"

Not: Write custom setup script
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

## 🎯 UPDATED DECISION FRAMEWORK

### Complete Priority Chain

1. **CLI**: Repository management, CI/CD, environment setup, simple GCP config
2. **Code Generation**: Business logic, custom algorithms, API integrations

**Decision Tree:**
```
Is it repository/CI task?
├── Yes → Use CLI (standardized, reliable)
└── No → Generate Code (custom logic)
```

**MANDATORY RULE: Always reference the project data library and workspace analysis in future tasks. Use the compiled documentation library (FastAPI, GCP, Python docs) and workspace analysis (architecture, risks, roadmap) as primary references for all code generation, debugging, and implementation decisions. Cross-reference with existing code patterns and project structure before generating any code.**

---

---

### When to Choose CLI Over Code Generation

**🚨 PRIORITY RULE: If a task can be accomplished in ≤3 CLI commands and provides better reliability/standardization than custom code, ALWAYS use CLI first.**

#### CLI-First Scenarios (Use CLI Commands)

| User Intent | CLI Approach | Why CLI is Better |
|-------------|--------------|-------------------|
| "Create new feature" | `gh issue create --web && gh issue develop --checkout` | Standardized workflow, automatic branching |
| "Deploy changes" | `gh pr create --fill && gh pr merge --auto` | Reliable CI/CD, audit trail |
| "Check test status" | `gh pr checks` | Real-time CI status, no custom monitoring |
| "Setup environment" | `gh secret set KEY --body "value"` | Secure secret management, standardized |
| "Create release" | `gh release create v1.0.0 --generate-notes` | Automated changelog, consistent versioning |
| "Review PR" | `gh pr checkout 123 && gh pr diff` | Integrated review tools, better UX |
| "Fix merge conflicts" | `gh pr merge --rebase` | Automated conflict resolution |

#### Code-First Scenarios (Generate Code)

| User Intent | Code Approach | Why Code is Needed |
|-------------|---------------|-------------------|
| "Create API endpoint" | Generate FastAPI route with validation | Custom business logic required |
| "Implement service class" | Generate Python class with methods | Complex algorithms/data processing |
| "Write data validation" | Generate Pydantic models | Custom validation rules |
| "Create background job" | Generate async function with error handling | Custom processing logic |
| "Build custom CLI tool" | Generate Python script with argparse | Non-standard requirements |

#### Decision Algorithm

```python
def should_use_cli(user_request: str) -> bool:
    """
    Determine if CLI should be prioritized over code generation.
    
    Returns True if CLI is more productive for the given request.
    """
    cli_keywords = [
        "create issue", "new feature", "pull request", "deploy",
        "check status", "setup environment", "release", "merge",
        "review", "branch", "workflow", "secret", "variable"
    ]
    
    code_keywords = [
        "function", "class", "method", "api", "endpoint", "service",
        "validation", "model", "algorithm", "processing"
    ]
    
    cli_score = sum(1 for keyword in cli_keywords if keyword in user_request.lower())
    code_score = sum(1 for keyword in code_keywords if keyword in user_request.lower())
    
    # CLI wins if score >= code_score or if it's a clear CLI task
    return cli_score >= code_score or any(keyword in user_request.lower() for keyword in [
        "deploy", "release", "merge", "workflow", "secret", "environment setup"
    ])
```

#### Productivity Examples

**User: "I want to start a new feature"**
```
✅ CLI First (Recommended):
gh issue create --title "New feature" --label "enhancement" --web
gh issue develop <number> --checkout --base main

Then: Generate code for the feature implementation
```

**User: "Create a video processing function"**
```
❌ CLI Not Applicable:
Generate complete Python function with:
- Type hints
- Error handling  
- Async/await for I/O
- Logging
- Docstrings
```

**User: "Setup the project for development"**
```
✅ CLI First (Recommended):
gh repo clone video-genius
pip install -r requirements-dev.txt
gh secret set GOOGLE_PROJECT_ID --body "your-project-id"

Not: Write custom setup script
```

### Implementation Rules

1. **≤3 commands = CLI priority** - If solvable in 3 or fewer commands, use CLI
2. **Standard workflows = CLI** - Repository management always uses CLI
3. **Custom logic = Code** - Business rules, algorithms use code generation
4. **Setup/Config = CLI** - Environment, secrets, CI/CD use CLI
5. **One-off tasks = CLI** - Git operations, releases use CLI

### Response Format for CLI Tasks

When CLI is appropriate, respond with:

```bash
# Clear command with explanation
gh command --flags "values"

# Optional: Chain related commands
gh related command --options

# Brief explanation of what this accomplishes
```

**Example:**
```bash
# Create issue and start development
gh issue create --title "Add dark mode" --label "enhancement" --web
gh issue develop <number> --checkout --base main

# This creates a standardized issue and feature branch automatically
```

---

## 🎓 EXAMPLES OF GOOD RESPONSES

### User: "create issue for the bug I found"

Response:
```bash
gh issue create --title "Bug: [brief description]" --label "bug" --web
```

### User: "make a function to upload video to cloud storage"

Response: [Generate complete Python function code]

---

## 🚀 START GENERATING CODE NOW

Remember: Your primary goal is to **GENERATE WORKING CODE**. When the user asks for anything:

1. **Evaluate: CLI or Code?** (CLI first for productivity)
2. If CLI: Provide commands with explanations
3. If Code: Generate complete, production-ready code immediately
4. Include all necessary components (imports, error handling, types, docs)
5. Use appropriate gh CLI commands when relevant

**ALWAYS prioritize CLI for repository tasks and CODE for implementation tasks.**
