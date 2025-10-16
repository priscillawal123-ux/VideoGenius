# Exemplos Práticos - BigQuery no Video Genius

## Configuração Inicial

### Criar Dataset

```bash
# Via gcloud CLI
gcloud bigquery datasets create video_analytics \
  --description="Dataset para analytics de vídeo do Video Genius" \
  --location=US

# Via Python Client
from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "video_genius.video_analytics"

dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"
dataset.description = "Dataset para analytics de vídeo"

dataset = client.create_dataset(dataset, timeout=30)
print(f"Dataset criado: {dataset.dataset_id}")
```

### Criar Tabelas com Schemas

```python
from google.cloud import bigquery

client = bigquery.Client()

# Schema para metadados de vídeo
video_metadata_schema = [
    bigquery.SchemaField("video_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("duration_seconds", "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("resolution", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("format", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("upload_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("tags", "STRING", mode="REPEATED"),
    bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
]

table_id = "video_genius.video_analytics.video_metadata"

table = bigquery.Table(table_id, schema=video_metadata_schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="upload_timestamp"
)
table.clustering_fields = ["user_id", "status"]

table = client.create_table(table)
print(f"Tabela criada: {table.table_id}")
```

## Ingestão de Dados

### Carregar Dados via CSV

```python
from google.cloud import bigquery

client = bigquery.Client()

# Configurar job de carregamento
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

table_id = "video_genius.video_analytics.video_metadata"
uri = "gs://video-genius-data/video_metadata_2024-01-01.csv"

load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config
)

load_job.result()  # Aguardar conclusão
print(f"Dados carregados em {table_id}")
```

### Streaming de Dados em Tempo Real

```python
from google.cloud import bigquery
import json

client = bigquery.Client()

# Dados de visualização para streaming
rows_to_insert = [
    {
        "video_id": "vid_12345",
        "user_id": "user_67890",
        "view_timestamp": "2024-01-15T10:30:00Z",
        "watch_duration_seconds": 245.5,
        "completion_rate": 0.85,
        "device_type": "mobile",
        "browser": "Chrome",
        "location": {"country": "BR", "region": "SP", "city": "São Paulo"},
        "referrer": "https://youtube.com"
    }
]

table_id = "video_genius.video_analytics.video_views"

errors = client.insert_rows_json(table_id, rows_to_insert)
if errors:
    print(f"Erros na inserção: {errors}")
else:
    print("Dados inseridos com sucesso")
```

### Ingestão via Pub/Sub

```python
from google.cloud import bigquery
from google.cloud import pubsub_v1
import json

# Subscriber para processar mensagens
def process_video_view(message):
    try:
        # Parse da mensagem
        data = json.loads(message.data.decode('utf-8'))

        # Inserir no BigQuery
        client = bigquery.Client()
        table_id = "video_genius.video_analytics.video_views"

        errors = client.insert_rows_json(table_id, [data])
        if not errors:
            message.ack()
            print(f"Visualização processada: {data['video_id']}")
        else:
            print(f"Erro ao inserir: {errors}")
            message.nack()

    except Exception as e:
        print(f"Erro no processamento: {e}")
        message.nack()

# Configurar subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('video-genius', 'video-views-sub')

future = subscriber.subscribe(subscription_path, process_video_view)
future.result()
```

## Consultas Analíticas

### Análise de Performance de Vídeo

```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
  vm.video_id,
  vm.title,
  COUNT(vv.video_id) as total_views,
  AVG(vv.watch_duration_seconds) as avg_watch_duration,
  AVG(vv.completion_rate) as avg_completion_rate,
  COUNT(DISTINCT vv.user_id) as unique_viewers
FROM `video_genius.video_analytics.video_metadata` vm
LEFT JOIN `video_genius.video_analytics.video_views` vv
  ON vm.video_id = vv.video_id
WHERE vm.upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY vm.video_id, vm.title
ORDER BY total_views DESC
LIMIT 10
"""

query_job = client.query(query)
results = query_job.result()

for row in results:
    print(f"{row.video_id}: {row.title} - {row.total_views} views")
```

### Dashboard de Métricas Diárias

