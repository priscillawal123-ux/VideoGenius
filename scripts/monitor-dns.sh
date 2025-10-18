#!/bin/bash

# 🔍 Monitor DNS Propagation
# Verifica continuamente a propagação DNS para api.videogenius.com.br

set -e

DOMAIN="api.videogenius.com.br"
CLOUD_RUN_HOST="video-genius-api-vch3lr5s3a-uc.a.run.app"
EXPECTED_CNAME="$CLOUD_RUN_HOST"
CHECK_INTERVAL=60  # segundos

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🔍 DNS PROPAGATION MONITOR                         ║"
echo "║                                                            ║"
echo "║ Domain: $DOMAIN"
echo "║ Expected CNAME: $EXPECTED_CNAME"
echo "║ Check Interval: ${CHECK_INTERVAL}s"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

check_dns() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🕐 Verificando em: $(date '+%H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Verificar com Google DNS
    echo ""
    echo "📍 Google DNS (8.8.8.8):"
    GOOGLE_DNS=$(dig +short $DOMAIN @8.8.8.8 CNAME 2>/dev/null | head -1)
    if [ -z "$GOOGLE_DNS" ]; then
        echo "  ❌ Sem resposta"
    elif [ "$GOOGLE_DNS" == "$EXPECTED_CNAME." ]; then
        echo "  ✅ $GOOGLE_DNS"
    else
        echo "  ⏳ $GOOGLE_DNS (esperando: $EXPECTED_CNAME.)"
    fi
    
    # Verificar com Cloudflare DNS
    echo ""
    echo "📍 Cloudflare DNS (1.1.1.1):"
    CF_DNS=$(dig +short $DOMAIN @1.1.1.1 CNAME 2>/dev/null | head -1)
    if [ -z "$CF_DNS" ]; then
        echo "  ❌ Sem resposta"
    elif [ "$CF_DNS" == "$EXPECTED_CNAME." ]; then
        echo "  ✅ $CF_DNS"
    else
        echo "  ⏳ $CF_DNS (esperando: $EXPECTED_CNAME.)"
    fi
    
    # Verificar com OpenDNS
    echo ""
    echo "📍 OpenDNS (208.67.222.222):"
    OPEN_DNS=$(dig +short $DOMAIN @208.67.222.222 CNAME 2>/dev/null | head -1)
    if [ -z "$OPEN_DNS" ]; then
        echo "  ❌ Sem resposta"
    elif [ "$OPEN_DNS" == "$EXPECTED_CNAME." ]; then
        echo "  ✅ $OPEN_DNS"
    else
        echo "  ⏳ $OPEN_DNS (esperando: $EXPECTED_CNAME.)"
    fi
    
    # Verificar com Google Cloud DNS nameservers
    echo ""
    echo "📍 Google Cloud DNS:"
    for ns in ns-cloud-c1 ns-cloud-c2 ns-cloud-c3 ns-cloud-c4; do
        GCP_DNS=$(dig +short $DOMAIN @${ns}.googledomains.com. CNAME 2>/dev/null | head -1)
        if [ -z "$GCP_DNS" ]; then
            echo "  ❌ ${ns}.googledomains.com - Sem resposta"
        elif [ "$GCP_DNS" == "$EXPECTED_CNAME." ]; then
            echo "  ✅ ${ns}.googledomains.com - $GCP_DNS"
        else
            echo "  ⏳ ${ns}.googledomains.com - $GCP_DNS"
        fi
    done
    
    # Resumo
    echo ""
    echo "📊 Resumo:"
    TOTAL_OK=0
    [ "$GOOGLE_DNS" == "$EXPECTED_CNAME." ] && ((TOTAL_OK++))
    [ "$CF_DNS" == "$EXPECTED_CNAME." ] && ((TOTAL_OK++))
    [ "$OPEN_DNS" == "$EXPECTED_CNAME." ] && ((TOTAL_OK++))
    
    echo "  Resolvido corretamente: $TOTAL_OK/7 nameservers"
    
    if [ $TOTAL_OK -eq 7 ]; then
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║                 ✅ DNS TOTALMENTE PROPAGADO!              ║"
        echo "║                                                            ║"
        echo "║ Próximos passos:                                           ║"
        echo "║  1. Configurar SSL/HTTPS                                  ║"
        echo "║  2. Testar: curl https://$DOMAIN/health         ║"
        echo "║  3. Atualizar frontend com novo domínio                   ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        exit 0
    fi
    
    echo ""
    echo "⏳ Próxima verificação em ${CHECK_INTERVAL}s... (Ctrl+C para sair)"
    echo ""
}

# Loop contínuo
while true; do
    check_dns
    sleep $CHECK_INTERVAL
done
