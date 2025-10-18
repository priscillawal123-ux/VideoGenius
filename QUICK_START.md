# 🚀 QUICK START - VIDEO GENIUS DASHBOARD

**Status**: ✅ Pronto para usar - Apenas 3 etapas!

---

## ⚡ Etapa 1: Deploy no Cloud Run (5 minutos)

```bash
# Já está pronto, basta executar:
cd /home/walland/Downloads/Video-Genius
chmod +x simple-deploy.sh
./simple-deploy.sh

# Ou manualmente:
gcloud run deploy video-genius-api \
    --image gcr.io/video-genius-prod-v1/video-genius-api:latest \
    --region us-central1 \
    --project video-genius-prod-v1
```

**Resultado**: API rodando em `https://video-genius-api-*.run.app`

---

## ⚡ Etapa 2: Integração Frontend (10 minutos)

### 2.1 Adicionar componente em App.tsx

```typescript
// frontend/src/App.tsx
import { DashboardRoadmap } from './components/DashboardRoadmap'

// Em routes:
{
  path: '/dashboard',
  element: <DashboardRoadmap />
}
```

### 2.2 Adicionar link na navegação

```tsx
<NavLink to="/dashboard">📊 Dashboard</NavLink>
```

### 2.3 Instalar dependência Supabase (opcional, já está pronta)

```bash
npm install @supabase/supabase-js
```

---

## ⚡ Etapa 3: Configuração Banco de Dados (5 minutos)

### 3.1 Conectar Supabase

```bash
# Você precisa de uma conta em supabase.com
# Projeto: Criar novo projeto
# Credenciais: Copiar URL e API Key
```

### 3.2 Executar migration

```bash
# Opção 1: Via Supabase CLI
supabase db push

# Opção 2: Via psql
psql -h seu-projeto.supabase.co -U postgres -d postgres < migrations/20241018_create_video_tasks.sql
```

### 3.3 Configurar variáveis

```bash
# Criar .env.local em frontend/
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-anon-key
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Criar .env em backend/
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-service-key
GITHUB_TOKEN=seu-github-token
```

---

## ✅ PRONTO!

Agora você tem:

✅ Backend rodando no Cloud Run  
✅ Frontend integrado com dashboard  
✅ Database sincronizado com GitHub Issues  
✅ Analytics em tempo real  

---

## 🧪 TESTAR

```bash
# Health check
curl https://video-genius-api-*.run.app/health

# Dashboard stats
curl https://video-genius-api-*.run.app/api/v1/dashboard/stats

# Frontend
http://localhost:5173/dashboard
```

---

## 📱 VISUALIZAÇÕES

- **Timeline**: Ver fases por data
- **Kanban**: Cards por status
- **Burndown**: Gráfico de progresso
- **Stats**: Métricas principais

---

## 🎯 Tempo Total

```
Etapa 1 (Deploy):       5 min
Etapa 2 (Frontend):    10 min
Etapa 3 (Database):     5 min
---
TOTAL:                 ~20 min
```

---

## 🔗 Recursos

- Documentação completa: `DASHBOARD_README.md`
- Detalhes técnicos: `DASHBOARD_IMPLEMENTATION_SUMMARY.md`
- Integração passo-a-passo: `DASHBOARD_INTEGRATION_CHECKLIST.md`
- Status final: `FINAL_STATUS_REPORT.md`

---

**Tudo pronto! Você consegue! 🚀**
