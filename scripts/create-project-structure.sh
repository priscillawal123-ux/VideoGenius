#!/bin/bash
# Script para criar estrutura completa do projeto Video Genius via GitHub CLI
# Execute: chmod +x create-project-structure.sh && ./create-project-structure.sh

set -e

echo "🚀 Criando estrutura do projeto Video Genius via GitHub CLI..."
echo ""

# Verificar se gh está instalado e autenticado
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI não encontrado. Instale com: brew install gh"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Não autenticado no GitHub. Execute: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI verificado"
echo ""

# 1. Criar milestone principal
echo "📋 Criando milestone principal..."
gh api repos/:owner/:repo/milestones -X POST \
  -f title="Estrutura Base do Projeto" \
  -f description="Implementar estrutura completa do backend e testes" \
  || echo "⚠️  Milestone pode já existir"

echo ""

# 2. Criar issues para estrutura de diretórios
echo "📁 Criando issue: Estrutura de diretórios..."
gh issue create \
  --title "feat: Criar estrutura de diretórios backend" \
  --body "## Descrição
Criar todos os diretórios necessários para o backend:
- backend/api/routes/
- backend/services/
- backend/models/
- backend/database/
- backend/storage/
- backend/core/
- backend/utils/

## Critérios de Aceitação
- [ ] Todos os diretórios criados
- [ ] Arquivos __init__.py em cada diretório
- [ ] Estrutura compatível com imports Python" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

# 3. Criar issues para componentes core
echo "⚙️  Criando issue: Sistema de configuração..."
gh issue create \
  --title "feat: Implementar sistema de configuração" \
  --body "## Descrição
Criar backend/core/config.py com:
- Configurações Pydantic Settings
- Variáveis de ambiente
- Configurações Google Cloud, API, CORS

## Dependências
- Estrutura de diretórios criada" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

echo "📝 Criando issue: Sistema de logging..."
gh issue create \
  --title "feat: Implementar sistema de logging" \
  --body "## Descrição
Criar backend/core/logging.py com:
- Logging estruturado
- Configuração automática
- Níveis apropriados para dev/prod

## Dependências
- Sistema de configuração implementado" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

# 4. Criar issues para API
echo "🌐 Criando issue: Aplicação FastAPI base..."
gh issue create \
  --title "feat: Criar aplicação FastAPI base" \
  --body "## Descrição
Implementar backend/api/main.py com:
- Inicialização FastAPI
- Middlewares (CORS, TrustedHost)
- Tratamento global de exceções
- Lifespan events

## Dependências
- Sistema de logging implementado" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

echo "🔗 Criando issue: Endpoints básicos..."
gh issue create \
  --title "feat: Implementar endpoints básicos" \
  --body "## Descrição
Criar endpoints em backend/api/routes/:
- GET /health - Health check
- GET / - Endpoint raiz
- Estrutura para futuros endpoints

## Dependências
- Aplicação FastAPI base criada" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

# 5. Criar issues para testes
echo "🧪 Criando issue: Estrutura de testes..."
gh issue create \
  --title "feat: Configurar estrutura de testes" \
  --body "## Descrição
Implementar estrutura de testes:
- tests/conftest.py com fixtures
- tests/unit/test_api.py
- Configuração pytest no pyproject.toml

## Critérios de Aceitação
- [ ] pytest configurado
- [ ] Fixtures compartilhadas
- [ ] Pelo menos 3 testes passando" \
  --label "type:feature,priority:high" \
  --milestone "Estrutura Base do Projeto"

# 6. Criar issues para models
echo "📋 Criando issue: Modelos Pydantic..."
gh issue create \
  --title "feat: Criar modelos Pydantic base" \
  --body "## Descrição
Implementar modelos em backend/models/:
- video.py - Modelos de vídeo
- user.py - Modelos de usuário
- job.py - Modelos de job/tarefa

## Dependências
- Estrutura de diretórios criada" \
  --label "type:feature,priority:medium" \
  --milestone "Estrutura Base do Projeto"

# 7. Criar issues para serviços
echo "🔧 Criando issue: Serviços base..."
gh issue create \
  --title "feat: Implementar serviços base" \
  --body "## Descrição
Criar serviços em backend/services/:
- script_generator.py - Geração de scripts com Vertex AI
- video_renderer.py - Renderização de vídeo
- asset_manager.py - Gerenciamento de assets

## Dependências
- Modelos Pydantic criados
- Sistema de configuração implementado" \
  --label "type:feature,priority:medium" \
  --milestone "Estrutura Base do Projeto"

echo ""
echo "✅ Todas as issues foram criadas com sucesso!"
echo ""
echo "📋 Para ver suas tarefas pendentes:"
echo "   gh work"
echo ""
echo "🎯 Para começar a trabalhar na primeira issue:"
echo "   gh issue develop 1 --checkout"
echo ""
echo "📊 Para ver o progresso do milestone:"
echo "   gh issue list --milestone 'Estrutura Base do Projeto'"