```python
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
  DATE(view_timestamp) as date,
  COUNT(*) as total_views,
  COUNT(DISTINCT video_id) as videos_viewed,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(watch_duration_seconds) as avg_watch_duration,
  AVG(completion_rate) as avg_completion_rate
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY DATE(view_timestamp)
ORDER BY date DESC
"""

df = client.query(query).to_dataframe()
print(df.head())

# Salvar como CSV para dashboard
df.to_csv('daily_metrics.csv', index=False)
```

## Machine Learning com BigQuery ML

### Modelo de Previsão de Engajamento

```sql
-- Criar modelo de regressão linear
CREATE OR REPLACE MODEL `video_genius.video_analytics.engagement_prediction`
OPTIONS (
  model_type='linear_reg',
  input_label_cols=['completion_rate'],
  data_split_method='AUTO_SPLIT'
) AS
SELECT
  duration_seconds,
  ARRAY_LENGTH(tags) as num_tags,
  EXTRACT(HOUR FROM upload_timestamp) as upload_hour,
  CASE
    WHEN device_type = 'mobile' THEN 1
    WHEN device_type = 'desktop' THEN 2
    WHEN device_type = 'tablet' THEN 3
    ELSE 0
  END as device_category,
  completion_rate
FROM `video_genius.video_analytics.video_metadata` vm
JOIN `video_genius.video_analytics.video_views` vv ON vm.video_id = vv.video_id
WHERE vm.upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY);
```

### Usar Modelo para Previsões

```python
from google.cloud import bigquery

client = bigquery.Client()

# Query para fazer previsões
prediction_query = """
SELECT
  video_id,
  title,
  predicted_completion_rate
FROM ML.PREDICT(
  MODEL `video_genius.video_analytics.engagement_prediction`,
  (
    SELECT
      video_id,
      title,
      duration_seconds,
      ARRAY_LENGTH(tags) as num_tags,
      EXTRACT(HOUR FROM upload_timestamp) as upload_hour,
      1 as device_category  -- assumindo mobile
    FROM `video_genius.video_analytics.video_metadata`
    WHERE upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  )
)
ORDER BY predicted_completion_rate DESC
LIMIT 10
"""

results = client.query(prediction_query).result()
for row in results:
    print(f"{row.video_id}: {row.predicted_completion_rate:.2f}")
```

### Avaliação do Modelo

```sql
-- Avaliar performance do modelo
SELECT
  *
FROM ML.EVALUATE(
  MODEL `video_genius.video_analytics.engagement_prediction`,
  (
    SELECT
      duration_seconds,
      ARRAY_LENGTH(tags) as num_tags,
      EXTRACT(HOUR FROM upload_timestamp) as upload_hour,
      CASE
        WHEN device_type = 'mobile' THEN 1
        WHEN device_type = 'desktop' THEN 2
        WHEN device_type = 'tablet' THEN 3
        ELSE 0
      END as device_category,
      completion_rate
    FROM `video_genius.video_analytics.video_metadata` vm
    JOIN `video_genius.video_analytics.video_views` vv ON vm.video_id = vv.video_id
    WHERE vm.upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  )
);
```

## Integração com Data Studio

### Criar Data Source no Data Studio

```python
# Script para gerar relatório automático
from google.cloud import bigquery
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/datastudio']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'service-account-key.json', SCOPES)

service = build('datastudio', 'v1', credentials=credentials)

# Criar data source
data_source = {
    'name': 'Video Genius Analytics',
    'dataSourceType': 'BIGQUERY',
    'bigQueryDataSourceSpec': {
        'projectId': 'video-genius',
        'query': '''
        SELECT
          DATE(view_timestamp) as date,
          COUNT(*) as views,
          AVG(watch_duration_seconds) as avg_duration,
          AVG(completion_rate) as completion_rate
        FROM `video_genius.video_analytics.video_views`
        WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        GROUP BY DATE(view_timestamp)
        '''
    }
}

request = service.datasources().create(body=data_source)
response = request.execute()
print(f"Data source criado: {response['dataSourceId']}")
```

## Monitoramento e Alertas

