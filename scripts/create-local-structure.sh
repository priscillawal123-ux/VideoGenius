#!/bin/bash
# Script para criar estrutura completa do projeto Video Genius localmente
# Execute: chmod +x create-local-structure.sh && ./create-local-structure.sh

set -e

echo "🏗️  Criando estrutura completa do projeto Video Genius..."
echo ""

# Criar diretórios base
echo "📁 Criando diretórios base..."
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .vscode
mkdir -p backend/api/routes
mkdir -p backend/services
mkdir -p backend/models
mkdir -p backend/database
mkdir -p backend/storage
mkdir -p backend/core
mkdir -p backend/utils
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p scripts/gh-helpers
mkdir -p docs

echo "✅ Diretórios criados"
echo ""

# Criar arquivos __init__.py
echo "📄 Criando arquivos __init__.py..."
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/api/routes/__init__.py
touch backend/services/__init__.py
touch backend/models/__init__.py
touch backend/database/__init__.py
touch backend/storage/__init__.py
touch backend/core/__init__.py
touch backend/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/e2e/__init__.py

echo "✅ Arquivos __init__.py criados"
echo ""

# Criar arquivos base do backend
echo "🔧 Criando arquivos base do backend..."

# backend/api/main.py
cat > backend/api/main.py << 'EOF'
"""
Main FastAPI application for Video Genius.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.core.config import get_settings
from backend.core.logging import setup_logging

# Setup logging
setup_logging()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Video Genius API...")

    yield

    # Shutdown
    print("🛑 Shutting down Video Genius API...")

def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Video Genius API",
        description="AI-powered video generation platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    return app

app = create_application()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Video Genius API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
EOF

# backend/core/config.py
cat > backend/core/config.py << 'EOF'
"""
Configuration management using Pydantic Settings.
"""
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://video-genius.com",
        ]
    )

    # Google Cloud
    google_project_id: str = Field(..., env="GOOGLE_PROJECT_ID")
    vertex_ai_location: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    bigquery_dataset: str = Field(default="video_data", env="BIGQUERY_DATASET")
    cloud_storage_bucket: str = Field(..., env="CLOUD_STORAGE_BUCKET")

    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")

    # YouTube API
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = None

def get_settings() -> Settings:
    """Get application settings."""
    global settings
    if settings is None:
        settings = Settings()
    return settings
EOF

# backend/core/logging.py
cat > backend/core/logging.py << 'EOF'
"""
Logging configuration for Video Genius.
"""
import logging
import sys
from typing import Optional

from backend.core.config import get_settings

def setup_logging(level: Optional[str] = None) -> None:
    """Setup logging configuration."""
    settings = get_settings()

    # Determine log level
    if level is None:
        level = "DEBUG" if settings.environment == "development" else "INFO"

    # Create logger
    logger = logging.getLogger("video_genius")
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(console_handler)

    # Set logging for external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(f"video_genius.{name}")
EOF

echo "✅ Arquivos base criados"
echo ""

# Criar arquivos de configuração
echo "⚙️  Criando arquivos de configuração..."

# pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "video-genius"
version = "0.1.0"
description = "AI-powered video generation platform"
authors = ["Video Genius Team <team@video-genius.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = {extras = ["settings"], version = "^2.5.0"}
google-cloud-aiplatform = "^1.39.0"
google-cloud-bigquery = "^3.13.0"
google-cloud-storage = "^2.10.0"
python-multipart = "^0.0.6"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
ruff = "^0.1.7"
mypy = "^1.7.1"
pre-commit = "^3.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=backend --cov-report=term-missing"
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic[settings]==2.5.0
google-cloud-aiplatform==1.39.0
google-cloud-bigquery==3.13.0
google-cloud-storage==2.10.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
EOF

# requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
-r requirements.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
ruff==0.1.7
mypy==1.7.1
pre-commit==3.5.0
EOF

# .env.example
cat > .env.example << 'EOF'
# Environment
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8080

# Google Cloud
GOOGLE_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
BIGQUERY_DATASET=video_data
CLOUD_STORAGE_BUCKET=video-genius-assets

# Security
JWT_SECRET_KEY=your-secret-key-here

# YouTube API (optional)
YOUTUBE_API_KEY=your-youtube-api-key
EOF

echo "✅ Arquivos de configuração criados"
echo ""

# Criar arquivos de teste
echo "🧪 Criando estrutura de testes..."

# tests/conftest.py
cat > tests/conftest.py << 'EOF'
"""
Pytest fixtures and configuration.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def setup_test_environment():
    """Setup test environment variables."""
    # Mock environment variables for testing
    import os
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("GOOGLE_PROJECT_ID", "test-project")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
    os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
EOF

