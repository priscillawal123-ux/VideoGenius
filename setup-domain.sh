#!/bin/bash

# Setup Domain Mapping para Video Genius
PROJECT_ID="video-genius-prod-v1"
DOMAIN="videogenius.com.br"
SERVICE="video-genius-api"
REGION="us-central1"

echo "🔗 Configurando Domain Mapping..."
echo "Domínio: $DOMAIN"
echo "Serviço: $SERVICE"
echo ""

# Verificar se domain mapping já existe
if gcloud run domain-mappings describe $DOMAIN --region $REGION 2>/dev/null; then
  echo "✅ Domain mapping já existe"
  echo ""
  gcloud run domain-mappings describe $DOMAIN --region $REGION --format='value(status.resourceRecords[*].rrdata)'
else
  echo "⏳ Criando domain mapping..."
  gcloud run domain-mappings create \
    --service $SERVICE \
    --domain $DOMAIN \
    --region $REGION
  
  echo ""
  echo "✅ Domain mapping criado!"
fi

echo ""
echo "📝 Registros DNS necessários:"
gcloud run domain-mappings describe $DOMAIN --region $REGION --format='table(
  status.resourceRecords[].name.basename():label=HOSTNAME,
  status.resourceRecords[].rrdata.list():label=VALUE,
  status.resourceRecords[].type:label=TYPE
)'

