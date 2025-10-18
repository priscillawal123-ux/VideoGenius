# 🚀 Frontend & Backend Integration - Phase 2

**Data:** 18 de outubro de 2025  
**Status:** 🔄 Em Progresso  
**Tempo Estimado:** 1 hora

---

## 📋 Checklist de Tarefas

### 1. Database Migration (Supabase)
- [ ] Executar SQL migration
- [ ] Verificar tabela `video_tasks` criada
- [ ] Inserir dados de amostra
- [ ] Ativar Realtime na tabela

### 2. Backend API Endpoints
- [ ] Registrar rotas em `backend/api/main.py`
- [ ] Implementar `GET /tasks`
- [ ] Implementar `POST /tasks`
- [ ] Implementar `PUT /tasks/{id}`
- [ ] Implementar `DELETE /tasks/{id}`
- [ ] Testar health check

### 3. Frontend Integration
- [ ] Integrar API client em DashboardRoadmap
- [ ] Chamar `api.getTasks()` ao carregar
- [ ] Conectar real-time Supabase
- [ ] Testar criação/atualização de tasks
- [ ] Validar sincronização em tempo real

### 4. GitHub Integration (Optional)
- [ ] Configurar GitHub token
- [ ] Testar sincronização de issues
- [ ] Validar labels e assignees

### 5. Testing
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] API endpoint: `curl http://localhost:8000/tasks`
- [ ] Frontend: `http://localhost:5173`
- [ ] Real-time sync test

---

## 🔧 Passo 1: SQL Migration (Supabase)

### Arquivo: `migrations/20241018_create_video_tasks.sql`

```sql
-- Criar tabela video_tasks
CREATE TABLE IF NOT EXISTS video_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  phase VARCHAR(50) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'todo',
  priority VARCHAR(20) NOT NULL DEFAULT 'medium',
  assignee VARCHAR(100),
  due_date TIMESTAMP,
  completed_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para performance
CREATE INDEX idx_tasks_phase ON video_tasks(phase);
CREATE INDEX idx_tasks_status ON video_tasks(status);
CREATE INDEX idx_tasks_priority ON video_tasks(priority);

-- Ativar Realtime
ALTER TABLE video_tasks ENABLE ROW LEVEL SECURITY;

-- Política de RLS (permitir leitura/escrita)
CREATE POLICY "Enable all operations" ON video_tasks
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Inserir dados de amostra
INSERT INTO video_tasks (title, phase, status, priority, assignee) VALUES
('Setup Supabase & Database', 'phase-1', 'completed', 'critical', 'team'),
('Create API Endpoints', 'phase-1', 'completed', 'critical', 'backend'),
('Build Dashboard UI', 'phase-1', 'completed', 'high', 'frontend'),
('Integrate Real-time Updates', 'phase-1', 'in-progress', 'high', 'frontend'),
('GitHub Sync Integration', 'phase-1', 'in-progress', 'medium', 'backend'),
('Cloud Run Deployment', 'phase-1', 'completed', 'critical', 'devops'),
('AI Model Integration', 'phase-2', 'planning', 'high', null),
('Video Processing Pipeline', 'phase-2', 'planning', 'high', null),
('Analytics Dashboard', 'phase-3', 'planning', 'medium', null),
('Performance Optimization', 'phase-3', 'planning', 'low', null),
('Production Monitoring', 'phase-4', 'planning', 'medium', null);
```

---

## 🔌 Passo 2: Backend API Routes

### Arquivo: `backend/api/main.py` (adicionar rotas)

```python
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Models
class TaskCreate(BaseModel):
    title: str
    phase: str
    status: str = "todo"
    priority: str = "medium"
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    phase: str
    status: str
    priority: str
    assignee: Optional[str]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]

# Router
router = APIRouter(prefix="/api/v1", tags=["tasks"])

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(phase: Optional[str] = None, status: Optional[str] = None):
    """Obter todas as tasks"""
    # Integrar com Supabase
    try:
        response = supabase.table("video_tasks").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Criar nova task"""
    try:
        response = supabase.table("video_tasks").insert(task.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate):
    """Atualizar task"""
    try:
        response = supabase.table("video_tasks").update(task.dict()).eq("id", task_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task não encontrada"
            )
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Deletar task"""
    try:
        supabase.table("video_tasks").delete().eq("id", task_id).execute()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

---

## 💻 Passo 3: Frontend Integration

### Atualizar `frontend/src/components/DashboardRoadmap.tsx`

**Adicionar ao início do arquivo:**

```typescript
import { apiRequest } from '@/lib/api'

// Fetch tasks from API instead of mock data
useEffect(() => {
  const loadTasks = async () => {
    try {
      const tasks = await apiRequest('/tasks')
      setTasks(tasks)
    } catch (error) {
      console.error('Erro ao carregar tasks:', error)
      // Fallback para dados de amostra
    }
  }
  
  loadTasks()
}, [])
```

---

## ✅ Passo 4: Local Testing

### Terminal 1: Backend
```bash
source .venv/bin/activate
uvicorn backend.api.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

### Terminal 3: Test
```bash
# Health check
curl http://localhost:8000/health

# Get tasks
curl http://localhost:8000/api/v1/tasks

# Test frontend
open http://localhost:5173
```

---

## 🚀 Próximas Etapas

1. ✅ **Executar SQL migration em Supabase**
2. ✅ **Registrar rotas de API**
3. ✅ **Integrar frontend com API**
4. ✅ **Testar real-time sync**
5. ⏳ **Configurar GitHub sync (opcional)**
6. ⏳ **Deploy em produção**

---

**Status:** 🔄 Pronto para começar!
