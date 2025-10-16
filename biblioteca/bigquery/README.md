# Google BigQuery

## Visão Geral

BigQuery é o data warehouse totalmente gerenciado, em escala de petabytes e com custo efetivo do Google Cloud que permite executar analytics sobre vastas quantidades de dados em near real time.

## Características Principais

### ⚡ Alta Performance
- Processamento em escala de petabytes
- SQL padrão (GoogleSQL)
- Otimização automática de queries
- Cache inteligente de resultados

### 🔄 Totalmente Gerenciado
- Sem infraestrutura para gerenciar
- Auto-scaling automático
- Alta disponibilidade garantida
- Backup e recovery automáticos

### 💰 Custo-Efetivo
- Preços baseados em uso
- Armazenamento separado de processamento
- Slots flexíveis ou sob demanda
- Custos previsíveis

### 🔒 Segurança Empresarial
- Encriptação em trânsito e repouso
- Controle de acesso granular (IAM)
- Auditoria completa
- Conformidade com regulamentações

## Arquitetura

### Componentes Principais
- **Datasets**: Containers para tabelas
- **Tabelas**: Dados estruturados
- **Views**: Queries salvas como tabelas virtuais
- **Jobs**: Execuções de queries, loads, exports

### Tipos de Tabelas
- **Nativas**: Dados gerenciados pelo BigQuery
- **Externas**: Dados em Cloud Storage, Drive, etc.
- **Particionadas**: Por tempo ou campo
- **Clusterizadas**: Para otimização de performance

## Linguagem SQL - GoogleSQL

### Funcionalidades Avançadas
- **Funções analíticas**: Window functions
- **Machine Learning**: BigQuery ML
- **Geospatial**: Funções geoespaciais
- **JSON**: Manipulação de dados JSON
- **Arrays e Structs**: Tipos complexos

### Exemplo Básico
```sql
SELECT
  video_id,
  title,
  duration_seconds,
  upload_date
FROM `project.dataset.videos`
WHERE upload_date >= '2024-01-01'
ORDER BY upload_date DESC
LIMIT 100;
```

## BigQuery ML

### Capacidades
- **Modelos supervisionados**: Regressão, classificação
- **Modelos não supervisionados**: Clustering
- **Time series**: Previsões temporais
- **Recomendação**: Sistemas de recomendação

### Exemplo
```sql
CREATE MODEL `project.dataset.video_recommendation`
OPTIONS (
  model_type='matrix_factorization',
  user_col='user_id',
  item_col='video_id',
  rating_col='rating'
) AS
SELECT user_id, video_id, rating
FROM `project.dataset.user_video_ratings`;
```

## Ingestão de Dados

### Métodos
- **Batch loading**: Arquivos CSV, JSON, Avro, Parquet
- **Streaming**: Inserção em tempo real via API
- **Transfer Service**: De outras fontes (Cloud Storage, etc.)
- **External tables**: Query direto de arquivos

### Formatos Suportados
- CSV, JSON, Avro, Parquet, ORC
- Compressed (gzip, snappy, etc.)
- Nested and repeated fields

## Segurança e Governança

### IAM (Identity and Access Management)
- **Primitive roles**: Owner, Editor, Viewer
- **Predefined roles**: BigQuery Admin, Data Editor, etc.
- **Custom roles**: Permissões específicas

### Data Governance
- **Tags e labels**: Organização de recursos
- **Policies**: Controle de acesso baseado em atributos
- **Audit logs**: Rastreamento de acesso

## Performance e Otimização

### Técnicas de Otimização
- **Partitioning**: Por data ou campo
- **Clustering**: Ordenação física dos dados
- **Materialized views**: Caches de queries frequentes
- **BI Engine**: Cache para dashboards

### Monitoramento
- **Query execution details**: Tempo, bytes processados
- **Slots utilizados**: Recursos de processamento
- **Storage usage**: Custos de armazenamento

## Integração com Ecossistema Google Cloud

