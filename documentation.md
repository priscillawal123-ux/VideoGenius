# Documentação de Variáveis de Ambiente - VideoGenius

Este documento detalha todas as variáveis de configuração utilizadas pelo sistema VideoGenius SaaS, conforme definidas no arquivo `env.toml`. Essas variáveis controlam o comportamento dos agentes, as integrações com o Google Cloud e os limites operacionais.
Este documento detalha todas as variáveis de configuração utilizadas pelo sistema VideoGenius, conforme definidas no arquivo `env.toml`. Essas variáveis controlam o comportamento dos agentes, as integrações com o Google Cloud e os limites operacionais.

---

## 1. Configurações do Google Cloud Platform (GCP)

Variáveis relacionadas à configuração do projeto e serviços no GCP.

```toml
[gcp]
```

| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `PROJECT_ID` | `crypto-groove-471219-v1` | ID do projeto no Google Cloud onde o SaaS será implantado. |
| `REGION` | `us-central1` | Região padrão para a criação de todos os recursos na GCP. |
| `GCS_BUCKET` | `repositorio_midia1` | Nome do bucket principal no Cloud Storage para armazenamento de mídias e artefatos. |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Modelo específico do Gemini a ser utilizado para geração de conteúdo e blueprints. |

---

## 2. Configurações da Aplicação VideoGenius

Parâmetros específicos do funcionamento do SaaS VideoGenius.

```toml
[videogenius]
```

| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `ORCHESTRATOR_URL` | `""` | URL do serviço do orquestrador. É preenchida dinamicamente após o deploy. |
| `PACKAGE_PREFIX` | `VideoGenius` | Prefixo utilizado para nomear pacotes, serviços e outros recursos gerados. |
| `DELIVERY_MODE` | `drive` | Modo de entrega dos vídeos gerados (ex: `drive`, `gmail`, `gcs`). |
| `SIGNED_URL_TTL_HOURS` | `24` | Tempo de vida (em horas) para as URLs assinadas do GCS. |
| `GENERATE_SIGNED_URLS` | `1` | Flag para habilitar (1) ou desabilitar (0) a geração de URLs assinadas. |

---

## 3. Caminhos de Diretórios (Paths)

Define os caminhos para os diretórios de trabalho do projeto.

```toml
[paths]
```

| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `WORKERS_DIR` | `${VIDEO_GENIUS_ROOT}/workers` | Diretório para os códigos-fonte dos microserviços (workers). |
| `SCRIPTS_DIR` | `${VIDEO_GENIUS_ROOT}/scripts` | Diretório para os scripts de automação e utilitários. |
| `OPS_DIR` | `${VIDEO_GENIUS_ROOT}/ops` | Diretório para arquivos operacionais, como relatórios e logs de deploy. |
| `LOGS_DIR` | `${VIDEO_GENIUS_ROOT}/logs` | Diretório para armazenar os logs de execução dos agentes. |

---

## 4. Endpoints de APIs

URLs base para as APIs de serviços externos utilizados.

```toml
[endpoints]
```

| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `GEMINI_ENDPOINT` | `https://us-central1-aiplatform.googleapis.com` | Endpoint da API do Vertex AI para acessar os modelos Gemini. |
| `DRIVE_API_URL` | `https://www.googleapis.com/drive/v3` | URL base da API do Google Drive. |
| `GMAIL_API_URL` | `https://gmail.googleapis.com/gmail/v1` | URL base da API do Gmail. |

---

## 5. Limites e Guardrails (Thresholds)

Valores de segurança para controle de custos e performance.

```toml
[thresholds]
```

| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `MAX_COST_PER_RUN` | `0.30` | Custo máximo estimado (em USD) para uma única execução do pipeline. |
| `MAX_DAILY_COST` | `12.00` | Limite de custo diário para o projeto. |
| `MAX_MONTHLY_COST` | `120.00` | Limite de custo mensal para o projeto. |
| `P95_LATENCY_SECONDS`| `360` | Limite de latência (em segundos) para o 95º percentil do tempo de execução. |

---

## 6. Configurações por Ambiente

Parâmetros que variam entre os ambientes de `dev` e `production`.

### Ambiente de Desenvolvimento (`dev`)
```toml
[environment.dev]
```
| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `DEBUG` | Nível de detalhe dos logs. |
| `MIN_INSTANCES` | `0` | Número mínimo de instâncias ativas no Cloud Run (permite escalar para zero). |
| `MAX_INSTANCES` | `5` | Número máximo de instâncias ativas no Cloud Run. |
| `MEMORY_LIMIT` | `512Mi` | Limite de memória para os serviços no Cloud Run. |

### Ambiente de Produção (`production`)
```toml
[environment.production]
```
| Variável | Valor Padrão | Descrição |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `INFO` | Nível de detalhe dos logs. |
| `MIN_INSTANCES` | `1` | Número mínimo de instâncias ativas no Cloud Run (garante alta disponibilidade). |
| `MAX_INSTANCES` | `20` | Número máximo de instâncias ativas no Cloud Run. |
| `MEMORY_LIMIT` | `1Gi` | Limite de memória para os serviços no Cloud Run. |