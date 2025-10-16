# Queries BigQuery - Video Genius

## Estrutura de Dados

### Tabelas Principais

```sql
-- Dataset: video_analytics

-- Metadados dos vídeos
CREATE TABLE `video_genius.video_analytics.video_metadata` (
  video_id STRING,
  title STRING,
  description STRING,
  duration_seconds FLOAT64,
  resolution STRING,
  format STRING,
  upload_timestamp TIMESTAMP,
  user_id STRING,
  tags ARRAY<STRING>,
  metadata JSON,
  status STRING
) PARTITION BY DATE(upload_timestamp)
CLUSTER BY user_id, status;

-- Visualizações de vídeo
CREATE TABLE `video_genius.video_analytics.video_views` (
  video_id STRING,
  user_id STRING,
  view_timestamp TIMESTAMP,
  watch_duration_seconds FLOAT64,
  completion_rate FLOAT64,
  device_type STRING,
  browser STRING,
  location STRUCT<country STRING, region STRING, city STRING>,
  referrer STRING
) PARTITION BY DATE(view_timestamp)
CLUSTER BY video_id;

-- Processamento de vídeo
CREATE TABLE `video_genius.video_analytics.video_processing` (
  video_id STRING,
  operation STRING, -- 'compress', 'thumbnail', 'transcribe', 'subtitles'
  status STRING, -- 'pending', 'processing', 'completed', 'failed'
  start_timestamp TIMESTAMP,
  end_timestamp TIMESTAMP,
  processing_time_seconds FLOAT64,
  error_message STRING,
  output_metadata JSON
) PARTITION BY DATE(start_timestamp)
CLUSTER BY video_id, operation;
```

## Queries Analíticas

### Métricas Básicas de Vídeo

```sql
-- Vídeos mais visualizados nos últimos 30 dias
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
LIMIT 10;
```

### Performance por Dispositivo

```sql
-- Taxa de conclusão por tipo de dispositivo
SELECT
  device_type,
  COUNT(*) as total_views,
  AVG(watch_duration_seconds) as avg_watch_duration,
  AVG(completion_rate) as avg_completion_rate,
  COUNTIF(completion_rate >= 0.8) as completed_views,
  ROUND(COUNTIF(completion_rate >= 0.8) / COUNT(*) * 100, 2) as completion_rate_pct
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY device_type
ORDER BY total_views DESC;
```

### Análise Geográfica

```sql
-- Visualizações por país e cidade
SELECT
  location.country,
  location.city,
  COUNT(*) as total_views,
  COUNT(DISTINCT video_id) as unique_videos,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(watch_duration_seconds) as avg_watch_duration
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND location.country IS NOT NULL
GROUP BY location.country, location.city
HAVING total_views >= 100
ORDER BY total_views DESC
LIMIT 20;
```

## Queries de Processamento

### Status de Processamento

```sql
-- Status atual do processamento de vídeos
SELECT
  operation,
  status,
  COUNT(*) as count,
  AVG(processing_time_seconds) as avg_processing_time,
  MIN(start_timestamp) as oldest_pending,
  MAX(end_timestamp) as latest_completed
FROM `video_genius.video_analytics.video_processing`
WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY operation, status
ORDER BY operation, status;
```

### Eficiência de Processamento

```sql
-- Tempo médio de processamento por operação
SELECT
  operation,
  COUNT(*) as total_operations,
  COUNTIF(status = 'completed') as successful_operations,
  ROUND(COUNTIF(status = 'completed') / COUNT(*) * 100, 2) as success_rate_pct,
  AVG(CASE WHEN status = 'completed' THEN processing_time_seconds END) as avg_processing_time,
  APPROX_QUANTILES(processing_time_seconds, 100)[OFFSET(50)] as median_processing_time,
  APPROX_QUANTILES(processing_time_seconds, 100)[OFFSET(95)] as p95_processing_time
FROM `video_genius.video_analytics.video_processing`
WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY operation
ORDER BY total_operations DESC;
```

## Queries de Machine Learning

### Recomendação Baseada em Tags

```sql
-- Vídeos similares baseados em tags compartilhadas
WITH video_tags AS (
  SELECT
    video_id,
    tag
  FROM `video_genius.video_analytics.video_metadata`,
  UNNEST(tags) as tag
  WHERE video_id = 'VIDEO_ID_AQUI'
),
similar_videos AS (
  SELECT
    vm.video_id,
    vm.title,
    COUNT(*) as shared_tags,
    AVG(vv.watch_duration_seconds) as avg_watch_duration
  FROM `video_genius.video_analytics.video_metadata` vm
  JOIN `video_genius.video_analytics.video_views` vv ON vm.video_id = vv.video_id
  JOIN video_tags vt ON vm.video_id != vt.video_id
  WHERE vm.video_id IN (
    SELECT DISTINCT video_id
    FROM `video_genius.video_analytics.video_metadata`,
    UNNEST(tags) as tag
    WHERE tag IN (SELECT tag FROM video_tags)
  )
  GROUP BY vm.video_id, vm.title
  HAVING shared_tags >= 2
)
SELECT * FROM similar_videos
ORDER BY shared_tags DESC, avg_watch_duration DESC
LIMIT 10;
```

