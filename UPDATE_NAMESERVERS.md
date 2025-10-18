# 🔧 Como Atualizar Nameservers no Seu Registrador

**Problema:** DNS ainda aponta para Google Sites (ghs.googlehosted.com)  
**Solução:** Atualizar nameservers no seu registrador

---

## ⚡ Nameservers do Google Cloud DNS

Copie estes 4 nameservers:

```
ns-cloud-c1.googledomains.com.
ns-cloud-c2.googledomains.com.
ns-cloud-c3.googledomains.com.
ns-cloud-c4.googledomains.com.
```

---

## 📍 Passo a Passo por Registrador

### 🔵 **Registro.br** (Registrador Brasileiro)

1. Acesse: https://www.registro.br/
2. Faça login com sua conta
3. Clique em "Meus Domínios"
4. Selecione `videogenius.com.br`
5. Clique em "Editar Domínio" ou "Configurar NS"
6. Procure por "Servidores de Nomes" ou "Nameservers"
7. **Substitua** os nameservers atuais pelos do Google:
   ```
   ns-cloud-c1.googledomains.com.
   ns-cloud-c2.googledomains.com.
   ns-cloud-c3.googledomains.com.
   ns-cloud-c4.googledomains.com.
   ```
8. Clique em "Salvar" ou "Confirmar"
9. **⏳ Aguarde 24-48 horas** (DNS propaga globalmente)

---

### 🟠 **GoDaddy**

1. Acesse: https://www.godaddy.com/
2. Faça login
3. Vá para "Meus Produtos" → "Domínios"
4. Clique em `videogenius.com.br`
5. Procure por "Nameservers" e clique "Alterar"
6. Selecione "Usar seus próprios nameservers"
7. Insira os 4 nameservers do Google
8. Salve

---

### 🔴 **NameCheap**

1. Acesse: https://www.namecheap.com/
2. Faça login
3. Vá para "Dashboard" → "Domain List"
4. Clique no ícone de engrenagem ao lado do domínio
5. Procure por "Nameservers"
6. Selecione "Custom DNS"
7. Substitua pelos nameservers do Google
8. Salve

---

### 🟡 **UOL/ViaWebsite**

1. Acesse: https://seudominio.com.br/ (ou seu painel UOL)
2. Faça login
3. Acesse "Configurações do Domínio"
4. Procure por "DNS" ou "Nameservers"
5. Edite os nameservers
6. Insira os 4 do Google Cloud DNS
7. Confirme

---

### 🟣 **HostGator / iHostGator**

1. Acesse: https://www.hostgator.com.br/
2. Faça login no painel de controle
3. Vá para "Meus Produtos" → "Domínios"
4. Clique em "Gerenciar Domínio"
5. Procure por "Gerenciar Nameservers" ou "DNS"
6. Clique em "Editar Nameservers"
7. Substitua pelos do Google
8. Salve

---

### 🔷 **Locaweb**

1. Acesse: https://www.locaweb.com.br/
2. Faça login
3. Vá para "Gerenciador de Domínios"
4. Selecione `videogenius.com.br`
5. Clique em "Configurar DNS"
6. Edite os nameservers
7. Insira os 4 do Google Cloud DNS
8. Salve

---

## ✅ Depois de Atualizar

### 1️⃣ Aguardar Propagação (24-48h)

```bash
# Verificar status da propagação
dig api.videogenius.com.br NS
```

### 2️⃣ Verificar Resolução

```bash
# Verificar se DNS foi resolvido corretamente
nslookup api.videogenius.com.br 8.8.8.8

# Resultado esperado:
# api.videogenius.com.br  canonical name = video-genius-api-vch3lr5s3a-uc.a.run.app.
# Name: video-genius-api-vch3lr5s3a-uc.a.run.app
# Address: 34.28.xxx.xxx
```

### 3️⃣ Verificar com dig

```bash
# Ver registros NS
dig api.videogenius.com.br NS

# Ver registros A
dig api.videogenius.com.br A

# Ver CNAME completo
dig www.api.videogenius.com.br CNAME
```

---

## 🔍 Diagnosticar Problema

### Se DNS ainda não funcionar:

```bash
# 1. Verificar nameservers configurados
whois api.videogenius.com.br | grep -i "nameserver"

# 2. Verificar propagação em tempo real
dig api.videogenius.com.br @ns-cloud-c1.googledomains.com.

# 3. Limpar cache DNS local
sudo systemctl restart systemd-resolved

# 4. Testar com diferentes DNS
nslookup api.videogenius.com.br 8.8.8.8      # Google DNS
nslookup api.videogenius.com.br 1.1.1.1      # Cloudflare DNS
nslookup api.videogenius.com.br 208.67.222.222 # OpenDNS
```

---

## 📊 Status Atual

| Componente | Status | Detalhes |
|-----------|--------|----------|
| Zona DNS GCP | ✅ Criada | videogenius-api |
| Registros DNS | ✅ Configurados | www → Cloud Run |
| Nameservers GCP | ✅ Prontos | ns-cloud-c1/2/3/4 |
| Nameservers Registrador | ❌ Pendente | **VOCÊ PRECISA FAZER ISSO** |
| Propagação DNS | ⏳ Aguardando | Após atualizar registrador |

---

## 💡 Dica Importante

**Guarde este link para verificar propagação DNS em tempo real:**

```
https://www.whatsmydns.net/#A/api.videogenius.com.br
```

Nele você pode ver o status de propagação DNS em todos os nameservers globais.

---

## ⚠️ Timeframe

- **Imediato:** Até 5 minutos para alguns provedores
- **Típico:** 15 minutos a 2 horas
- **Máximo:** Até 48 horas para propagação global

Se após 2 horas ainda não funcionar, verifique:
1. Se os nameservers foram realmente salvos no registrador
2. Se digitou corretamente (sem espaços extras)
3. Limpe o cache DNS local

---

## 🎯 Próximo Passo

Depois que o DNS estiver resolvendo para Cloud Run:

1. Configurar SSL/HTTPS (Google-managed certificate)
2. Testar endpoint: `curl https://api.videogenius.com.br/health`
3. Atualizar frontend com novo domínio
4. Começar Phase 2 (Backend Connection)

---

**Status:** ⏳ Aguardando sua ação no registrador  
**Tempo estimado:** 5 minutos para atualizar + 2 horas para propagar
