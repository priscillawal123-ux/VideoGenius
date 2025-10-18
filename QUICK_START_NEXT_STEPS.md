# 🚀 QUICK START - Próximas Ações

**Status**: Deploy em progresso (Docker Buildx build+push)  
**Arquivo Deploy Log**: `deploy.log`

---

## ⏳ Enquanto o Deploy Roda

O `deploy.sh` está executando em background:

```bash
# Você pode monitorar:
tail -f deploy.log

# Ou ver o status do buildx:
docker buildx du
```

Tempo estimado: 10-15 minutos para build+push+deploy completar

---

## ✅ Após Deploy Completar

### 1. Verificar Cloud Run Service (1 min)

```bash
# Obter URL do serviço
gcloud run services describe video-genius-api --region us-central1

# Testar health check
curl https://video-genius-api-XXXXX.run.app/health

# Ver logs
gcloud run services logs read video-genius-api --limit 50
```

### 2. Frontend Integration (15-20 min)

```bash
# Adicionar em App.tsx:
import { DashboardRoadmap } from './components/DashboardRoadmap'

// Em routes:
<Route path="/dashboard" element={<DashboardRoadmap />} />

# No terminal:
npm run dev
# Acessar: http://localhost:5173/dashboard
```

### 3. Backend Integration (10 min)

```bash
# Em backend/api/main.py:
from backend.api.routes import dashboard
app.include_router(dashboard.router)

# Copiar env:
cp .env.dashboard.example .env
# Editar com credenciais

# Testar:
uvicorn backend.api.main:app --reload
# Acessar: http://localhost:8000/api/v1/dashboard/stats
```

### 4. Database Setup (5-10 min)

```bash
# Conectar ao Supabase:
psql -h seu-projeto.supabase.co -U postgres -d postgres

# Executar migration:
\i migrations/20241018_create_video_tasks.sql

# Verificar:
SELECT * FROM video_tasks LIMIT 5;

# Habilitar Realtime no Supabase Dashboard:
# Settings → Replication → Enable Realtime para video_tasks
```

### 5. GitHub Setup (10 min)

```bash
# Gerar token em: https://github.com/settings/tokens
# Permissões: repo, read:org

# Adicionar em .env:
GITHUB_TOKEN=seu_token_aqui
GITHUB_OWNER=priscillawal123-ux
GITHUB_REPO=VideoGenius

# Testar sync:
curl -X POST http://localhost:8000/api/v1/dashboard/sync-github \
  -H "Content-Type: application/json" \
  -d '{"direction": "github_to_dashboard"}'
```

---

## 📋 Checklist Rápido

```
Deploy:
  □ Build completado
  □ Push para GCR sucesso
  □ Cloud Run service rodando
  □ Health check OK

Frontend:
  □ DashboardRoadmap importado
  □ Rota /dashboard criada
  □ Componente renderizando
  □ Estilos aplicados

Backend:
  □ Rotas registradas
  □ Endpoints respondendo
  □ GitHub sync funcionando
  □ Logging ok

Database:
  □ Migrations executadas
  □ Tabela criada
  □ Índices criados
  □ RLS habilitado
  □ Realtime habilitado

Testing:
  □ Unit tests passed
  □ Integration tests passed
  □ E2E tests passed
  □ Performance OK
```

---

## 🐛 Common Issues & Solutions

### "Docker: command not found"
```bash
# Docker buildx ainda está sendo instalado
# Espere ou reinstale:
mkdir -p ~/.docker/cli-plugins
curl -L https://github.com/docker/buildx/releases/download/v0.13.1/buildx-v0.13.1.linux-amd64 \
  -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx
```

### "Supabase connection refused"
```bash
# Verificar credenciais em .env:
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-key-aqui
```

### "GitHub sync returns 401"
```bash
# Verificar token:
GITHUB_TOKEN=seu_token_aqui

# Token precisa de permissões:
# - repo (full control)
# - read:org
```

### "Realtime not updating"
```bash
# Habilitar no Supabase Dashboard:
# Settings → Replication → video_tasks

# Verificar RLS está configurado:
SELECT * FROM pg_policies WHERE tablename = 'video_tasks';
```

---

## 📊 Tempo Total Restante

```
Deploy:              15-30 min  ⏳ Em progresso
Frontend:            15-20 min  ⏳ Próximo
Backend:             10 min     ⏳ Próximo
Database:            5-10 min   ⏳ Próximo
GitHub:              10 min     ⏳ Próximo
Testing:             30 min     ⏳ Próximo
─────────────────────────────
TOTAL:               85-120 min (~1.5-2 horas)
```

---

## 📚 Referências Rápidas

- [Dashboard README](./DASHBOARD_README.md)
- [Integration Checklist](./DASHBOARD_INTEGRATION_CHECKLIST.md)
- [Implementation Summary](./DASHBOARD_IMPLEMENTATION_SUMMARY.md)
- [Design System](./DASHBOARD_DESIGN_SYSTEM.md)

---

## 🎯 End Goal

Quando tudo completar:
- ✅ Dashboard live em produção
- ✅ Real-time updates funcionando
- ✅ GitHub sync automático
- ✅ API endpoints acessíveis
- ✅ Monitoring & alerting
- ✅ Documentação completa

---

**Você está apenas 2 horas de distância de tudo funcionando em produção! 🚀**

*Deploy em progresso → Integração → Testes → Live!*
