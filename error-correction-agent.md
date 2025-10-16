# 🔧 Error Correction Agent - VideoGenius SaaS

## 📋 Configuração do Agente

### Agent Definition File: `error-correction-agent.agent.toml`

```toml
[agent]
name = "error-correction-agent"
description = "Agente especializado em identificar, diagnosticar e corrigir erros no projeto VideoGenius SaaS"
version = "1.0.0"
author = "VideoGenius Team"
category = "quality-assurance"

[agent.capabilities]
primary_function = "error_detection_and_correction"
supported_languages = ["python", "javascript", "typescript", "yaml", "dockerfile", "terraform"]
supported_platforms = ["gcp", "cloud-run", "bigquery", "vertex-ai"]
error_types = ["syntax", "logic", "configuration", "deployment", "security", "performance"]

[agent.integration]
parent_orchestrator = "orchestrator"
dependencies = ["validation-agent", "bootstrap-agent", "deploy-agent"]
output_formats = ["json", "markdown", "yaml"]
notification_channels = ["console", "bigquery", "cloud-logging"]

[agent.settings]
auto_fix_enabled = true
severity_levels = ["critical", "high", "medium", "low", "info"]
scan_depth = "comprehensive"
timeout_minutes = 15
max_concurrent_fixes = 5

[agent.prompts]
system_prompt = """
Você é o Error Correction Agent do VideoGenius SaaS, especializado em:

1. IDENTIFICAÇÃO PROATIVA de erros e problemas potenciais
2. DIAGNÓSTICO PRECISO da causa raiz dos problemas
3. CORREÇÃO AUTOMÁTICA quando possível
4. RECOMENDAÇÕES DETALHADAS para correção manual
5. PREVENÇÃO de regressões futuras

Sua expertise abrange:
- Arquitetura de microserviços Python/FastAPI
- Frontend React + Tailwind CSS
- Infraestrutura GCP (Cloud Run, BigQuery, GCS)
- Pipelines CI/CD e DevOps
- Segurança e compliance
- Performance e otimização de custos
"""

analysis_prompt = """
ANÁLISE SISTEMÁTICA DE ERROS:

1. **Scan Inicial**:
   - Verificar sintaxe em todos os arquivos
   - Validar configurações GCP
   - Checar dependências e versões
   - Analisar logs de erro recentes

2. **Diagnóstico Avançado**:
   - Correlacionar erros entre componentes
   - Identificar padrões de falha
   - Mapear impacto nos serviços
   - Classificar severidade dos problemas

3. **Proposta de Correção**:
   - Soluções automáticas implementáveis
   - Passos manuais detalhados
   - Scripts de correção ersonalizados
   - Medidas preventivas

4. **Validação Pós-Correção**:
   - Smoke tests automáticos
   - Verificação de regressões
   - Monitoramento contínuo
   - Relatório de qualidade
"""
```

## 🎯 Prompts Especializados para Gemini Code Assist

### 1. Comando Principal - Análise Completa

```
@error-correction-agent Executar análise completa de erros VideoGenius

Realizar auditoria completa do projeto VideoGenius SaaS:

**FASE 1: SCAN AUTOMÁTICO**
- Verificar todos os arquivos Python/JS/React para erros de sintaxe
- Validar configurações GCP (Cloud Run, BigQuery, GCS)
- Checar dependências desatualizadas ou conflitantes
- Analisar logs dos últimos 7 dias para padrões de erro

**FASE 2: DIAGNÓSTICO AVANÇADO**
- Correlacionar erros entre microserviços
- Identificar gargalos de performance
- Mapear vulnerabilidades de segurança
- Analisar otimizações de custo perdidas

**FASE 3: CORREÇÕES AUTOMÁTICAS**
- Aplicar fixes automáticos para erros simples
- Gerar scripts de correção customizados
- Propor refatorações de código problemático
- Implementar melhorias de configuração

**FASE 4: RELATÓRIO EXECUTIVO**
- Dashboard de saúde do projeto
- Roadmap de correções prioritárias
- Estimativas de impacto e esforço
- Métricas de qualidade before/after

Priorizar: Critical > High > Medium > Low
Focar em: Estabilidade, Performance, Segurança, Custos
```

### 2. Análise Rápida de Problemas Críticos

