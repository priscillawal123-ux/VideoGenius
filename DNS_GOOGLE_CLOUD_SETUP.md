# 🌐 DNS com Google Cloud DNS (Sem Google Domains)

**Data:** 18 de outubro de 2025  
**Status:** ✅ Pronto para Configurar  
**Problema Resolvido:** Google Domains descontinuado

---

## 📋 Resumo da Solução

Como Google Domains foi vendido, vamos usar **Google Cloud DNS puro** com seu registrador atual.

**Vantagens:**
- ✅ Funciona com qualquer registrador (Registro.br, GoDaddy, etc)
- ✅ Nameservers confiáveis do Google Cloud
- ✅ Gerenciamento 100% na GCP Console
- ✅ Melhor performance e segurança

---

## ⚡ Criar Nova Zona DNS

### Passo 1: Criar Zona DNS Pública no GCP

```bash
# Deletar a zona antiga (já feito)
gcloud dns managed-zones delete videogenius-api --quiet

# Criar nova zona DNS
gcloud dns managed-zones create videogenius-dns \
  --dns-name="videogenius.com.br." \
  --description="Main DNS zone for Video Genius" \
  --visibility=public

# Verificar zona criada
gcloud dns managed-zones describe videogenius-dns
```

---

## 🔧 Obter Nameservers do Google Cloud DNS

Estes são os nameservers que você vai usar no seu registrador:

```bash
# Comando para obter nameservers
gcloud dns managed-zones describe videogenius-dns \
  --format='value(nameServers[])'
```

**Resultado esperado:**
```
ns-cloud-b1.googledomains.com.
ns-cloud-b2.googledomains.com.
ns-cloud-b3.googledomains.com.
ns-cloud-b4.googledomains.com.
```

---

## 📝 Adicionar Registros DNS

### 1️⃣ Registro A para o Apex (raiz)

```bash
# Obter IP do Cloud Run
CLOUD_RUN_IP=$(gcloud run services describe video-genius-api \
  --region us-central1 \
  --format='value(status.loadBalancer.ingress[0].ipAddress)')

echo "IP: $CLOUD_RUN_IP"

# Adicionar registro A (apontando para IP do Cloud Run)
gcloud dns record-sets create videogenius.com.br. \
  --rrdatas="$CLOUD_RUN_IP" \
  --ttl=300 \
  --type=A \
  --zone=videogenius-dns
```

### 2️⃣ Registro CNAME para API

```bash
# Criar CNAME para api.videogenius.com.br
gcloud dns record-sets create api.videogenius.com.br. \
  --rrdatas="video-genius-api-vch3lr5s3a-uc.a.run.app." \
  --ttl=300 \
  --type=CNAME \
  --zone=videogenius-dns
```

### 3️⃣ Registro CNAME para WWW (opcional)

```bash
# Criar CNAME para www
gcloud dns record-sets create www.videogenius.com.br. \
  --rrdatas="video-genius-api-vch3lr5s3a-uc.a.run.app." \
  --ttl=300 \
  --type=CNAME \
  --zone=videogenius-dns
```

---

## 📊 Verificar Registros Criados

```bash
# Listar todos os registros
gcloud dns record-sets list --zone=videogenius-dns

# Resultado esperado:
# NAME                        TYPE  TTL  DATA
# videogenius.com.br.        A     300  34.28.xxx.xxx
# api.videogenius.com.br.    CNAME 300  video-genius-api...
# www.videogenius.com.br.    CNAME 300  video-genius-api...
```

---

## 🔑 Configurar no Seu Registrador

### Exemplo: Registro.br

1. **Acesse:** https://www.registro.br/
2. **Login** com sua conta
3. **Meus Domínios** → Selecione `videogenius.com.br`
4. **Editar Domínio** ou **Configurar NS**
5. **Servidores de Nomes** → Clique em "Editar"
6. **Substitua** pelos nameservers do Google Cloud:
   ```
   ns-cloud-b1.googledomains.com.
   ns-cloud-b2.googledomains.com.
   ns-cloud-b3.googledomains.com.
   ns-cloud-b4.googledomains.com.
   ```
7. **Salvar** ou **Confirmar**
8. **Aguarde 2-24 horas** para propagação

### Outros Registradores

**GoDaddy, NameCheap, Locaweb, HostGator:**
- Procure por "Nameservers" ou "DNS Settings"
- Selecione "Custom DNS" ou "Usar meus próprios nameservers"
- Insira os 4 nameservers acima
- Salve

---

## ✅ Script Completo (Execute Tudo de Uma Vez)

