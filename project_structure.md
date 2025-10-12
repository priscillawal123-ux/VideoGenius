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

### 2. `pyproject.toml`

### 3. `.vscode/settings.json`

## 📝 Comandos para Criar Estrutura

### Criar Diretórios Base

### Criar Arquivos __init__.py

### Usar gh CLI para Setup

## 🎨 Templates de Arquivos

### backend/api/main.py

### backend/core/config.py

### tests/conftest.py

## 🚀 Uso com GitHub Copilot

### Como Pedir ao Copilot

#### ✅ BONS EXEMPLOS:

#### ❌ MAUS EXEMPLOS:

### Workflow com Copilot

1. **Abra arquivos relacionados** - Copilot usa contexto de tabs abertas
2. **Escreva comentário descritivo** - Seja específico
3. **Deixe Copilot sugerir** - Aceite com Tab
4. **Refine se necessário** - Use Copilot Chat (Ctrl+I)

## 📋 Checklist de Setup

### Inicial

### Desenvolvimento

### CI/CD

## 🎓 Convenções de Código

### Naming Conventions

#### Arquivos e Diretórios

#### Classes

#### Funções e Variáveis

#### Constantes

### Estrutura de Commits

#### Conventional Commits

### Organização de Imports

### Docstrings (Google Style)

## 🔧 Comandos gh CLI para Estrutura

### Criar Issues com Labels

### Criar PRs por Módulo

### Organizar com Projects

## 📊 Métricas de Qualidade

### Coverage Mínimo

### Linting Score

### Performance

## 🎯 Próximos Passos

### Fase 1: Setup (Você está aqui!)
- [x] Criar estrutura de diretórios
- [x] Configurar ambiente
- [x] Setup GitHub CLI + Copilot
- [ ] Criar arquivos base
- [ ] Primeiro commit

### Fase 2: Core Features

### Fase 3: Testing & CI/CD

### Fase 4: Deploy & Monitoring

## 💡 Dicas Finais

### 1. Mantenha copilot-instructions.md Atualizado

### 2. Use Tags de TODO

### 3. Documente Decisões

### 4. Automatize Tudo

### 5. Use gh CLI para Tudo

## 🎬 Comandos para Começar AGORA