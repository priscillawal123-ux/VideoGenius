# 🚀 Quick Reference - Video Genius

Referência rápida para máxima produtividade no desenvolvimento.

## ⌨️ Atalhos de Teclado VS Code

| Atalho | Ação |
|--------|------|
| `Ctrl+Shift+G` | GitHub Copilot Suggest (shell) |
| `Ctrl+Shift+H` | Ver status GitHub |
| `Ctrl+Shift+P` → `Ctrl+R` | Criar PR rápido |
| `Ctrl+Shift+I` | Listar minhas issues |
| `Ctrl+Shift+B` | Abrir repo no navegador |
| `Ctrl+Shift+C` → `Ctrl+I` | Verificar status CI |
| `Ctrl+Shift+T` | Rodar todos os testes |
| `Ctrl+Shift+L` | Executar linting |
| `Ctrl+Shift+F` → `Ctrl+M` | Formatar código |
| `F5` | Iniciar debug |
| `Ctrl+F5` | Rodar Docker local |
| `Ctrl+Shift+D` → `Ctrl+B` | Build Docker |

## 🔧 GitHub CLI - Comandos Essenciais

### Autenticação
```bash
gh auth login                    # Login interativo
gh auth status                   # Verificar autenticação
gh auth refresh -s copilot       # Adicionar scope Copilot
```

### Issues
```bash
# Criar
gh issue create --title "Bug: descrição" --label bug --web
gh issue create --title "Feature: descrição" --label enhancement

# Listar
gh work                          # Alias: minhas issues
gh bugs                          # Alias: bugs abertos
gh issue list --state open --assignee @me

# Gerenciar
gh issue develop 42 --checkout   # Criar branch da issue
gh issue close 42                # Fechar issue
gh issue view 42 --web          # Abrir no navegador
```

### Pull Requests
```bash
# Criar
gh prc                          # Alias: PR rápido com --fill
gh pr create --fill --web       # Criar no navegador
gh pr create --draft            # Criar draft

# Gerenciar
gh co 42                        # Alias: checkout PR
gh pr view 42                   # Ver detalhes
gh pr diff 42                   # Ver mudanças
gh ci                           # Alias: verificar CI
gh pr checks --watch            # Assistir CI em tempo real

# Review
gh pr review 42 --approve       # Aprovar
gh pr review 42 --comment --body "LGTM!"
gh pr review 42 --request-changes --body "Adicione testes"

# Merge
gh pr merge --squash --delete-branch
gh pr merge --auto --squash     # Auto-merge quando aprovado
```

### Workflows & Actions
```bash
# Workflows
gh workflow list                # Listar workflows
gh workflow run deploy --ref main  # Executar workflow

# Runs
gh run list --limit 10          # Últimos runs
gh run watch                    # Assistir run atual
gh run view --log              # Ver logs
gh run rerun --failed          # Re-executar apenas falhas
```

### Secrets & Variables
```bash
# Secrets
gh secret set SECRET_NAME --body "value"
gh secret set SECRET_NAME < secret.txt
gh secret list

# Variables
gh variable set VAR_NAME --body "value"
gh variable list
```

### Copilot CLI
```bash
# Sugestões
gh copilot suggest                              # Modo interativo
gh copilot suggest -t shell "find large files"  # Shell
gh copilot suggest -t git "undo last commit"    # Git
gh copilot suggest -t gh "create release"       # GitHub CLI

# Explicações
gh copilot explain "docker run -d nginx"
gh copilot explain "kubectl get pods -A"
```

### Aliases Pré-configurados
```bash
gh work      # gh issue list --assignee @me
gh prc       # gh pr create --fill
gh co        # gh pr checkout
gh bugs      # gh issue list --label bug
gh ci        # gh pr checks
```

## 🐍 Python - Comandos de Desenvolvimento

### Ambiente Virtual
```bash
# Ativar
source .venv/bin/activate

# Desativar
deactivate

# Instalar deps
pip install -r requirements-dev.txt
```

### Testing
```bash
# Todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=backend --cov-report=html

# Teste específico
pytest tests/test_api.py::test_create_video -v

# Modo watch (instalar: pip install pytest-watch)
ptw tests/

# Apenas testes rápidos
pytest tests/ -m "not slow"
```

### Linting & Formatting
```bash
# Ruff (linting)
ruff check .                    # Verificar
ruff check --fix .              # Corrigir automaticamente
ruff check --watch .            # Modo watch

# Black (formatting)
black backend/ tests/           # Formatar
black --check backend/          # Verificar apenas

# MyPy (type checking)
mypy backend/                   # Verificar tipos

# isort (imports)
isort backend/ tests/           # Organizar imports

# Rodar tudo
ruff check --fix . && black backend/ tests/ && mypy backend/
```

