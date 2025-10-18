# 🌐 DNS Setup - Complete

**Data:** 18 de outubro de 2025  
**Status:** ✅ COMPLETO

---

## ✅ O que foi concluído

### 1. Zona DNS Criada
```
Nome da Zona: videogenius-api
DNS Name: api.videogenius.com.br.
Tipo: Pública
Projeto: video-genius-prod-v1
```

### 2. Registros DNS Configurados

#### Nameservers (para apontar no registrador)
```
ns-cloud-c1.googledomains.com.
ns-cloud-c2.googledomains.com.
ns-cloud-c3.googledomains.com.
ns-cloud-c4.googledomains.com.
```

#### Registros DNS
| Nome | Tipo | TTL | Dados |
|------|------|-----|-------|
| `api.videogenius.com.br.` | NS | 21600 | Google Nameservers (acima) |
| `api.videogenius.com.br.` | SOA | 21600 | Google Cloud DNS |
| `www.api.videogenius.com.br.` | CNAME | 300 | `video-genius-api-vch3lr5s3a-uc.a.run.app.` |

---

## 🔧 Próximos Passos

### 1. Adicionar Nameservers no Registrador

**Onde:**
- Registrador de domínio (ex: GoDaddy, NameCheap, Registro.br)

**O que fazer:**
1. Acesse a configuração DNS do seu domínio `videogenius.com.br`
2. Encontre a seção "Nameservers" ou "NS Records"
3. Substitua pelos nameservers do Google:
   ```
   ns-cloud-c1.googledomains.com.
   ns-cloud-c2.googledomains.com.
   ns-cloud-c3.googledomains.com.
   ns-cloud-c4.googledomains.com.
   ```
4. Salve as alterações
5. **⏳ Aguarde 24-48 horas** para propagação DNS

### 2. Verificar Propagação DNS

```bash
# Verificar se DNS foi propagado
nslookup api.videogenius.com.br

# Ou com dig
dig api.videogenius.com.br
dig www.api.videogenius.com.br
```

**Resultado esperado:**
```
api.videogenius.com.br has address 34.28.xxx.xxx
```

### 3. Configurar SSL/HTTPS (Google-managed certificate)

```bash
# Criar certificate para o domínio
gcloud compute ssl-certificates create videogenius-cert \
  --domains=api.videogenius.com.br,www.api.videogenius.com.br \
  --global

# Verificar status
gcloud compute ssl-certificates describe videogenius-cert --global
```

### 4. Criar Cloud Armor (Optional - Security)

```bash
# Criar policy de segurança
gcloud compute security-policies create videogenius-policy \
  --description="Security policy for Video Genius API"

# Aplicar ao Cloud Run (via Load Balancer)
```

### 5. Adicionar Mais Registros (Se necessário)

```bash
# Adicionar registro A para subdomínio específico
gcloud dns record-sets create api.videogenius.com.br. \
  --rrdatas="34.28.xxx.xxx" \
  --ttl=300 \
  --type=A \
  --zone=videogenius-api

# Adicionar MX record (para email)
gcloud dns record-sets create api.videogenius.com.br. \
  --rrdatas="10 mail.videogenius.com.br." \
  --ttl=3600 \
  --type=MX \
  --zone=videogenius-api

# Adicionar TXT record (para verificação)
gcloud dns record-sets create api.videogenius.com.br. \
  --rrdatas="\"v=spf1 include:google.com ~all\"" \
  --ttl=3600 \
  --type=TXT \
  --zone=videogenius-api
```

---

## 🔗 Links Úteis

**Cloud DNS Console:**
```
https://console.cloud.google.com/net-services/dns/zones/videogenius-api
```

**Cloud Run Service:**
```
https://console.cloud.google.com/run/detail/us-central1/video-genius-api
```

**Verificar DNS:**
```
https://www.whatsmydns.net/
```

---

## 📊 Arquitetura DNS

```
Internet
    ↓
videogenius.com.br (seu registrador)
    ↓
Nameservers do Google Cloud DNS
    ↓
Zona: api.videogenius.com.br.
    ↓
    ├── api.videogenius.com.br. → SOA + NS
    └── www.api.videogenius.com.br. → CNAME → Cloud Run
            ↓
    video-genius-api-vch3lr5s3a-uc.a.run.app
```

---

## ✅ Checklist Final

- [x] Zona DNS criada (videogenius-api)
- [x] Registros DNS configurados
- [x] Nameservers obtidos
- [ ] Nameservers adicionados ao registrador
- [ ] DNS propagação verificada (24-48h)
- [ ] SSL certificate criado
- [ ] Frontend atualizado com novo domínio
- [ ] Testes de conectividade realizados

---

## 🚀 Comandos Úteis

```bash
# Ver zona DNS
gcloud dns managed-zones describe videogenius-api

# Listar todos os registros
gcloud dns record-sets list --zone=videogenius-api

# Verificar DNS externamente
dig api.videogenius.com.br +short
nslookup www.api.videogenius.com.br

# Testar CNAME
dig www.api.videogenius.com.br CNAME

# Verificar IP resolvido
dig api.videogenius.com.br A +short
```

---

## 💡 Troubleshooting

### DNS não resolvendo?
1. Verifique se nameservers foram adicionados no registrador
2. Aguarde propagação DNS (até 48 horas)
3. Limpe cache DNS: `sudo systemctl restart systemd-resolved`
4. Use: `nslookup api.videogenius.com.br 8.8.8.8` (Google DNS)

### CNAME não funciona?
1. Verifique se o domínio Cloud Run está acessível
2. Confirme que TTL expirou (300 segundos)
3. Tente: `dig www.api.videogenius.com.br CNAME`

### Cloud Run retorna 404?
1. Verifique se service está rodando: `gcloud run services describe video-genius-api`
2. Confirme região: us-central1
3. Verifique IAM permissions

---

## 📝 Notas

- Zona DNS foi criada como **pública** (recomendado para Cloud Run)
- CNAME criado para `www.api.videogenius.com.br.` (subdomínio)
- TTL definido como 300 segundos (5 minutos) para rápidas mudanças
- Nameservers do Google Cloud DNS: 4 servidores para redundância

---

**Próxima Etapa:** Aguardar propagação DNS e depois configurar SSL/HTTPS  
**Status:** ✅ DNS pronto para usar!