### Previsão de Engajamento

```sql
-- Modelo simples de previsão de engajamento
CREATE OR REPLACE MODEL `video_genius.video_analytics.engagement_prediction`
OPTIONS (
  model_type='linear_reg',
  input_label_cols=['completion_rate']
) AS
SELECT
  duration_seconds,
  ARRAY_LENGTH(tags) as num_tags,
  upload_hour,
  device_type,
  completion_rate
FROM (
  SELECT
    vm.duration_seconds,
    vm.tags,
    EXTRACT(HOUR FROM vm.upload_timestamp) as upload_hour,
    vv.device_type,
    vv.completion_rate
  FROM `video_genius.video_analytics.video_metadata` vm
  JOIN `video_genius.video_analytics.video_views` vv ON vm.video_id = vv.video_id
  WHERE vm.upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
);
```

## Queries de Monitoramento

### Alertas de Performance

```sql
-- Vídeos com baixa taxa de conclusão
SELECT
  vm.video_id,
  vm.title,
  COUNT(*) as total_views,
  AVG(vv.completion_rate) as avg_completion_rate,
  AVG(vv.watch_duration_seconds) as avg_watch_duration
FROM `video_genius.video_analytics.video_metadata` vm
JOIN `video_genius.video_analytics.video_views` vv ON vm.video_id = vv.video_id
WHERE vm.upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY vm.video_id, vm.title
HAVING avg_completion_rate < 0.3 AND total_views >= 50
ORDER BY avg_completion_rate ASC;
```

### Uso de Recursos

```sql
-- Queries mais custosas nos últimos 7 dias
SELECT
  job_id,
  query,
  total_bytes_processed,
  total_slot_ms,
  ROUND(total_bytes_processed / 1024 / 1024 / 1024, 2) as gb_processed,
  ROUND(total_slot_ms / 1000 / 60, 2) as slot_minutes,
  creation_time,
  end_time
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
ORDER BY total_bytes_processed DESC
LIMIT 10;
```

## Queries de ETL

### Carregamento Incremental

```sql
-- Merge incremental de dados de visualização
MERGE `video_genius.video_analytics.video_views` target
USING (
  SELECT
    video_id,
    user_id,
    view_timestamp,
    watch_duration_seconds,
    completion_rate,
    device_type,
    browser,
    STRUCT(country, region, city) as location,
    referrer
  FROM `video_genius.staging.new_video_views`
  WHERE processed = false
) source
ON target.video_id = source.video_id
  AND target.user_id = source.user_id
  AND target.view_timestamp = source.view_timestamp
WHEN NOT MATCHED THEN
  INSERT (video_id, user_id, view_timestamp, watch_duration_seconds,
          completion_rate, device_type, browser, location, referrer)
  VALUES (source.video_id, source.user_id, source.view_timestamp,
          source.watch_duration_seconds, source.completion_rate,
          source.device_type, source.browser, source.location, source.referrer);
```

### Limpeza de Dados

```sql
-- Remover visualizações duplicadas
CREATE OR REPLACE TABLE `video_genius.video_analytics.video_views_cleaned`
PARTITION BY DATE(view_timestamp)
CLUSTER BY video_id
AS
WITH ranked_views AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY video_id, user_id, view_timestamp
      ORDER BY watch_duration_seconds DESC
    ) as rn
  FROM `video_genius.video_analytics.video_views`
  WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
)
SELECT * EXCEPT(rn)
FROM ranked_views
WHERE rn = 1;
```

## Queries de Business Intelligence

### Dashboard de Performance

```sql
-- Métricas diárias para dashboard
SELECT
  DATE(view_timestamp) as date,
  COUNT(*) as total_views,
  COUNT(DISTINCT video_id) as videos_viewed,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(watch_duration_seconds) as avg_watch_duration,
  AVG(completion_rate) as avg_completion_rate,
  SUM(watch_duration_seconds) as total_watch_time
FROM `video_genius.video_analytics.video_views`
WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY DATE(view_timestamp)
ORDER BY date DESC;
```

### Análise de Tendências

```sql
-- Tendências semanais de upload vs visualização
WITH weekly_stats AS (
  SELECT
    DATE_TRUNC(upload_timestamp, WEEK) as week,
    COUNT(*) as videos_uploaded,
    AVG(duration_seconds) as avg_duration
  FROM `video_genius.video_analytics.video_metadata`
  WHERE upload_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY DATE_TRUNC(upload_timestamp, WEEK)
),
weekly_views AS (
  SELECT
    DATE_TRUNC(view_timestamp, WEEK) as week,
    COUNT(*) as total_views,
    COUNT(DISTINCT user_id) as unique_users
  FROM `video_genius.video_analytics.video_views`
  WHERE view_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY DATE_TRUNC(view_timestamp, WEEK)
)
SELECT
  COALESCE(ws.week, wv.week) as week,
  ws.videos_uploaded,
  wv.total_views,
  wv.unique_users,
  ROUND(wv.total_views / NULLIF(ws.videos_uploaded, 0), 2) as views_per_video
FROM weekly_stats ws
FULL OUTER JOIN weekly_views wv ON ws.week = wv.week
ORDER BY week DESC;
```

---

*Queries otimizadas para o projeto Video Genius*