```
@error-correction-agent Scan rápido problemas críticos apenas

ANÁLISE EXPRESS (5-10 minutos):

**CRITICAL ISSUES ONLY:**
- Serviços Cloud Run com falhas
- Erros de autenticação/autorização
- Problemas de conectividade BigQuery/GCS
- Memory leaks ou CPU spikes
- Vulnerabilidades de segurança críticas
- Budget overruns ou quota exceeded

**AUTO-FIX HABILITADO:**
- Restart serviços com problemas
- Corrigir configurações básicas
- Aplicar patches de segurança urgentes
- Otimizar queries BigQuery custosas

**OUTPUT:**
- Lista priorizada de issues críticos
- Status de correções aplicadas
- Próximos passos recomendados
- Alertas de monitoramento sugeridos
```

### 3. Correção Específica por Componente

#### Backend (Python/FastAPI)
```
@error-correction-agent Analisar e corrigir backend Python

FOCO BACKEND MICROSERVICES:

**ANÁLISE ESPECÍFICA:**
- Validar schemas Pydantic
- Checar endpoints FastAPI e rotas
- Verificar conexões async/await
- Analisar performance database queries
- Validar error handling e logging

**CORREÇÕES AUTOMÁTICAS:**
- Otimizar imports e dependencies
- Corrigir type hints inconsistentes
- Implementar retry logic faltante
- Adicionar validações de entrada
- Melhorar exception handling

**TESTES E VALIDAÇÃO:**
- Executar pytest suite completa
- Validar OpenAPI specs geradas
- Testar health checks endpoints
- Verificar métricas Prometheus
```

#### Frontend (React)
```
@error-correction-agent Analisar e corrigir frontend React

FOCO FRONTEND APLICAÇÃO:

**ANÁLISE ESPECÍFICA:**
- ESLint errors e warnings
- Componentes React deprecados
- Bundle size optimization
- Accessibility violations
- Tailwind CSS classes não utilizadas

**CORREÇÕES AUTOMÁTICAS:**
- Aplicar Prettier formatting
- Remover imports não utilizados
- Otimizar re-renders desnecessários
- Implementar lazy loading faltante
- Corrigir keys em listas

**PERFORMANCE:**
- Analisar Core Web Vitals
- Otimizar imagens e assets
- Implementar code splitting
- Corrigir memory leaks JavaScript
```

#### Infraestrutura (GCP)
```
@error-correction-agent Analisar e corrigir infraestrutura GCP

FOCO INFRAESTRUTURA CLOUD:

**ANÁLISE ESPECÍFICA:**
- Cloud Run services health
- BigQuery quotas e performance
- GCS buckets permissions e lifecycle
- Service Account permissions mínimas
- Vertex AI API limits e custos

**CORREÇÕES AUTOMÁTICAS:**
- Otimizar Cloud Run configurations
- Implementar circuit breakers
- Corrigir IAM roles excessivas
- Aplicar lifecycle policies GCS
- Configurar alertas missing

**OBSERVABILIDADE:**
- Verificar logs estruturados
- Validar métricas customizadas
- Testar alertas e notifications
- Corrigir distributed tracing gaps
```

### 4. Correção Orientada por Logs

```
@error-correction-agent Analisar logs e corrigir erros identificados

ANÁLISE BASEADA EM LOGS:

**FONTE DE DADOS:**
- Cloud Logging últimas 24h
- Application logs dos microserviços
- BigQuery job failures
- Cloud Run error rates
- Vertex AI API errors

**PATTERN ANALYSIS:**
- Identificar erros mais frequentes
- Mapear correlações temporais
- Detectar cascading failures
- Analisar error rate trends

**AUTOMATED REMEDIATION:**
- Implementar retry automático
- Ajustar timeouts baseado em dados
- Corrigir error handling gaps
- Otimizar resource allocation

**PREVENTION MEASURES:**
- Adicionar circuit breakers
- Implementar graceful degradation
- Configurar alerts proativos
- Criar runbooks automáticos
```

### 5. Validação Pós-Correção