```bash
#!/bin/bash

# 1. Criar zona DNS
echo "📍 Criando zona DNS..."
gcloud dns managed-zones create videogenius-dns \
  --dns-name="videogenius.com.br." \
  --description="Main DNS zone for Video Genius" \
  --visibility=public

# 2. Obter IP do Cloud Run
echo "🔍 Obtendo IP do Cloud Run..."
CLOUD_RUN_IP=$(gcloud run services describe video-genius-api \
  --region us-central1 \
  --format='value(status.loadBalancer.ingress[0].ipAddress)')

echo "IP obtido: $CLOUD_RUN_IP"

# 3. Criar registros A e CNAME
echo "📝 Adicionando registros DNS..."

# Registro A (apex)
gcloud dns record-sets create videogenius.com.br. \
  --rrdatas="$CLOUD_RUN_IP" \
  --ttl=300 \
  --type=A \
  --zone=videogenius-dns

# CNAME para API
gcloud dns record-sets create api.videogenius.com.br. \
  --rrdatas="video-genius-api-vch3lr5s3a-uc.a.run.app." \
  --ttl=300 \
  --type=CNAME \
  --zone=videogenius-dns

# CNAME para WWW
gcloud dns record-sets create www.videogenius.com.br. \
  --rrdatas="video-genius-api-vch3lr5s3a-uc.a.run.app." \
  --ttl=300 \
  --type=CNAME \
  --zone=videogenius-dns

# 4. Obter nameservers
echo ""
echo "✅ Zona DNS criada!"
echo ""
echo "📍 Use estes Nameservers no seu Registrador:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gcloud dns managed-zones describe videogenius-dns \
  --format='value(nameServers[])'
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 5. Listar registros
echo ""
echo "📊 Registros DNS criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gcloud dns record-sets list --zone=videogenius-dns
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "⏳ Próximos passos:"
echo "  1. Adicione os nameservers acima no seu registrador"
echo "  2. Aguarde 2-24 horas para propagação"
echo "  3. Teste: dig videogenius.com.br"
echo "  4. Configure SSL/HTTPS no Cloud Run"
```

---

## 🔍 Verificar Propagação DNS

```bash
# Verificar com Google DNS
nslookup videogenius.com.br 8.8.8.8

# Verificar com Cloudflare
nslookup videogenius.com.br 1.1.1.1

# Ver todos os registros
dig videogenius.com.br ANY

# Ver especificamente A record
dig videogenius.com.br A

# Ver CNAME
dig api.videogenius.com.br CNAME
```

---

## 📱 Monitorar Propagação em Tempo Real

Use este site para verificar propagação global:

```
https://www.whatsmydns.net/#A/videogenius.com.br
```

---

## 🎯 Arquitetura Final

```
┌─────────────────────────────────────┐
│   Registrador (Registro.br, etc)    │
│   videogenius.com.br NS:            │
│   ns-cloud-b1/b2/b3/b4              │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│   Google Cloud DNS                   │
│   ┌──────────────────────────────┐   │
│   │ Zona: videogenius.com.br.    │   │
│   ├──────────────────────────────┤   │
│   │ videogenius.com.br.      A   │   │
│   │  → 34.28.xxx.xxx             │   │
│   ├──────────────────────────────┤   │
│   │ api.videogenius.com.br.  CNAME   │
│   │  → video-genius-api...       │   │
│   ├──────────────────────────────┤   │
│   │ www.videogenius.com.br.  CNAME   │
│   │  → video-genius-api...       │   │
│   └──────────────────────────────┘   │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│   Cloud Run Service                  │
│   video-genius-api                   │
│   https://api.videogenius.com.br     │
└──────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] Zona DNS criada no GCP (videogenius-dns)
- [ ] Registros A e CNAME adicionados
- [ ] Nameservers copiados (ns-cloud-b1/b2/b3/b4)
- [ ] Nameservers adicionados no registrador
- [ ] Aguardado 2-24 horas para propagação
- [ ] DNS testado com `dig` ou `nslookup`
- [ ] SSL/HTTPS configurado
- [ ] Frontend atualizado com novo domínio

---

## 💡 Diferenças: Google Domains vs Google Cloud DNS

| Aspecto | Google Domains | Google Cloud DNS |
|---------|---|---|
| **Status** | ❌ Descontinuado | ✅ Ativo |
| **Nameservers** | ns-cloud-goog-c.googledomains.com | ns-cloud-b[1-4].googledomains.com |
| **Configuração** | Interface Web | gcloud CLI + Console |
| **Compatibilidade** | Apenas Google | Qualquer registrador |
| **Custo** | Incluído | $0.40 USD/zona/mês |

---

## 🚀 Próximas Etapas

1. **Configurar SSL/HTTPS**
   ```bash
   gcloud compute ssl-certificates create videogenius-cert \
     --domains=videogenius.com.br,www.videogenius.com.br,api.videogenius.com.br \
     --global
   ```

2. **Mapear domínio ao Cloud Run**
   ```bash
   gcloud run services update video-genius-api \
     --region us-central1 \
     --set-env-vars API_DOMAIN=api.videogenius.com.br
   ```

3. **Testar Endpoint**
   ```bash
   curl https://api.videogenius.com.br/health
   ```

---

**Status:** ✅ Pronto para configurar no seu registrador  
**Tempo:** 5 minutos de setup + 2-24 horas de propagação