### Pre-commit
```bash
# Instalar hooks
pre-commit install

# Rodar manualmente
pre-commit run --all-files

# Atualizar hooks
pre-commit autoupdate

# Pular hooks (emergência)
git commit --no-verify -m "..."
```

## 🐳 Docker - Comandos Úteis

### Build & Run
```bash
# Build development
docker build --target development -t video-genius:dev .

# Build production
docker build --target production -t video-genius:prod .

# Run development
docker run -p 8080:8080 --env-file .env.local video-genius:dev

# Run production
docker run -p 8080:8080 --env-file .env.local video-genius:prod

# Background
docker run -d -p 8080:8080 --name video-genius video-genius:dev
```

### Docker Compose
```bash
# Iniciar todos os serviços
docker-compose up

# Background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Rebuild
docker-compose up --build
```

### Manutenção
```bash
# Limpar containers parados
docker container prune -f

# Limpar imagens não usadas
docker image prune -a -f

# Limpar volumes
docker volume prune -f

# Limpar tudo
docker system prune -a --volumes -f
```

## ☁️ Google Cloud - Comandos Essenciais

### Configuração
```bash
# Login
gcloud auth login
gcloud auth application-default login

# Projeto
gcloud config set project PROJECT_ID
gcloud config get-value project

# Listar projetos
gcloud projects list
```

### Cloud Run
```bash
# Deploy
gcloud run deploy video-genius-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Listar services
gcloud run services list

# Ver logs
gcloud run logs tail video-genius-api --project=PROJECT_ID

# Deletar
gcloud run services delete video-genius-api
```

### BigQuery
```bash
# Executar query
bq query --use_legacy_sql=false 'SELECT * FROM dataset.table LIMIT 10'

# Listar datasets
bq ls

# Listar tabelas
bq ls dataset_name

# Criar tabela
bq mk --table dataset.table schema.json

# Carregar dados
bq load --source_format=CSV dataset.table data.csv
```

### Cloud Storage
```bash
# Criar bucket
gsutil mb gs://video-genius-assets

# Upload
gsutil cp local-file.mp4 gs://bucket-name/

# Download
gsutil cp gs://bucket-name/file.mp4 ./

# Listar
gsutil ls gs://bucket-name/

# Sincronizar diretório
gsutil -m rsync -r ./local-dir gs://bucket-name/remote-dir
```

### Vertex AI
```bash
# Listar modelos
gcloud ai models list --region=us-central1

# Ver quotas
gcloud compute project-info describe --project=PROJECT_ID
```

## 🔄 Workflows Comuns

### 1. Nova Feature (Fluxo Completo)
```bash
# 1. Criar issue
gh issue create --title "Feature: nova funcionalidade" --web

# 2. Criar branch da issue
gh issue develop 42 --checkout

# 3. Desenvolver e testar
pytest tests/ -v

# 4. Commit
git add .
git commit -m "feat: implementar nova funcionalidade"

# 5. Push e criar PR
git push -u origin feature/nova-funcionalidade
gh prc

# 6. Verificar CI
gh ci --watch

# 7. Após aprovação, merge
gh pr merge --squash --delete-branch
```

### 2. Hotfix Urgente
```bash
# 1. Branch do main
git checkout main && git pull
git checkout -b hotfix/bug-critico

# 2. Fix rápido
# ... fazer mudanças ...
git add . && git commit -m "fix: corrigir bug crítico"

# 3. PR urgente
gh pr create --title "HOTFIX: Bug crítico" --label "priority:critical"

# 4. Merge (após revisão mínima)
gh pr merge --admin --squash

# 5. Deploy imediato
gh workflow run deploy-production --ref main
gh run watch
```

### 3. Code Review
```bash
# 1. Checkout PR
gh co 42

# 2. Rodar testes localmente
pytest tests/ -v

# 3. Ver mudanças
gh pr diff 42

# 4. Verificar CI
gh ci

# 5. Revisar
gh pr review 42 --approve --body "LGTM!"
# ou
gh pr review 42 --request-changes --body "Adicione testes para X"
```

### 4. Atualizar Branch com Main
```bash
# 1. Atualizar main local
git checkout main && git pull origin main

# 2. Voltar para sua branch
git checkout feature/sua-branch

# 3. Rebase ou merge
git rebase main
# ou
git merge main

# 4. Resolver conflitos se houver
git add .
git rebase --continue  # se usando rebase
# ou
git commit  # se usando merge

# 5. Force push (apenas se fez rebase)
git push --force-with-lease
```

### 5. Setup Novo Desenvolvedor
```bash
# 1. Clone
gh repo clone seu-usuario/video-genius
cd video-genius

# 2. Setup automatizado
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Ativar ambiente
source .venv/bin/activate

# 4. Configurar credenciais
# Editar .env.local

# 5. Testar
uvicorn backend.api.main:app --reload

# 6. Primeiro commit
git checkout -b setup/add-developer
gh pr create --title "docs: adicionar desenvolvedor ao projeto"
```

