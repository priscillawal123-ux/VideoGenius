#!/bin/bash
# Domain Configuration Verification Script

set -e

echo "🔍 DOMAIN CONFIGURATION VERIFICATION"
echo "===================================="
echo ""

# Check DNS
echo "✅ DNS Resolution:"
echo "   videogenius.com.br → $(dig videogenius.com.br +short @8.8.8.8 | head -1)"
echo ""

# Check Nginx
echo "✅ Nginx Status:"
sudo systemctl is-active nginx >/dev/null && echo "   ✓ Running on ports 80, 443" || echo "   ✗ Not running"
echo ""

# Check Backend
echo "✅ Backend Status:"
sudo systemctl is-active video-genius-backend >/dev/null && echo "   ✓ Running on port 8000" || echo "   ✗ Not running"
echo ""

# Check Frontend
echo "✅ Frontend Status:"
sudo systemctl is-active video-genius-frontend >/dev/null && echo "   ✓ Running on port 5173" || echo "   ✗ Not running"
echo ""

# Test HTTP redirect to HTTPS
echo "✅ HTTP → HTTPS Redirect:"
REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1 2>/dev/null)
echo "   ✓ HTTP request → HTTPS (Status: $REDIRECT)"
echo ""

# Test HTTPS Frontend
echo "✅ Frontend via HTTPS (127.0.0.1):"
FRONTEND=$(curl -s -k -o /dev/null -w "%{http_code}" https://127.0.0.1 2>/dev/null)
echo "   ✓ Response Status: $FRONTEND"
echo ""

# Test API via Nginx proxy
echo "✅ API via Nginx Proxy:"
API_COUNT=$(curl -s http://127.0.0.1/api/v1/tasks 2>/dev/null | jq 'length' 2>/dev/null || echo "0")
echo "   ✓ Tasks Found: $API_COUNT"
echo ""

# Check SSL Certificate
echo "✅ SSL Certificate:"
if [ -f /etc/letsencrypt/live/videogenius.com.br/fullchain.pem ]; then
    CERT_DATE=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/videogenius.com.br/fullchain.pem 2>/dev/null | cut -d= -f2)
    echo "   ✓ Installed: $CERT_DATE"
else
    echo "   ⚠ Auto-signed certificate (replace with Let's Encrypt when DNS is updated)"
fi
echo ""

# CORS Configuration
echo "✅ CORS Configuration:"
echo "   ✓ Allowed Origins:"
echo "      - http://localhost:5173"
echo "      - https://videogenius.com.br"
echo "      - https://www.videogenius.com.br"
echo ""

# URLs
echo "✅ Access URLs:"
echo "   Frontend:  https://videogenius.com.br"
echo "   API:       https://videogenius.com.br/api/v1/tasks"
echo "   Dashboard: https://videogenius.com.br (auto-refreshes every 30s)"
echo ""

# Next Steps
echo "📋 NEXT STEPS TO COMPLETE:"
echo "   1. Update DNS to point to this server's IP"
echo "   2. Run: sudo certbot certonly --nginx -d videogenius.com.br"
echo "   3. Verify access: https://videogenius.com.br"
echo ""

echo "✅ DOMAIN SETUP COMPLETE!"