# tests/unit/test_api.py
cat > tests/unit/test_api.py << 'EOF'
"""
Unit tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Video Genius API" in data["message"]

def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
EOF

echo "✅ Estrutura de testes criada"
echo ""

# Criar arquivos GitHub
echo "🐙 Criando arquivos GitHub..."

# .github/copilot-instructions.md
cat > .github/copilot-instructions.md << 'EOF'
# GitHub Copilot Instructions - Video Genius Project

## 🎯 PRIMARY OBJECTIVE
You are an expert code generator for the Video Genius project. Your PRIMARY FOCUS is generating precise, production-ready code and GitHub CLI commands. Always prioritize code generation over explanations unless explicitly asked.

## 📋 PROJECT CONTEXT

### Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await patterns)
- **Cloud**: Google Cloud Platform (Vertex AI, BigQuery, Cloud Storage)
- **Containerization**: Docker
- **Version Control**: Git + GitHub CLI (gh)

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
└── scripts/              # Automation scripts
```

## 💻 CODE GENERATION RULES

### General Principles
1. **ALWAYS generate complete, working code** - no placeholders, no "TODO" comments
2. **Type hints are MANDATORY** for all functions (PEP 484)
3. **Use async/await** for all I/O operations (API calls, database, file operations)
4. **Error handling is REQUIRED** - use specific exceptions, never bare `except:`
5. **Docstrings are REQUIRED** - use Google style for all functions/classes
6. **Follow PEP 8** - max line length 88 characters

### Function Template
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

## 🔨 WHEN GENERATING GITHUB CLI COMMANDS

### Command Generation Rules
1. **ALWAYS use full command syntax** - no shortcuts unless in aliases
2. **Include flags explicitly** - prefer `--flag value` over `-f value`
3. **Add comments** explaining what each command does
4. **Chain commands with `&&`** only if subsequent commands depend on success

### Common Task → Command Mappings

#### Starting New Feature
```bash
# Create and checkout feature branch
gh issue create --title "Feature: <description>" --label "enhancement" --web
gh issue develop <issue-number> --checkout --base main
```

#### Creating Pull Request
```bash
# Create PR from current branch
gh pr create --fill --web
```

#### Checking CI Status
```bash
# Check CI status for PR
gh pr checks
```

## 🎯 COPILOT BEHAVIOR INSTRUCTIONS

### When User Asks Questions
1. **"How do I..."** → Use `gh copilot suggest` in your response
2. **"Create/Generate..."** → Generate complete code immediately
3. **"Fix this error..."** → Analyze, then provide fixed code

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

## 🚀 START GENERATING CODE NOW

Remember: Your primary goal is to **GENERATE WORKING CODE**. When the user asks for anything:
1. Understand the requirement
2. Generate complete, production-ready code immediately
3. Include all necessary components (imports, error handling, types, docs)
4. Use appropriate gh CLI commands when relevant

**ALWAYS prioritize code generation over explanations.**
EOF

echo "✅ Arquivos GitHub criados"
echo ""

# Criar arquivos VS Code
echo "💻 Criando arquivos VS Code..."

# .vscode/settings.json
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": "explicit",
        "source.organizeImports.ruff": "explicit"
    },
    "files.exclude": {
        "**/.venv": true,
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
EOF

# .vscode/extensions.json
cat > .vscode/extensions.json << 'EOF'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "ms-vscode.vscode-json",
        "GitHub.copilot",
        "GitHub.copilot-chat",
        "ms-vscode-remote.remote-containers",
        "ms-azuretools.vscode-docker"
    ]
}
EOF

echo "✅ Arquivos VS Code criados"
echo ""

# Criar README.md
echo "📖 Criando README.md..."

cat > README.md << 'EOF'
# 🎬 Video Genius

AI-powered video generation platform built with FastAPI and Google Cloud Platform.

## 🚀 Features

- 🤖 AI-powered script generation using Vertex AI
- 🎥 Automated video rendering
- ☁️ Cloud storage integration (Google Cloud Storage)
- 📊 Analytics and reporting (BigQuery)
- 🔐 Secure authentication
- 📱 RESTful API

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI/ML**: Google Cloud Vertex AI (Gemini)
- **Database**: Google BigQuery
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run
- **Testing**: pytest, pytest-cov
- **Linting**: ruff, mypy, black

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Platform account
- GitHub CLI (gh)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/video-genius.git
   cd video-genius
   ```

2. **Setup environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud credentials
   ```

4. **Run the application**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

5. **Run tests**
   ```bash
   pytest
   ```

## 📚 API Documentation

Once the application is running, visit:
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_api.py
```

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Production
```bash
# Deploy to Google Cloud Run
gcloud run deploy video-genius \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email team@video-genius.com or create an issue in this repository.
EOF

echo "✅ README.md criado"
echo ""

# Criar .gitignore
echo "🚫 Criando .gitignore..."

cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp

# Google Cloud
google-cloud-key.json
EOF

echo "✅ .gitignore criado"
echo ""

echo "🎉 Estrutura completa do projeto Video Genius criada com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas variáveis de ambiente: cp .env.example .env"
echo "2. Instale as dependências: pip install -r requirements-dev.txt"
echo "3. Execute os testes: pytest"
echo "4. Inicie o servidor: uvicorn backend.api.main:app --reload"
echo ""
echo "📚 Documentação:"
echo "- API Docs: http://localhost:8080/docs"
echo "- Health Check: http://localhost:8080/health"
echo ""
echo "🐙 GitHub:"
echo "- Ver issues: gh issue list"
echo "- Criar PR: gh pr create --fill"
echo ""
echo "✅ Setup completo! 🎬"
EOF

# Tornar executável
chmod +x create-local-structure.sh

echo "✅ Script criado: create-local-structure.sh"
echo ""

echo "🎯 Para executar o script:"
echo "   ./create-local-structure.sh"
echo ""
echo "📝 Ou copie e execute o comando diretamente:"
echo "   mkdir -p .github/workflows .github/ISSUE_TEMPLATE .vscode backend/api/routes backend/services backend/models backend/database backend/storage backend/core backend/utils tests/unit tests/integration tests/e2e scripts/gh-helpers docs && touch backend/__init__.py backend/api/__init__.py backend/api/routes/__init__.py backend/services/__init__.py backend/models/__init__.py backend/database/__init__.py backend/storage/__init__.py backend/core/__init__.py backend/utils/__init__.py tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/e2e/__init__.py"
echo ""
echo "✅ Comando gh CLI pronto!"</content>
<parameter name="filePath">/models/workspaces/ai-assistant/video-genius.code-workspace/scripts/create-local-structure.sh