```
@error-correction-agent Validar correções aplicadas

VALIDAÇÃO COMPLETA PÓS-CORREÇÃO:

**SMOKE TESTS:**
- Testar todos os endpoints principais
- Verificar pipeline E2E funcionando
- Validar integrações GCP ativas
- Confirmar entrega Drive/Gmail

**REGRESSION TESTS:**
- Executar suite de testes completa
- Verificar performance benchmarks
- Testar cenários edge cases
- Validar backwards compatibility

**QUALITY GATES:**
- Code coverage > 80%
- Security scan 100% clean
- Performance tests passing
- Documentation updated

**RELATÓRIO FINAL:**
- Lista de correções aplicadas
- Métricas before vs after
- Riscos mitigados
- Recomendações para monitoramento
```

## 🛠️ Scripts de Suporte

### Script de Inicialização do Agente

```bash
#!/bin/bash
# initialize-error-correction-agent.sh

echo "🔧 Inicializando Error Correction Agent..."

# Criar estrutura de diretórios
mkdir -p ~/.codex/agents/error-correction
mkdir -p ~/VideoGenius/logs/error-correction
mkdir -p ~/VideoGenius/fixes/automated
mkdir -p ~/VideoGenius/fixes/manual

# Criar arquivo de configuração do agente
cat > ~/.codex/agents/error-correction-agent.agent.toml << 'EOF'
[agent]
name = "error-correction-agent"
description = "Agente especializado em correção de erros VideoGenius SaaS"
version = "1.0.0"
enabled = true
priority = "high"

[agent.capabilities]
auto_fix = true
deep_analysis = true
cross_component = true
preventive_measures = true

[agent.settings]
scan_frequency = "on-demand"
auto_fix_level = "safe"
notification_threshold = "medium"
max_execution_time = 900  # 15 minutes
EOF

echo "✅ Error Correction Agent configurado com sucesso!"
echo "📍 Localização: ~/.codex/agents/error-correction-agent.agent.toml"
echo ""
echo "🚀 Comandos disponíveis:"
echo "  @error-correction-agent Executar análise completa de erros VideoGenius"
echo "  @error-correction-agent Scan rápido problemas críticos apenas"
echo "  @error-correction-agent Analisar e corrigir backend Python"
echo "  @error-correction-agent Analisar e corrigir frontend React"
echo "  @error-correction-agent Analisar e corrigir infraestrutura GCP"
echo ""
```

### Script de Monitoramento Contínuo

```python
#!/usr/bin/env python3
# continuous-monitor.py

"""
Monitor contínuo de erros do VideoGenius SaaS
Executa verificações automáticas em intervalos regulares
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import json

class VideoGeniusErrorMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_patterns = {
            "critical": [
                "INTERNAL_SERVER_ERROR",
                "QUOTA_EXCEEDED",
                "BILLING_NOT_ENABLED",
                "PERMISSION_DENIED"
            ],
            "high": [
                "CONNECTION_TIMEOUT",
                "RESOURCE_EXHAUSTED",
                "INVALID_CREDENTIALS",
                "RATE_LIMIT_EXCEEDED"
            ]
        }
    
    async def scan_cloud_run_services(self) -> Dict:
        """Verificar saúde dos serviços Cloud Run"""
        # Implementação do scan
        pass
    
    async def analyze_bigquery_jobs(self) -> Dict:
        """Analisar jobs BigQuery com falhas"""
        # Implementação da análise
        pass
    
    async def check_vertex_ai_quotas(self) -> Dict:
        """Verificar quotas Vertex AI"""
        # Implementação da verificação
        pass
    
    async def generate_error_report(self) -> Dict:
        """Gerar relatório consolidado de erros"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cloud_run": await self.scan_cloud_run_services(),
            "bigquery": await self.analyze_bigquery_jobs(),
            "vertex_ai": await self.check_vertex_ai_quotas(),
            "recommendations": []
        }
        return report

if __name__ == "__main__":
    monitor = VideoGeniusErrorMonitor()
    asyncio.run(monitor.generate_error_report())
```

## 📊 Dashboard de Monitoramento

### Métricas Principais a Monitorar

