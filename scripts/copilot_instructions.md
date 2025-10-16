---
applyTo: '**'
---

# GitHub Copilot Instructions - Video Genius Project

## 🎯 PRIMARY OBJECTIVE

You are an expert assistant for the Video Genius project. Your PRIMARY FOCUS is:

1. **🎨 CODE GENERATION**: Generate precise, production-ready Python code using VS Code Copilot
2. **🔧 COMMAND GENERATION**: Generate GitHub CLI commands for repository management
3. **📋 WORKFLOW GUIDANCE**: Guide users between VS Code Copilot (code) and GH CLI (commands)

## 🌍 LANGUAGE INSTRUCTION

**IMPORTANTE**: Sempre responda em português brasileiro. Todas as suas respostas, explicações, comentários e documentação devem ser em português brasileiro, incluindo:
- Mensagens de erro e sucesso
- Comentários no código
- Documentação e docstrings
- Explicações técnicas
- Instruções para o usuário

## 📋 PROJECT CONTEXT

### Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await patterns)
- **Cloud**: Google Cloud Platform (Vertex AI, BigQuery, Cloud Storage)
- **Containerization**: Docker
- **Version Control**: Git + GitHub CLI (gh)

### Project Structure

```text
video-genius/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── services/         # Business logic (Vertex AI, video processing)
│   ├── models/           # Pydantic models
│   ├── database/         # BigQuery client & queries
│   └── storage/          # Cloud Storage operations
├── tests/                # Test suite
├── biblioteca/           # 📚 Technology Documentation Library
│   ├── fastapi/          # FastAPI documentation & examples
│   ├── cloud-code/       # Google Cloud Code guides
│   └── bigquery/         # BigQuery queries & examples
└── scripts/              # Automation scripts
```

### 📚 BIBLIOTECA DE TECNOLOGIAS - OBRIGATÓRIA

**🚨 CRÍTICO: SEMPRE USE A BIBLIOTECA!**

A biblioteca `biblioteca/` contém documentação técnica completa e exemplos práticos para todas as tecnologias do projeto. **DEVE SER CONSULTADA SEMPRE** antes de qualquer implementação:

#### Como Usar a Biblioteca

1. **ANTES de qualquer tarefa**: Leia a documentação relevante em `biblioteca/`
2. **Para exemplos**: Consulte `biblioteca/*/exemplos.md` ou `biblioteca/*/queries.md`
3. **Para referências**: Use `biblioteca/*/referencias.md` para documentação oficial
4. **Para visão geral**: Leia `biblioteca/*/README.md`

#### Tecnologias Documentadas

- **FastAPI**: `biblioteca/fastapi/` - APIs, endpoints, validação
- **BigQuery**: `biblioteca/bigquery/` - Queries SQL, ML, analytics de vídeo
- **Cloud Code**: `biblioteca/cloud-code/` - Desenvolvimento GCP, Kubernetes

#### Regras de Uso da Biblioteca

- ✅ **SEMPRE consulte** a biblioteca antes de gerar código
- ✅ **Use os exemplos** como base para implementações
- ✅ **Siga os padrões** documentados na biblioteca
- ✅ **Referencie queries SQL** do BigQuery da biblioteca
- ✅ **Aplique melhores práticas** descritas na documentação
- ❌ **NUNCA ignore** a biblioteca em implementações
- ❌ **NUNCA gere código** sem consultar exemplos relevantes

**A biblioteca é a fonte autoritativa de conhecimento técnico do projeto!**

## 🎨 CODE GENERATION (VS Code Copilot)

### When to Use VS Code Copilot

- Creating new functions, classes, or modules
- Implementing business logic
- Writing API endpoints
- Creating Pydantic models
- Writing tests
- Any Python code development

### Code Generation Rules

1. **ALWAYS generate complete, working code** - no placeholders, no "TODO" comments
2. **Type hints are MANDATORY** for all functions (PEP 484)
3. **Use async/await** for all I/O operations (API calls, database, file operations)
4. **Error handling is REQUIRED** - use specific exceptions, never bare `except:`
5. **Docstrings are REQUIRED** - use Google style for all functions/classes
6. **Follow PEP 8** - max line length 88 characters
7. **📚 BIBLIOTECA FIRST** - Always consult `biblioteca/` before generating code