### Serviços Integrados
- **Cloud Storage**: Armazenamento de arquivos
- **Dataflow**: Processamento de streams
- **Dataproc**: Big data processing
- **AI Platform**: Machine learning
- **Looker**: Business intelligence

### Ferramentas de Desenvolvimento
- **BigQuery CLI**: `bq` command
- **Client libraries**: Python, Java, Go, etc.
- **APIs REST**: Integração programática
- **JDBC/ODBC**: Conexão de ferramentas BI

## Uso no Video Genius

O Video Genius utiliza BigQuery para:

- **Analytics de vídeo**: Métricas de visualização, engajamento
- **Machine Learning**: Recomendações personalizadas
- **Data warehousing**: Histórico completo de vídeos
- **Real-time analytics**: Processamento de streams
- **Business intelligence**: Dashboards e relatórios

### Esquema Típico

```sql
-- Dataset: video_analytics
-- Tabela: video_metadata
CREATE TABLE `project.video_analytics.video_metadata` (
  video_id STRING,
  title STRING,
  description STRING,
  duration_seconds FLOAT64,
  resolution STRING,
  format STRING,
  upload_timestamp TIMESTAMP,
  user_id STRING,
  tags ARRAY<STRING>,
  metadata JSON
) PARTITION BY DATE(upload_timestamp)
CLUSTER BY user_id;

-- Tabela: video_views
CREATE TABLE `project.video_analytics.video_views` (
  video_id STRING,
  user_id STRING,
  view_timestamp TIMESTAMP,
  watch_duration_seconds FLOAT64,
  device_type STRING,
  location STRUCT<country STRING, region STRING>
) PARTITION BY DATE(view_timestamp)
CLUSTER BY video_id;
```

## Preços

### Armazenamento
- **Active storage**: $0.02/GB/mês
- **Long-term storage**: $0.01/GB/mês (90+ dias)
- **Streaming inserts**: $0.01/200MB

### Processamento
- **On-demand**: $5/TB processado
- **Flat-rate**: $2,000/mês por 500 slots
- **BI Engine**: $0.045/hora por reserva

## Melhores Práticas

### Design de Schema
- Use particionamento por data para tabelas temporais
- Clusterize por campos de filtro frequentes
- Use tipos apropriados para economizar espaço
- Normalize quando apropriado, denormalize para performance

### Otimização de Queries
- Use LIMIT em queries de desenvolvimento
- Filtre cedo na query (WHERE clauses)
- Use subqueries com moderação
- Monitore bytes processados

### Segurança
- Princípio do menor privilégio
- Use service accounts para aplicações
- Rotate credentials regularmente
- Audit logs de acesso

## Ferramentas e Integrações

### Interfaces
- **BigQuery Studio**: Editor SQL integrado
- **Cloud Console**: Interface web
- **CLI bq**: Linha de comando
- **Client libraries**: APIs programáticas

### BI Tools
- **Looker**: Business intelligence
- **Data Studio**: Dashboards gratuitos
- **Tableau**: Visualização avançada
- **Power BI**: Microsoft integration

## Monitoramento e Alertas

### Métricas Principais
- Query performance
- Storage usage
- Cost tracking
- Error rates

### Alertas
- Budget alerts
- Query failures
- Performance degradation
- Security events

## Links Úteis

- **Documentação**: https://cloud.google.com/bigquery/docs
- **SQL Reference**: https://cloud.google.com/bigquery/docs/reference/standard-sql/
- **BigQuery ML**: https://cloud.google.com/bigquery/docs/bqml-introduction
- **Preços**: https://cloud.google.com/bigquery/pricing
- **Tutoriais**: https://cloud.google.com/bigquery/docs/quickstarts

## Casos de Uso

- **Analytics em tempo real**: Streaming de eventos
- **Machine Learning**: Modelos em SQL
- **Data Lake**: Armazenamento de dados brutos
- **ETL/ELT**: Processamento de dados
- **Business Intelligence**: Dashboards e relatórios

---

*Documentação criada para o projeto Video Genius - Outubro 2025*