```yaml
# monitoring-dashboard.yaml
error_metrics:
  critical_alerts:
    - service_down_count
    - error_rate_5xx
    - quota_exhaustion_alerts
    - security_violations
    
  performance_metrics:
    - response_time_p99
    - cpu_utilization
    - memory_usage
    - database_connection_pool
    
  business_metrics:
    - video_generation_success_rate
    - delivery_completion_rate
    - user_satisfaction_score
    - cost_per_execution

quality_gates:
  deployment_requirements:
    - error_rate_threshold: "< 1%"
    - performance_regression: "< 10%"
    - security_scan_passed: true
    - test_coverage: "> 80%"
```

## 🎯 Casos de Uso Comuns

### 1. Após Deploy com Falhas
```
@error-correction-agent Deploy falhou - investigar e corrigir automaticamente

CONTEXTO: Deploy da versão v2.1.3 falhou em prod
ERRO: Cloud Run service não conseguiu iniciar
TIMEOUT: 15 minutos para resolver

AÇÕES AUTOMÁTICAS:
1. Rollback para versão anterior estável
2. Analisar logs de startup failure
3. Identificar configuração problemática
4. Aplicar hotfix se possível
5. Agendar redeploy corrigido

NOTIFICAR: Slack #videogenius-ops com status
```

### 2. Performance Degradada
```
@error-correction-agent Performance degradou 40% - otimizar urgente

SINTOMAS DETECTADOS:
- Tempo resposta API aumentou de 200ms para 800ms
- BigQuery queries executando > 10 segundos
- Memory usage Cloud Run > 90%
- User complaints aumentaram 300%

INVESTIGAÇÃO AUTOMÁTICA:
1. Profiling aplicações Python
2. Análise explain plans BigQuery
3. Review recent code changes
4. Verificar external dependencies

OTIMIZAÇÕES AUTOMÁTICAS:
- Implementar query caching
- Otimizar serialization
- Aumentar resources Cloud Run
- Add database indexes missing
```

### 3. Custos Elevados Inesperados
```
@error-correction-agent Custos 500% acima do orçamento - otimizar

ALERTAS DE CUSTO:
- Vertex AI API calls: $120/dia (budget: $25/dia)
- BigQuery scan: 2TB/dia (expected: 200GB/dia)
- Cloud Run instances: 50 concurrent (expected: 10)

ANÁLISE DE ROOT CAUSE:
1. Identificar queries full-scan BigQuery
2. Detectar loops infinitos em APIs
3. Verificar retry logic excessivo
4. Analisar data pipeline efficiency

CORREÇÕES IMEDIATAS:
- Implementar query limits
- Add circuit breakers
- Otimizar data partitioning
- Configure auto-scaling limits
```

## ✅ Checklist de Validação do Agente

### Pré-Deployment
- [ ] Agent definition file criado e válido
- [ ] Integração com orchestrator configurada
- [ ] Permissions GCP adequadas configuradas
- [ ] Scripts de suporte testados
- [ ] Monitoring dashboard configurado

### Pós-Deployment
- [ ] Agente responde a comandos Gemini
- [ ] Análise automática funcionando
- [ ] Correções automáticas sendo aplicadas
- [ ] Relatórios sendo gerados corretamente
- [ ] Integração com outros agentes operacional

### Validação Contínua
- [ ] Error detection rate > 95%
- [ ] False positive rate < 5%
- [ ] Average time to resolution < 10 min
- [ ] Auto-fix success rate > 80%
- [ ] User satisfaction score > 4.5/5

---

## 🚀 Como Usar

### Instalação
```bash
# No Cloud Shell Editor, dentro do diretório VideoGenius
cd ~/VideoGenius
chmod +x scripts/initialize-error-correction-agent.sh
./scripts/initialize-error-correction-agent.sh
```

### Comandos Principais
```bash
# Análise completa (recomendado semanalmente)
@error-correction-agent Executar análise completa de erros VideoGenius

# Scan rápido (recomendado diariamente)
@error-correction-agent Scan rápido problemas críticos apenas

# Correção específica (quando necessário)
@error-correction-agent Analisar e corrigir [backend|frontend|infraestrutura]
```

### Automação
```bash
# Adicionar ao crontab para execução automática
0 */4 * * * /usr/local/bin/error-correction-agent --quick-scan
0 2 * * 1 /usr/local/bin/error-correction-agent --full-analysis
```

Este agente se integra perfeitamente ao seu sistema existente de agentes especializados, fornecendo uma camada robusta de quality assurance e correção automática para o VideoGenius SaaS! 🎯