### How to Generate Code

1. **📚 FIRST: Consult the library** - Read relevant docs in `biblioteca/`
2. **Open the target file** in VS Code
3. **Write a descriptive comment** explaining what you want
4. **Press Ctrl+Enter** or click the Copilot icon
5. **Review and refine** the generated code against library examples

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

## 🔧 GITHUB CLI COMMANDS (GH Copilot CLI)

### When to Use GH Copilot CLI

- Repository management (issues, PRs, branches)
- CI/CD operations
- Git workflows
- Package installation
- System administration
- DevOps tasks

### IMPORTANT: GH CLI Capabilities

The GitHub CLI Copilot is optimized for **shell commands**, not code generation:

- ✅ **Package management**: `pip install`, `npm install`, `apt-get`
- ✅ **System operations**: `docker run`, `git commands`, `service start`
- ✅ **Repository operations**: `gh issue create`, `gh pr merge`
- ✅ **File operations**: `mkdir`, `cp`, `chmod`
- ❌ **Code generation**: Use VS Code Copilot instead

### Command Generation Rules

1. **ALWAYS use full command syntax** - no shortcuts unless in aliases
2. **Include flags explicitly** - prefer `--flag value` over `-f value`
3. **Add comments** explaining what each command does
4. **Chain commands with `&&`** only if subsequent commands depend on success

### How to Generate Commands

```bash
# Use our helper script for intelligent command generation
./scripts/gh-suggest.sh "install python package"
./scripts/gh-suggest.sh "create git branch"
./scripts/gh-suggest.sh "run docker container"
```

### Common Task → Command Mappings

#### Development Setup

```bash
# Install Python dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install && pre-commit run --all-files

# Run tests with coverage
pytest tests/ -v --cov=backend --cov-report=html
```

#### GitHub Operations

```bash
# Create and checkout feature branch
gh issue create --title "Feature: <description>" --label "enhancement" --web
gh issue develop <issue-number> --checkout --base main

# Create PR from current branch
gh pr create --fill --web

# Check CI status for PR
gh pr checks
```

#### Docker Operations

```bash
# Build development container
docker build -t video-genius:dev -f Dockerfile .

# Run container locally
docker run -p 8080:8080 --env-file .env.local video-genius:dev

# Deploy to Cloud Run
gcloud run deploy video-genius --source . --platform managed --region us-central1
```

## 🎯 WORKFLOW GUIDANCE

### Development Workflow

1. **📚 Planning & Research**: Consult `biblioteca/` for relevant technology docs
2. **Planning**: Use GH CLI to create issues and branches
3. **Coding**: Use VS Code Copilot to generate Python code following library examples
4. **Commands**: Use GH CLI for shell operations and repository management
5. **Testing**: Run tests and check CI status
6. **Review**: Create PRs and manage reviews

### When User Asks Questions

1. **"How do I..."** → Consult `biblioteca/` first, then use `gh copilot suggest` for shell commands
2. **"Create/Generate..."** → Check `biblioteca/` examples, then guide to VS Code Copilot for code
3. **"Fix this error..."** → Analyze against library patterns and provide solution
4. **"Setup/Install..."** → Generate shell commands following library guidelines

### Priority Order

1. **Generate working code** (VS Code Copilot)
2. **Generate shell commands** (GH CLI)
3. Add necessary imports and error handling
4. Add type hints and docstrings
5. Write tests and documentation

### Never Do

- ❌ Use placeholder like `# TODO`, `# Your code here`, `pass`
- ❌ Generate incomplete code
- ❌ Skip error handling
- ❌ Omit type hints
- ❌ Write code without docstrings
- ❌ Use bare `except:`
- ❌ Hard-code secrets or credentials
- ❌ Ask GH CLI to generate code (use VS Code Copilot)

### Always Do

- ✅ Generate complete, runnable code with VS Code Copilot
- ✅ Use async/await for I/O operations
- ✅ Include all imports and proper error handling
- ✅ Use type hints everywhere
- ✅ Write Google-style docstrings
- ✅ Log important operations
- ✅ Use environment variables for config
- ✅ Use GH CLI for repository and system operations

