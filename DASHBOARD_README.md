# Dashboard Roadmap - Video Genius

Painel interativo em tempo real para acompanhar o progresso do projeto Video Genius com sincronização bidirecional com GitHub Issues.

## 📋 Visão Geral

A Dashboard Roadmap oferece:

- **4 Fases do Projeto**: MVP, AI Integration, Production, Analytics
- **3 Modos de Visualização**: Timeline, Kanban, Burndown Chart
- **Real-time Updates**: Sincronização ao vivo via Supabase
- **GitHub Integration**: Sincronização bidirecional com GitHub Issues
- **Analytics**: Estatísticas de progresso, velocidade e ETA
- **Responsive Design**: Funciona em desktop e mobile

## 🚀 Instalação

### Pré-requisitos

- Node.js 18+ (Frontend)
- Python 3.11+ (Backend)
- Conta Supabase
- GitHub Token com acesso ao repositório

### 1. Frontend

```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.dashboard.example .env.local
# Editar .env.local com suas credenciais

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build
```

### 2. Backend

```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Configurar variáveis de ambiente
cp .env.dashboard.example .env
# Editar .env com suas credenciais

# Executar migrations
python -m alembic upgrade head

# Executar servidor
uvicorn backend.api.main:app --reload
```

### 3. Banco de Dados (Supabase)

```bash
# Conectar ao seu projeto Supabase via psql
psql -h your-project.supabase.co -U postgres -d postgres

# Executar migration
\i migrations/20241018_create_video_tasks.sql
```

## 📁 Estrutura de Arquivos

```
frontend/src/components/
├── DashboardRoadmap.tsx          # Componente principal
└── DashboardRoadmap.css          # Estilos

backend/
├── services/
│   └── github_sync_service.py    # Sincronização GitHub
├── api/
│   └── routes/
│       └── dashboard.py          # Rotas FastAPI

migrations/
└── 20241018_create_video_tasks.sql  # Schema do banco
```

## 🔧 Configuração

### Variáveis de Ambiente

#### Frontend (`VITE_*`)

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ENABLE_GITHUB_SYNC=true
VITE_ENABLE_REALTIME=true
```

#### Backend

```env
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=priscillawal123-ux
GITHUB_REPO=VideoGenius
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
GCP_PROJECT_ID=video-genius-prod-v1
```

### GitHub Token

1. Acesse https://github.com/settings/tokens
2. Gere novo token com permissões:
   - `repo` (full control)
   - `issues` (read/write)
3. Salve em `GITHUB_TOKEN`

### Supabase Setup

1. Crie novo projeto em https://supabase.com
2. Execute a migration SQL
3. Configure RLS policies (incluídas na migration)
4. Habilite Realtime para a tabela `video_tasks`

## 💻 Uso

### Iniciar o Projeto

```bash
# Terminal 1: Backend
cd backend
uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Monitorar sincronização
python -m backend.services.github_sync_service
```

### Sincronizar com GitHub

#### GitHub → Dashboard

```bash
curl -X POST http://localhost:8000/api/v1/dashboard/sync-github \
  -H "Content-Type: application/json" \
  -d '{"direction": "github_to_dashboard"}'
```

#### Dashboard → GitHub

```bash
curl -X POST http://localhost:8000/api/v1/dashboard/sync-github \
  -H "Content-Type: application/json" \
  -d '{"direction": "dashboard_to_github", "task_id": "a0000000-0000-0000-0000-000000000001"}'
```

### API Endpoints

#### Estatísticas

```bash
GET /api/v1/dashboard/stats
```

Resposta:
```json
{
  "total_tasks": 11,
  "completed_tasks": 5,
  "in_progress_tasks": 3,
  "blocked_tasks": 1,
  "completion_percentage": 45.45,
  "velocity": 0.5,
  "eta_days": 12,
  "last_updated": "2024-10-18T12:00:00"
}
```

#### Listar Fases

```bash
GET /api/v1/dashboard/phases
```

#### Listar Tarefas

```bash
GET /api/v1/dashboard/tasks?status=in-progress&priority=high&phase=phase-1
```

#### Criar Tarefa

```bash
POST /api/v1/dashboard/tasks
Content-Type: application/json

{
  "title": "Task Title",
  "description": "Task description",
  "status": "todo",
  "priority": "medium",
  "phase": "phase-1",
  "assignee": "username",
  "due_date": "2024-11-30T00:00:00Z"
}
```

#### Atualizar Tarefa

```bash
PATCH /api/v1/dashboard/tasks/{task_id}
Content-Type: application/json