## 🎯 Copilot - Como Usar Efetivamente

### No VS Code (Chat)
```
Bons prompts:
✅ "criar endpoint POST /videos que aceita título e duração"
✅ "adicionar validação de email no modelo User"
✅ "criar teste para a função generate_script"
✅ "refatorar esta função para usar async/await"

Prompts ruins:
❌ "me ajude"
❌ "como faço isso"
❌ "não funciona"
```

### No Terminal (gh copilot)
```bash
# Shell commands
gh copilot suggest -t shell "find all python files modified today"
gh copilot suggest -t shell "compress video file to 1080p"

# Git commands
gh copilot suggest -t git "undo last 3 commits keeping changes"
gh copilot suggest -t git "show files changed between two branches"

# GH CLI commands
gh copilot suggest -t gh "create release with auto-generated notes"
gh copilot suggest -t gh "merge all approved PRs"
```

### Dicas de Produtividade
1. **Comentários descritivos**: Escreva o que quer antes do código
2. **Contexto aberto**: Mantenha arquivos relacionados abertos em tabs
3. **Aceite rapidamente**: Tab para aceitar, Alt+] para próxima sugestão
4. **Use o chat**: Ctrl+I para perguntas inline
5. **Instruções claras**: `.github/copilot-instructions.md` guia o Copilot

## 🐛 Troubleshooting Rápido

### GitHub CLI não funciona
```bash
# Reinstalar
brew upgrade gh  # Mac
sudo apt update && sudo apt upgrade gh  # Linux

# Re-autenticar
gh auth logout
gh auth login
gh auth refresh -s copilot,workflow
```

### Copilot não sugere
```bash
# Verificar extensão
gh extension list | grep copilot

# Reinstalar
gh extension remove gh-copilot
gh extension install github/gh-copilot

# Verificar auth
gh auth status
```

### Docker build falha
```bash
# Limpar cache
docker builder prune -f

# Build sem cache
docker build --no-cache -t video-genius:dev .

# Verificar espaço em disco
docker system df
```

### Testes falhando
```bash
# Limpar cache
pytest --cache-clear

# Reinstalar deps
pip install -r requirements-dev.txt --force-reinstall

# Verificar ambiente
which python
python --version
```

### Pre-commit hooks lentos
```bash
# Rodar apenas em arquivos modificados (padrão)
pre-commit run

# Pular temporariamente (emergência)
git commit --no-verify

# Atualizar hooks
pre-commit autoupdate
```

## 📚 Links Úteis

### Documentação
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vertex AI Docs](https://cloud.google.com/vertex-ai/docs)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Copilot CLI](https://githubnext.com/projects/copilot-cli)

### Ferramentas
- [Ruff](https://docs.astral.sh/ruff/)
- [Pytest](https://docs.pytest.org/)
- [Docker](https://docs.docker.com/)
- [Pre-commit](https://pre-commit.com/)

### Comunidade
- [FastAPI Discord](https://discord.gg/fastapi)
- [Google Cloud Community](https://www.googlecloudcommunity.com/)
- [GitHub Community](https://github.community/)

## 💡 Dicas de Produtividade

### 1. Use Aliases
```bash
# Adicione ao .bashrc ou .zshrc
alias ghs='gh copilot suggest -t shell'
alias ghg='gh copilot suggest -t git'
alias ghh='gh copilot suggest -t gh'
alias ghe='gh copilot explain'

# Agora use:
ghs "find large files"
ghg "undo commits"
```

### 2. Terminal Multiplexer
```bash
# Instalar tmux
brew install tmux  # Mac
sudo apt install tmux  # Linux

# Usar
tmux new -s dev
# Ctrl+B, D para detach
# tmux attach -t dev para reattach
```

### 3. Watch Commands
```bash
# Assistir CI
watch -n 5 'gh pr checks'

# Assistir logs
watch -n 2 'docker logs video-genius --tail 50'

# Assistir testes
ptw tests/  # pytest-watch
```

### 4. Fish Shell (Autocomplete Poderoso)
```bash
# Instalar Fish
brew install fish  # Mac
sudo apt install fish  # Linux

# Configurar gh completion
gh completion -s fish | source
```

### 5. VS Code Snippets Customizados
Crie `.vscode/snippets.json` com seus snippets mais usados.

## 🎓 Próximos Passos

1. ✅ Setup completo (você já fez!)
2. 📖 Ler a documentação das APIs do Google Cloud
3. 🧪 Criar primeiro endpoint e teste
4. 🔄 Fazer primeiro PR usando gh CLI
5. 🚀 Deploy para Cloud Run
6. 📊 Configurar monitoramento
7. 🎯 Implementar features do projeto

---

**💡 Tip**: Mantenha este arquivo aberto em uma tab separada enquanto desenvolve!