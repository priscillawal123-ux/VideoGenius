# 📁 Estrutura do Projeto Video Genius

## Visão Geral da Estrutura

```
video-genius/
├── .github/                      # GitHub configurations
│   ├── workflows/                # CI/CD pipelines
│   │   ├── test.yml             # Run tests on PR
│   │   ├── deploy-staging.yml   # Deploy to staging
│   │   └── deploy-prod.yml      # Deploy to production
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── copilot-instructions.md  # Copilot context (CRITICO!)
│
├── .vscode/                      # VS Code workspace config
│   ├── settings.json            # Editor settings
│   ├── extensions.json          # Recommended extensions
│   ├── tasks.json               # Automated tasks
│   ├── launch.json              # Debug configurations
│   └── keybindings.json         # Custom keyboard shortcuts
│
├── backend/                      # Application code
│   ├── __init__.py
│   ├── api/                     # FastAPI routes
│   │   ├── __init__.py
│   │   ├── main.py             # App initialization
│   │   ├── dependencies.py     # Shared dependencies
│   │   └── routes/             # API endpoints
│   │       ├── __init__.py
│   │       ├── videos.py       # Video generation endpoints
│   │       ├── health.py       # Health check
│   │       └── auth.py         # Authentication
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── script_generator.py # Vertex AI script generation
│   │   ├── video_renderer.py  # Video rendering service
│   │   ├── asset_manager.py   # Asset management
│   │   └── youtube_uploader.py # YouTube API integration
│   │
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── video.py            # Video models
│   │   ├── user.py             # User models
│   │   └── job.py              # Job models
│   │
│   ├── database/                # Database clients
│   │   ├── __init__.py
│   │   ├── bigquery_client.py  # BigQuery operations
│   │   └── schemas.py          # Table schemas
│   │
│   ├── storage/                 # Storage operations
│   │   ├── __init__.py
│   │   └── gcs_client.py       # Google Cloud Storage
│   │
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── logging.py          # Logging setup
│   │   ├── security.py         # Auth & security
│   │   └── exceptions.py       # Custom exceptions
│   │
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       ├── validators.py       # Data validation
│       └── helpers.py          # General helpers
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_services.py
│   │   └── test_models.py
│   ├── integration/            # Integration tests
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/                    # End-to-end tests
│       └── test_video_flow.py
│
├── scripts/                     # Automation scripts
│   ├── setup.sh                # Complete environment setup
│   ├── deploy.sh               # Deployment script
│   ├── migrate.sh              # Database migrations
│   └── gh-helpers/             # GitHub CLI helper scripts
│       ├── quick-pr.sh
│       └── sync-fork.sh
│
├── docs/                        # Documentation
│   ├── QUICK_REFERENCE.md      # Quick command reference
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── API.md                  # API documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── CONTRIBUTING.md         # Contribution guidelines
│
├── .env.example                 # Environment variables template
├── .env.local                   # Local development env (gitignored)
├── .gitignore                   # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks config
├── pyproject.toml              # Python project config
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Local development compose
├── README.md                   # Project README
└── video-genius.code-workspace # VS Code workspace file
```

## 📂 Descrição dos Diretórios

### `/backend` - Código da Aplicação