{
  "status": "completed",
  "priority": "high"
}
```

#### Deletar Tarefa

```bash
DELETE /api/v1/dashboard/tasks/{task_id}
```

## 📊 Visualizações

### Timeline View

Mostra as 4 fases em ordem cronológica com:
- Barra de progresso por fase
- Número de tarefas
- Data de início/fim
- Status geral

### Kanban View

Colunas por status:
- **Todo**: Tarefas não iniciadas
- **In Progress**: Tarefas em desenvolvimento
- **Blocked**: Tarefas bloqueadas
- **Completed**: Tarefas completadas

### Burndown Chart

Gráfico SVG mostrando:
- Número de tarefas por dia
- Linha de tendência ideal
- Projeção de conclusão
- ETA calculado

## 📈 Estatísticas

Calculadas automaticamente e atualizadas em tempo real:

- **Completion %**: (Completed / Total) × 100
- **Velocity**: Tasks completed per day (7-day average)
- **ETA**: (Remaining Tasks / Velocity) em dias
- **Blocked %**: Tasks blocked vs total

## 🔄 Sincronização GitHub

### Mapeamento de Campos

| GitHub | Dashboard | Lógica |
|--------|-----------|--------|
| Labels | Priority | `priority:critical` → `critical` |
| State | Status | `closed` → `completed`, `open` → `todo` |
| Milestone | Phase | Milestone name → phase identifier |
| Assignee | Assignee | Conservado |

### Sincronização Automática

```python
# Em background via Celery/Scheduler
from backend.services import GitHubSyncService

sync = GitHubSyncService(
    github_token=os.getenv("GITHUB_TOKEN"),
    github_owner=os.getenv("GITHUB_OWNER"),
    github_repo=os.getenv("GITHUB_REPO"),
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)

result = await sync.sync_github_to_dashboard()
print(f"Synced: {result['created']} created, {result['updated']} updated")
```

## 🧪 Testes

### Frontend Tests

```bash
npm run test
npm run test:coverage
```

### Backend Tests

```bash
pytest tests/ --cov=backend
pytest tests/integration/test_dashboard.py -v
```

### E2E Tests

```bash
npm run test:e2e
```

## 📱 Responsive Design

Dashboard adapta-se para:

- **Desktop**: 1920x1080+ (4 colunas kanban)
- **Tablet**: 768x1024 (2 colunas kanban)
- **Mobile**: 375x667 (1 coluna kanban)

CSS media queries:
- `@media (max-width: 768px)` - Tablets
- `@media (max-width: 480px)` - Celulares

## 🔐 Segurança

### Autenticação

- JWT via Supabase
- Row Level Security (RLS) habilitado
- Políticas por role (authenticated_user)

### Políticas RLS

```sql
-- Usuários autenticados podem ler/criar/atualizar/deletar
CREATE POLICY "Allow authenticated users"
    ON video_tasks FOR ALL
    USING (auth.role() = 'authenticated_user');
```

## 🐛 Troubleshooting

### "Cannot find module '@/lib/supabase'"

Adicione ao `tsconfig.json`:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Realtime não funciona

1. Verifique se Realtime está habilitado no Supabase
2. Cheque o console do navegador para erros
3. Confirme que Row Level Security está configurado

### GitHub sync retorna erro

1. Verifique token GitHub em `.env`
2. Confirme permissões (repo, issues)
3. Verifique credenciais Supabase
4. Veja logs em `backend/logs/`

## 📚 Documentação

- [Supabase Docs](https://supabase.com/docs)
- [FastAPI Docs](http://localhost:8000/docs)
- [React Docs](https://react.dev)
- [GitHub API](https://docs.github.com/en/rest)

## 🚀 Deploying

### Frontend (Vercel)

```bash
npm run build
# Deploy build/ folder to Vercel
```

### Backend (Cloud Run)

```bash
./deploy.sh
```

### Database (Supabase)

Migrations são versionadas em `migrations/`

```bash
# Usar Supabase CLI
supabase db push
```

## 📞 Suporte

Para issues e dúvidas:
1. Abra issue no GitHub
2. Verifique logs em `backend/logs/`
3. Consulte documentação acima

## 📄 Licença

MIT License - Veja LICENSE file

## 👥 Contribuindo

1. Fork o repositório
2. Crie branch: `git checkout -b feature/feature-name`
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/feature-name`
5. Abra Pull Request

---

**Last Updated**: October 18, 2024
**Versão Dashboard**: 1.0.0
**Status**: MVP Complete ✅