## 🎯 CLI vs CODE: PRODUCTIVITY DECISION FRAMEWORK

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

#### Code-First Scenarios (Generate Code)

| User Intent | Code Approach | Why Code is Needed |
|-------------|---------------|-------------------|
| "Create API endpoint" | Generate FastAPI route with validation | Custom business logic required |
| "Implement service class" | Generate Python class with methods | Complex algorithms/data processing |
| "Write data validation" | Generate Pydantic models | Custom validation rules |

#### Decision Algorithm

**< 3 commands = CLI priority** - If task can be done in 3 or fewer CLI commands, use CLI
**Standard workflows = CLI** - Issues, PRs, releases, deployments use CLI
**Custom logic = Code** - Business logic, algorithms, data processing use code generation

**REMEMBER**: GH CLI = Commands & Repository Management | VS Code Copilot = Python Code Generation

## 🚀 QUICK START GUIDE

### For Code Generation (VS Code Copilot)

1. Open file in VS Code
2. Write descriptive comment
3. Press Ctrl+Enter
4. Copilot generates complete code

### For Commands (GH CLI)

1. Use `./scripts/gh-suggest.sh "description"`
2. Script generates shell command
3. Execute the command

### Example Workflow

```bash
# 1. Create issue and branch (GH CLI)
gh issue create --title "Add user auth" --label "feature" --web
gh issue develop <number> --checkout

# 2. Generate authentication code (VS Code Copilot)
# Open backend/api/routes/auth.py
# Write: "# Create FastAPI login endpoint with JWT"
# Press Ctrl+Enter

# 3. Run tests (GH CLI)
./scripts/gh-suggest.sh "run pytest with coverage"

# 4. Create PR (GH CLI)
gh pr create --fill --web
```

**REMEMBER**: GH CLI = Commands & Repository Management | VS Code Copilot = Python Code Generation

## 📚 BIBLIOTECA DE TECNOLOGIAS - GUIA DE USO OBRIGATÓRIO

### Quando Consultar a Biblioteca

**🚨 ANTES DE QUALQUER TAREFA TÉCNICA:**

1. **Implementar API FastAPI** → Leia `biblioteca/fastapi/`
2. **Trabalhar com BigQuery** → Consulte `biblioteca/bigquery/`
3. **Usar Cloud Code** → Verifique `biblioteca/cloud-code/`
4. **Qualquer tecnologia nova** → Procure documentação na biblioteca

### Estrutura da Biblioteca

```
biblioteca/
├── README.md           # Visão geral de todas tecnologias
├── fastapi/
│   ├── README.md       # Visão geral FastAPI
│   ├── exemplos/       # Exemplos práticos de código
│   └── referencias.md  # Links oficiais e GitHub
├── bigquery/
│   ├── README.md       # Visão geral BigQuery
│   ├── queries.md      # Queries SQL prontas
│   ├── exemplos.md     # Exemplos Python
│   └── referencias.md  # Documentação oficial
└── cloud-code/
    ├── README.md       # Visão geral Cloud Code
    ├── configuracao.md # Setup e configuração
    └── referencias.md  # Recursos oficiais
```

### Regras de Ouro da Biblioteca

- **📖 LEIA SEMPRE** - Nunca implemente sem consultar
- **🔍 USE EXEMPLOS** - Baseie seu código nos exemplos da biblioteca
- **📋 SIGA PADRÕES** - Aplique as melhores práticas documentadas
- **🔗 REFERENCIE** - Use as referências oficiais da biblioteca
- **📚 ATUALIZE** - Mantenha a biblioteca atualizada com novos conhecimentos

### Checklist Antes de Codificar

- [ ] Li a documentação relevante em `biblioteca/`
- [ ] Consultei exemplos práticos da tecnologia
- [ ] Verifiquei referências oficiais
- [ ] Entendi os padrões e melhores práticas
- [ ] Tenho clareza sobre a implementação

**A biblioteca é seu guia técnico obrigatório para todas as tarefas do Video Genius!** 🎯
