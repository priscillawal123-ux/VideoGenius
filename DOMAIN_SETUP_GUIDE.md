# Domain Configuration & Next Steps for Video Genius

## ✅ Current Status

### Infrastructure Running
- **Nginx**: Listening on ports 80 (HTTP → HTTPS redirect) and 443 (HTTPS)
- **Frontend**: Vite dev server on port 5173 (proxied via Nginx)
- **Backend**: FastAPI with Uvicorn on port 8000 (proxied via Nginx)
- **All Services**: Systemd managed with auto-restart enabled

### DNS Configuration
- **Domain**: videogenius.com.br
- **Current IP**: 34.143.74.2 (Cloud Run - old production instance)
- **Local IP**: 192.168.15.69 (where Nginx is running)

### SSL/TLS
- **Current**: Self-signed certificate (valid for local testing)
- **Production Certificate**: Let's Encrypt (ready to install when DNS is updated)

---

## 📋 Required DNS Update

To make `videogenius.com.br` accessible via this server:

### Step 1: Update DNS Records at Your Registrar

**A Record:**
```
Domain: videogenius.com.br
Type: A
Value: [YOUR_SERVER_IP]  # Replace with actual server IP
TTL: 3600
```

**CNAME Record (optional, for www):**
```
Domain: www.videogenius.com.br
Type: CNAME
Value: videogenius.com.br
TTL: 3600
```

### Step 2: Update Nameservers (if using DNS hosting)

Contact your domain registrar to point nameservers to your DNS provider or update A record directly.

---

## 🔒 SSL Certificate Installation

Once DNS is updated (Step 1 above):

```bash
# Obtain Let's Encrypt certificate
sudo certbot certonly --nginx \
  -d videogenius.com.br \
  -d www.videogenius.com.br \
  --agree-tos \
  -m your-email@example.com

# Verify installation
openssl x509 -in /etc/letsencrypt/live/videogenius.com.br/fullchain.pem -noout -text | grep -E "(Not Before|Not After)"

# Restart Nginx
sudo systemctl restart nginx
```

---

## 🌐 Access URLs (After DNS Update)

```
Frontend:  https://videogenius.com.br
           https://www.videogenius.com.br

API:       https://videogenius.com.br/api/v1/tasks
Dashboard: https://videogenius.com.br (auto-refreshes every 30s)
```

---

## ✅ Current Nginx Configuration

### HTTP → HTTPS Redirect
```nginx
server {
    listen 80;
    server_name videogenius.com.br www.videogenius.com.br;
    return 301 https://$server_name$request_uri;
}
```

### HTTPS Reverse Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name videogenius.com.br www.videogenius.com.br;
    
    # Frontend (Vite on 5173)
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_http_version 1.1;
    }
    
    # Backend API (FastAPI on 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔐 CORS Configuration

Backend (`backend/core/config.py`) configured to accept:
- `https://videogenius.com.br`
- `https://www.videogenius.com.br`
- `http://localhost:5173` (development)
- `https://video-genius.com` (legacy)

---

## 🚀 Testing Locally

### Test Frontend (via Nginx on localhost)
```bash
curl -k https://127.0.0.1 2>/dev/null | head -5
```

### Test API (via Nginx proxy)
```bash
curl -s http://127.0.0.1/api/v1/tasks | jq 'length'
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/videogenius.access.log
sudo tail -f /var/log/nginx/videogenius.error.log
```

---

## 📊 Service Management

```bash
# Check all services
sudo systemctl status nginx video-genius-backend video-genius-frontend

# View service logs
sudo journalctl -u video-genius-backend -f
sudo journalctl -u video-genius-frontend -f
sudo journalctl -u nginx -f

# Restart Nginx (after DNS update)
sudo systemctl restart nginx
sudo certbot renew  # Auto-renews 30 days before expiry
```

---

## ⚠️ Known Issues & Workarounds

### Issue: SSL Certificate Warning
**Cause**: Using self-signed certificate until DNS is updated
**Resolution**: Update DNS (Step 1) and obtain Let's Encrypt certificate (Step 2)

### Issue: Frontend shows "Cannot GET /"
**Cause**: Vite dev server responding with 404
**Resolution**: Verify Vite is running on port 5173:
```bash
sudo lsof -i :5173
```

### Issue: API returns CORS errors
**Cause**: Origin not in CORS whitelist
**Resolution**: Verify backend has `https://videogenius.com.br` in `cors_origins`

---

## 📝 Configuration Files

| File | Purpose |
|------|---------|
| `/etc/nginx/sites-available/videogenius.com.br` | Nginx reverse proxy config |
| `/etc/systemd/system/video-genius-backend.service` | Backend service definition |
| `/etc/systemd/system/video-genius-frontend.service` | Frontend service definition |
| `/home/walland/Downloads/Video-Genius/backend/core/config.py` | CORS settings, backend config |
| `/home/walland/Downloads/Video-Genius/frontend/vite.config.ts` | Frontend build/dev config |

---

## 🎯 Next Steps

1. **Update DNS** → Point `videogenius.com.br` to your server IP
2. **Wait for DNS propagation** → ~5-30 minutes
3. **Obtain SSL cert** → Run certbot command above
4. **Verify HTTPS access** → Visit https://videogenius.com.br
5. **Monitor dashboard** → Tasks should load with live data

---

## 📞 Support

To verify everything is working:
```bash
# All-in-one test
./verify-domain.sh
```

If Nginx fails, check:
```bash
sudo nginx -t                           # Syntax check
sudo systemctl status nginx             # Service status
sudo tail -50 /var/log/nginx/error.log # Error logs
```

---

**Status**: ✅ Ready for domain activation