### Monitor de Performance de Queries

```python
from google.cloud import bigquery
import time

client = bigquery.Client()

def monitor_query_performance():
    """Monitora queries custosas nos últimos 7 dias"""

    query = """
    SELECT
      job_id,
      query,
      total_bytes_processed,
      total_slot_ms,
      creation_time,
      ROUND(total_bytes_processed / 1024 / 1024 / 1024, 2) as gb_processed
    FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
    WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
      AND job_type = 'QUERY'
      AND state = 'DONE'
      AND total_bytes_processed > 100 * 1024 * 1024 * 1024  -- > 100GB
    ORDER BY total_bytes_processed DESC
    LIMIT 10
    """

    results = client.query(query).result()

    expensive_queries = []
    for row in results:
        expensive_queries.append({
            'job_id': row.job_id,
            'gb_processed': row.gb_processed,
            'query': row.query[:200] + '...' if len(row.query) > 200 else row.query
        })

    return expensive_queries

# Executar monitoramento
expensive = monitor_query_performance()
if expensive:
    print("Queries custosas encontradas:")
    for q in expensive:
        print(f"- {q['job_id']}: {q['gb_processed']} GB")
else:
    print("Nenhuma query custosa encontrada")
```

### Alertas de Qualidade de Dados

```python
from google.cloud import bigquery

client = bigquery.Client()

def check_data_quality():
    """Verifica qualidade dos dados de visualização"""

    quality_checks = {
        'null_video_ids': """
        SELECT COUNT(*) as null_count
        FROM `video_genius.video_analytics.video_views`
        WHERE video_id IS NULL
          AND view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        """,

        'negative_durations': """
        SELECT COUNT(*) as negative_count
        FROM `video_genius.video_analytics.video_views`
        WHERE watch_duration_seconds < 0
          AND view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        """,

        'invalid_completion_rates': """
        SELECT COUNT(*) as invalid_count
        FROM `video_genius.video_analytics.video_views`
        WHERE completion_rate < 0 OR completion_rate > 1
          AND view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        """
    }

    alerts = []
    for check_name, query in quality_checks.items():
        result = client.query(query).result()
        for row in result:
            count = row[0]
            if count > 0:
                alerts.append(f"{check_name}: {count} registros problemáticos")

    return alerts

# Executar verificações
alerts = check_data_quality()
if alerts:
    print("Alertas de qualidade de dados:")
    for alert in alerts:
        print(f"- {alert}")
else:
    print("Dados estão OK")
```

## Otimização de Performance

### Criar Índices com Clustering

```sql
-- Otimizar tabela com clustering
CREATE OR REPLACE TABLE `video_genius.video_analytics.video_views_optimized`
PARTITION BY DATE(view_timestamp)
CLUSTER BY video_id, user_id
AS
SELECT * FROM `video_genius.video_analytics.video_views`;
```

### Materialized Views para Consultas Frequentes

```sql
-- View materializada para métricas diárias
CREATE MATERIALIZED VIEW `video_genius.video_analytics.daily_metrics_mv`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 60
)
AS
SELECT
  DATE(view_timestamp) as date,
  COUNT(*) as total_views,
  COUNT(DISTINCT video_id) as unique_videos,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(watch_duration_seconds) as avg_watch_duration,
  AVG(completion_rate) as avg_completion_rate
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY DATE(view_timestamp);
```

### Cache de Resultados

```python
from google.cloud import bigquery

client = bigquery.Client()

# Configurar cache para query
job_config = bigquery.QueryJobConfig(
    use_query_cache=True,
    maximum_bytes_billed=100 * 1024 * 1024 * 1024  # 100GB
)

query = """
SELECT
  video_id,
  COUNT(*) as views,
  AVG(watch_duration_seconds) as avg_duration
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY video_id
ORDER BY views DESC
LIMIT 100
"""

query_job = client.query(query, job_config=job_config)
results = query_job.result()

print(f"Cache usado: {query_job.cache_hit}")
print(f"Bytes processados: {query_job.total_bytes_processed}")
```

---

*Exemplos práticos para implementação no projeto Video Genius*