#### `/backend/api` - Camada de API
- **main.py**: Inicialização do FastAPI, middlewares, CORS
- **dependencies.py**: Dependências compartilhadas (auth, DB clients)
- **routes/**: Endpoints organizados por domínio

#### `/backend/services` - Lógica de Negócio
- Serviços isolados e testáveis
- Cada serviço tem responsabilidade única
- Usa async/await para operações I/O

#### `/backend/models` - Modelos de Dados
- Pydantic models para validação
- Request/Response schemas
- Database models

#### `/backend/database` - Acesso a Dados
- Clients para BigQuery
- Queries SQL organizadas
- Schema definitions

#### `/backend/storage` - Armazenamento
- Client para Cloud Storage
- Upload/download de arquivos
- Gerenciamento de assets

#### `/backend/core` - Núcleo da Aplicação
- Configurações centralizadas
- Logging configurado
- Segurança e autenticação
- Exceções customizadas

### `/tests` - Testes

#### `/tests/unit` - Testes Unitários
- Testa funções/métodos isoladamente
- Usa mocks para dependências externas
- Rápido de executar

#### `/tests/integration` - Testes de Integração
- Testa integração entre componentes
- Pode usar emuladores (BigQuery, GCS)
- Mais lento que unitários

#### `/tests/e2e` - Testes End-to-End
- Testa fluxo completo da aplicação
- Usa ambiente de teste real
- Executado em CI/CD

### `/.github` - Configurações GitHub

#### `/workflows` - CI/CD
- Automação de build, test, deploy
- Executado em eventos (push, PR, etc)

#### `/ISSUE_TEMPLATE` - Templates de Issues
- Padroniza criação de issues
- Coleta informações necessárias

#### `copilot-instructions.md` - 🎯 CRÍTICO
- **Arquivo mais importante para Copilot!**
- Contém todo contexto do projeto
- Comandos gh CLI completos
- Padrões de código
- **Copilot lê este arquivo automaticamente**

### `/scripts` - Automação

- **setup.sh**: Setup completo do ambiente
- **deploy.sh**: Deploy automatizado
- **gh-helpers/**: Scripts auxiliares para gh CLI

## 🎯 Arquivos Críticos para o Copilot

### 1. `.github/copilot-instructions.md` (MAIS IMPORTANTE)
```markdown
# Contém:
- Contexto completo do projeto
- Stack tecnológica
- TODOS os comandos gh CLI
- Padrões de código
- Templates de código
- Workflows comuns
```

### 2. `pyproject.toml`
```toml
# Configurações de:
- Black (formatação)
- Ruff (linting)
- MyPy (type checking)
- Pytest (testing)
```

### 3. `.vscode/settings.json`
```json
# Configurações do Copilot:
- Linguagens habilitadas
- Auto-completions
- Chat settings
```

## 📝 Comandos para Criar Estrutura

### Criar Diretórios Base
```bash
# Copilot vai gerar isso quando você pedir:
# "criar estrutura de diretórios do projeto"

mkdir -p backend/{api/routes,services,models,database,storage,core,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p scripts/gh-helpers
mkdir -p docs
mkdir -p .github/{workflows,ISSUE_TEMPLATE}
```

### Criar Arquivos __init__.py
```bash
# Copilot vai gerar isso quando você pedir:
# "criar arquivos init em todos os diretórios python"

find backend tests -type d -exec touch {}/__init__.py \;
```

### Usar gh CLI para Setup
```bash
# Criar repositório
gh repo create video-genius --private --clone

# Adicionar labels úteis
gh label create "priority:critical" --color "d93f0b"
gh label create "priority:high" --color "e99695"
gh label create "type:feature" --color "0e8a16"
gh label create "type:bug" --color "d73a4a"
gh label create "status:in-progress" --color "fbca04"

# Criar issue template
gh api repos/:owner/:repo/contents/.github/ISSUE_TEMPLATE/bug_report.md \
  -X PUT \
  -f message="Add bug report template" \
  -f content="$(base64 < bug_report.md)"
```

## 🎨 Templates de Arquivos

### backend/api/main.py
```python
"""
Main FastAPI application.

Use este template como base.
Copilot vai expandir quando você pedir:
"criar aplicação FastAPI principal"
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.api.routes import videos, health, auth

# Setup logging
setup_logging()

# Create app
app = FastAPI(
    title="Video Genius API",
    description="AI-powered video generation for YouTube",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(videos.router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    pass
```

### backend/core/config.py
```python
"""
Configuration management using Pydantic Settings.

Copilot vai expandir quando você pedir:
"criar configuração da aplicação"
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""

    # App
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080

    # Google Cloud
    GOOGLE_PROJECT_ID: str
    VERTEX_AI_LOCATION: str = "us-central1"
    BIGQUERY_DATASET: str
    CLOUD_STORAGE_BUCKET: str

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env.local"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings()
```

### tests/conftest.py
```python
"""
Pytest fixtures shared across tests.

Copilot vai expandir quando você pedir:
"criar fixtures de teste"
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from backend.api.main import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client."""
    mock = MagicMock()
    mock.insert_row = AsyncMock(return_value="test-id")
    mock.query = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI client."""
    mock = MagicMock()
    mock.generate_content = AsyncMock(return_value="Generated content")
    return mock
```

## 🚀 Uso com GitHub Copilot

### Como Pedir ao Copilot

#### ✅ BONS EXEMPLOS:
```python
# No arquivo backend/services/script_generator.py
# Escreva um comentário descritivo:

# criar serviço que gera roteiros de vídeo usando Vertex AI
# deve aceitar tópico, duração e estilo
# retornar script, título e key points
# usar async/await e tratamento de erros completo

# Copilot vai gerar o código completo baseado em copilot-instructions.md!
```

```bash
# No terminal, use gh copilot:
gh copilot suggest -t shell "criar todos os diretórios do backend"
gh copilot suggest -t git "criar branch para feature de geração de vídeo"
gh copilot suggest -t gh "criar issue para implementar API de vídeos"
```

#### ❌ MAUS EXEMPLOS:
```python
# muito vago
# fazer função

# sem contexto
# criar API

# incompleto
# video service
```

### Workflow com Copilot

1. **Abra arquivos relacionados** - Copilot usa contexto de tabs abertas
2. **Escreva comentário descritivo** - Seja específico
3. **Deixe Copilot sugerir** - Aceite com Tab
4. **Refine se necessário** - Use Copilot Chat (Ctrl+I)

## 📋 Checklist de Setup

### Inicial
```bash
- [ ] Clonar repositório (gh repo clone)
- [ ] Executar scripts/setup.sh
- [ ] Ativar ambiente virtual (source .venv/bin/activate)
- [ ] Configurar .env.local
- [ ] Testar autenticação GCP (gcloud auth login)
- [ ] Verificar gh CLI (gh auth status)
```

### Desenvolvimento
```bash
- [ ] Criar estrutura de diretórios
- [ ] Criar arquivos __init__.py
- [ ] Configurar pre-commit hooks
- [ ] Rodar testes iniciais (pytest tests/)
- [ ] Testar build Docker (docker build -t video-genius:dev .)
```

### CI/CD
```bash
- [ ] Configurar secrets no GitHub (gh secret set)
- [ ] Criar workflows básicos
- [ ] Testar deploy para staging
- [ ] Configurar branch protection
```

## 🎓 Convenções de Código

### Naming Conventions

#### Arquivos e Diretórios
```
✅ snake_case:
- script_generator.py
- video_renderer.py
- test_api.py

❌ Evitar:
- ScriptGenerator.py
- videoRenderer.py
- testAPI.py
```

#### Classes
```python
✅ PascalCase:
class ScriptGeneratorService:
class VideoModel:
class BigQueryClient:

❌ Evitar:
class script_generator_service:
class videomodel:
```

#### Funções e Variáveis
```python
✅ snake_case:
async def generate_script():
user_id = "123"
video_duration = 60

❌ Evitar:
async def GenerateScript():
userId = "123"
VideoDuration = 60
```

#### Constantes
```python
✅ UPPER_SNAKE_CASE:
MAX_VIDEO_DURATION = 600
DEFAULT_LOCATION = "us-central1"
API_VERSION = "v1"
```

### Estrutura de Commits

#### Conventional Commits
```bash
# Features
feat: adicionar endpoint de geração de vídeo
feat(api): implementar autenticação JWT

# Fixes
fix: corrigir erro na validação de duração
fix(bigquery): resolver timeout em queries longas

# Docs
docs: atualizar README com instruções de setup
docs(api): adicionar exemplos de uso

# Refactor
refactor: simplificar lógica de geração de script
refactor(storage): melhorar performance de upload

# Tests
test: adicionar testes para script generator
test(integration): testar fluxo completo de vídeo

# Chore
chore: atualizar dependências
chore(ci): configurar workflow de deploy
```

### Organização de Imports
```python
# 1. Standard library
import os
import sys
from typing import Optional, List

# 2. Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery

# 3. Local
from backend.core.config import settings
from backend.services.script_generator import ScriptGeneratorService
from backend.models.video import VideoModel
```

### Docstrings (Google Style)
```python
async def generate_video_script(
    topic: str,
    duration: int,
    style: str = "educational"
) -> dict:
    """Generate video script using AI.

    Long description providing more context about what this
    function does and how it should be used.

    Args:
        topic: Main topic for the video
        duration: Target duration in seconds (30-600)
        style: Script style (educational, entertaining, documentary)

    Returns:
        Dictionary containing:
            - script (str): Generated script text
            - title (str): Video title
            - key_points (List[str]): Main points covered

    Raises:
        ValueError: If duration is out of range
        ConnectionError: If AI service is unavailable

    Example:
        >>> result = await generate_video_script(
        ...     topic="Python async",
        ...     duration=180,
        ...     style="educational"
        ... )
        >>> print(result["title"])
        'Understanding Python Async/Await'
    """
    pass
```

## 🔧 Comandos gh CLI para Estrutura

### Criar Issues com Labels
```bash
# Feature
gh issue create \
  --title "Feature: Implementar geração de vídeo" \
  --body "Descrição detalhada..." \
  --label "type:feature,priority:high" \
  --assignee @me

# Bug
gh issue create \
  --title "Bug: Erro na validação" \
  --label "type:bug,priority:critical" \
  --web

# Documentation
gh issue create \
  --title "Docs: Atualizar API reference" \
  --label "type:docs" \
  --milestone "v1.0"
```

### Criar PRs por Módulo
```bash
# API routes
gh issue develop 1 --checkout --base main
# ... desenvolver ...
gh pr create --title "feat(api): adicionar rotas de vídeo" --fill

# Services
gh issue develop 2 --checkout --base main
gh pr create --title "feat(services): implementar script generator"

# Tests
gh pr create --title "test: adicionar cobertura para services" --draft
```

### Organizar com Projects
```bash
# Criar project
gh project create --title "Video Genius MVP" --owner @me

# Adicionar issues ao project
gh issue list --json number | jq '.[].number' | \
  xargs -I {} gh project item-add 1 --owner @me --url "issues/{}"
```

## 📊 Métricas de Qualidade

### Coverage Mínimo
```bash
# Configurado em pyproject.toml
[tool.coverage.report]
fail_under = 80  # Mínimo 80% coverage

# Rodar com coverage
pytest tests/ --cov=backend --cov-report=html --cov-fail-under=80
```

### Linting Score
```bash
# Ruff não deve ter erros
ruff check . && echo "✅ Linting OK"

# MyPy não deve ter erros de tipo
mypy backend/ && echo "✅ Type checking OK"

# Black verifica formatação
black --check backend/ && echo "✅ Formatting OK"
```

### Performance
```bash
# Testes devem ser rápidos
pytest tests/unit/ --durations=10  # Mostrar 10 mais lentos

# Testes lentos devem ser marcados
@pytest.mark.slow
def test_video_rendering():
    pass
```

## 🎯 Próximos Passos

### Fase 1: Setup (Você está aqui!)
- [x] Criar estrutura de diretórios
- [x] Configurar ambiente
- [x] Setup GitHub CLI + Copilot
- [ ] Criar arquivos base
- [ ] Primeiro commit

### Fase 2: Core Features
```bash
# Use Copilot para gerar:
gh copilot suggest -t gh "criar milestones para MVP"

# Criar issues
gh issue create --title "Implementar ScriptGeneratorService"
gh issue create --title "Criar endpoints de API"
gh issue create --title "Integrar BigQuery"
gh issue create --title "Setup Cloud Run"
```

### Fase 3: Testing & CI/CD
```bash
# Configurar workflows
gh workflow list
gh workflow enable test
gh workflow enable deploy-staging

# Adicionar secrets
gh secret set GOOGLE_PROJECT_ID --body "$PROJECT_ID"
```

### Fase 4: Deploy & Monitoring
```bash
# Deploy inicial
gcloud run deploy video-genius-api --source .

# Configurar monitoring
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

## 💡 Dicas Finais

### 1. Mantenha copilot-instructions.md Atualizado
```bash
# Sempre que adicionar nova feature, atualize:
vim .github/copilot-instructions.md

# Adicione:
# - Novos serviços
# - Novos padrões
# - Novos comandos gh CLI úteis
```

### 2. Use Tags de TODO
```python
# TODO: Implementar cache
# FIXME: Corrigir race condition
# HACK: Workaround temporário
# XXX: Revisar esta lógica
```

### 3. Documente Decisões
```bash
# Crie ADRs (Architecture Decision Records)
mkdir -p docs/adr
vim docs/adr/001-use-fastapi.md
```

### 4. Automatize Tudo
```bash
# Crie scripts para tarefas repetitivas
vim scripts/create-service.sh  # Criar novo serviço
vim scripts/add-endpoint.sh    # Adicionar endpoint
```

### 5. Use gh CLI para Tudo
```bash
# Ao invés de ir ao browser:
gh issue view 42          # Ver issue
gh pr view 10 --web      # Abrir PR no browser
gh browse                # Abrir repo
gh repo view --web       # Ver repo no browser
```

## 🎬 Comandos para Começar AGORA

```bash
# 1. Criar estrutura completa
mkdir -p backend/{api/routes,services,models,database,storage,core,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p scripts/gh-helpers docs
find backend tests -type d -exec touch {}/__init__.py \;

# 2. Criar primeiro issue
gh issue create --title "Setup: Criar aplicação FastAPI base" --web

# 3. Criar branch
gh issue develop 1 --checkout

# 4. Pedir ao Copilot para gerar código
# No backend/api/main.py, escreva:
# criar aplicação fastapi completa com health check e cors

# 5. Commit e PR
git add .
git commit -m "feat: adicionar aplicação FastAPI base"
gh pr create --fill --web

# 6. Continuar desenvolvendo!
gh work  # Ver próximas tasks
```

---

**🎯 Lembre-se**: O arquivo `.github/copilot-instructions.md` é o cérebro do Copilot. Quanto mais contexto você der lá, melhor ele vai gerar código!

**💡 Dica Pro**: Sempre que Copilot gerar algo bom, considere adicionar esse padrão no copilot-instructions.md para uso futuro.
