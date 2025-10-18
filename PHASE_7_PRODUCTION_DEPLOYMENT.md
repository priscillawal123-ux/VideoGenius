# Phase 7: Production Deployment & Monitoring Guide

**Status:** 🟢 READY FOR DEPLOYMENT  
**Last Updated:** October 18, 2025  
**Time to Complete:** 2-3 hours

---

## Overview

This guide covers the final steps to deploy Video Genius to production:

1. **DNS Configuration** - Point domain to server
2. **SSL/TLS Certificate** - Obtain Let's Encrypt certificate
3. **Cloud Run Deployment** - Deploy to Google Cloud
4. **Monitoring Setup** - Configure Cloud Logging & alerts
5. **Go-Live Testing** - Verify production environment

---

## 1. DNS Configuration (User Action Required)

### Prerequisites
- Access to domain registrar (where you registered videogenius.com.br)
- Server IP address from your hosting provider

### Steps

#### 1.1 Get Your Server IP
```bash
# If running on local server:
hostname -I

# If on Google Cloud Run (after deployment):
gcloud run services describe video-genius-backend \
  --platform managed \
  --format 'value(status.url)'
```

#### 1.2 Update DNS Records at Registrar

Log into your domain registrar (e.g., namecheap.com, godaddy.com) and update:

**A Record (IPv4):**
```
Type: A
Name: @
Value: [Your-Server-IP]
TTL: 3600
```

**CNAME for www:**
```
Type: CNAME
Name: www
Value: videogenius.com.br
TTL: 3600
```

#### 1.3 Verify DNS Resolution
```bash
# Wait 5-30 minutes for DNS propagation, then:
dig videogenius.com.br +short
nslookup videogenius.com.br
```

Expected output:
```
[Your-Server-IP]
```

---

## 2. SSL/TLS Certificate Setup

### 2.1 Install Let's Encrypt Certificate

Once DNS is resolved, obtain the certificate:

```bash
# Stop Nginx temporarily (if needed)
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
  -d videogenius.com.br \
  -d www.videogenius.com.br \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Or with Nginx plugin (if Nginx is running):
sudo certbot certonly --nginx \
  -d videogenius.com.br \
  -d www.videogenius.com.br \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive
```

### 2.2 Configure Nginx with SSL

Update `/etc/nginx/sites-available/videogenius.com.br`:

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name videogenius.com.br www.videogenius.com.br;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS with SSL
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name videogenius.com.br www.videogenius.com.br;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/videogenius.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/videogenius.com.br/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json;
    gzip_min_length 1000;
}
```

### 2.3 Reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Verify
curl -I https://videogenius.com.br
```

### 2.4 Auto-Renewal Setup

```bash
# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run

# Check timer status
sudo systemctl status certbot.timer
```

---

## 3. Cloud Run Deployment

### 3.1 Prerequisites

- Google Cloud project with billing enabled
- Service account with Cloud Run Admin role
- Docker images built and pushed to GHCR

### 3.2 Deploy Backend to Cloud Run

```bash
# Set variables
PROJECT_ID="video-genius-prod-v1"
REGION="us-central1"
IMAGE="ghcr.io/priscillawal123-ux/videogenius:latest"

# Deploy backend
gcloud run deploy video-genius-backend \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 100 \
  --min-instances 1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL="$SUPABASE_URL" \
  --set-env-vars SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
  --set-env-vars SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
  --project "$PROJECT_ID"
```

### 3.3 Deploy Frontend to Cloud Run

```bash
# Set variables
IMAGE_FRONTEND="ghcr.io/priscillawal123-ux/videogenius-frontend:latest"

# Deploy frontend
gcloud run deploy video-genius-frontend \
  --image "$IMAGE_FRONTEND" \
  --platform managed \
  --region "$REGION" \
  --memory 256Mi \
  --cpu 0.5 \
  --timeout 60 \
  --max-instances 50 \
  --min-instances 1 \
  --allow-unauthenticated \
  --project "$PROJECT_ID"
```

### 3.4 Get Service URLs

```bash
# Backend URL
gcloud run services describe video-genius-backend \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)'

# Frontend URL
gcloud run services describe video-genius-frontend \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)'
```

---

## 4. Monitoring Setup

### 4.1 Run Monitoring Setup Script

```bash
cd /home/walland/Downloads/Video-Genius

# Make script executable
chmod +x setup-monitoring.sh

# Run setup (replace with your project ID)
./setup-monitoring.sh video-genius-prod-v1
```

### 4.2 Configure Log Aggregation

```bash
# View backend logs
gcloud logging read \
  'resource.type="cloud_run_revision" 
   resource.labels.service_name="video-genius-backend"' \
  --limit 50 \
  --format json

# View errors only
gcloud logging read \
  'severity="ERROR" 
   resource.type="cloud_run_revision"' \
  --limit 20

# Stream logs real-time
gcloud logging read \
  'resource.type="cloud_run_revision"' \
  --follow
```

### 4.3 Set Up Notification Channels

1. Go to Cloud Console: https://console.cloud.google.com
2. Navigate to **Monitoring → Notification channels**
3. Create channels for:
   - Email alerts
   - Slack notifications (optional)
   - PagerDuty (optional)
4. Create alert policies:
   - High error rate (>5%)
   - Response time spike (>5s)
   - Backend service down
   - Frontend service down

---

## 5. Go-Live Testing

### 5.1 Verify DNS and SSL

```bash
# Check DNS resolution
dig videogenius.com.br +short
nslookup videogenius.com.br

# Test HTTPS
curl -I https://videogenius.com.br

# Expected output:
# HTTP/2 200
# server: nginx
# strict-transport-security: max-age=31536000
```

### 5.2 Test Frontend Access

```bash
# Open in browser
# https://videogenius.com.br

# Expected:
# ✅ Dashboard loads
# ✅ 13 tasks visible
# ✅ Stats display correctly
# ✅ Auto-refresh working
```

### 5.3 Test Backend API

```bash
# Get tasks
curl https://videogenius.com.br/api/v1/tasks

# Expected: JSON array of 21 tasks
# Expected HTTP status: 200 OK
```

### 5.4 Performance Check

```bash
# Frontend performance
curl -w "Total time: %{time_total}s\n" https://videogenius.com.br

# Expected: < 3 seconds

# Backend performance
curl -w "API response: %{time_total}s\n" \
  https://videogenius.com.br/api/v1/tasks | jq 'length'

# Expected: < 1 second, 21 tasks
```

### 5.5 Error Handling Test

```bash
# Test 404 error
curl -I https://videogenius.com.br/nonexistent

# Test invalid API request
curl https://videogenius.com.br/api/v1/tasks/invalid

# Verify errors logged in Cloud Logging
gcloud logging read 'severity="ERROR"' --limit 10
```

---

## 6. Production Checklist

### Pre-Launch
- [ ] DNS records updated and propagated (verified with `dig`)
- [ ] SSL certificate obtained and configured
- [ ] Nginx HTTPS redirect working
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed to Cloud Run
- [ ] Monitoring dashboards created
- [ ] Alert policies configured
- [ ] Log aggregation working

### Launch Day
- [ ] Test frontend access: https://videogenius.com.br
- [ ] Test API endpoints
- [ ] Verify performance metrics
- [ ] Check error logs
- [ ] Monitor resource usage
- [ ] Test mobile responsive design

### Post-Launch
- [ ] Monitor errors for 24 hours
- [ ] Check database performance
- [ ] Verify auto-scaling behavior
- [ ] Review user analytics
- [ ] Plan optimization improvements

---

## 7. Troubleshooting

### DNS Not Resolving

```bash
# Check nameserver propagation
dig videogenius.com.br NS

# Flush local DNS cache (macOS)
sudo dscacheutil -flushcache

# Flush local DNS cache (Linux)
sudo systemctl restart systemd-resolved

# Wait up to 48 hours for full propagation
```

### SSL Certificate Issues

```bash
# Verify certificate
openssl s_client -connect videogenius.com.br:443

# Check certificate expiration
certbot certificates

# Renew manually
sudo certbot renew --force-renewal
```

### Cloud Run Deployment Fails

```bash
# Check service status
gcloud run services describe video-genius-backend \
  --platform managed

# View deployment logs
gcloud run services describe video-genius-backend \
  --platform managed \
  --format json | jq '.status.conditions'

# Re-deploy with verbose output
gcloud run deploy video-genius-backend \
  --image <image-url> \
  --platform managed \
  --verbosity debug
```

### High Memory Usage

```bash
# Reduce Cloud Run memory
gcloud run services update video-genius-backend \
  --memory 256Mi \
  --platform managed

# Monitor memory in dashboard
# Cloud Console → Cloud Run → Metrics
```

---

## 8. Rollback Procedure

If issues occur after deployment:

```bash
# Rollback frontend
gcloud run services update-traffic video-genius-frontend \
  --to-revisions LATEST=0

# Revert to previous revision
gcloud run services update-traffic video-genius-frontend \
  --to-revisions [PREVIOUS-REVISION-ID]=100

# Scale down problematic service
gcloud run services update video-genius-backend \
  --min-instances 0 \
  --platform managed
```

---

## 9. Performance Optimization

### Frontend Optimization

```bash
# Enable CDN caching
# Cloud Console → CDN → Create policy

# Optimize images
npx vite build --minify

# Bundle analysis
npm run build -- --report
```

### Backend Optimization

```bash
# Increase worker processes
# Dockerfile: CMD uvicorn backend.api.main:app --workers 8

# Enable database connection pooling
# Connection pool: min=5, max=20

# Configure caching headers
# For API responses: Cache-Control: max-age=300
```

---

## 10. Monitoring Dashboard

Access production metrics:

**Cloud Console:** https://console.cloud.google.com/monitoring/dashboards

**Key Metrics:**
- Request latency (p50, p95, p99)
- Error rate percentage
- Traffic volume (requests/sec)
- Resource utilization (CPU, memory)
- Database query performance
- Frontend load time

---

## Next Steps

1. **Update DNS** at domain registrar (BLOCKING)
2. **Obtain SSL certificate** via Let's Encrypt
3. **Deploy to Cloud Run** services
4. **Monitor production** environment
5. **Gather user feedback** and optimize

---

## Support Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Cloud Logging Guide](https://cloud.google.com/logging/docs)
- [Project Repository](https://github.com/priscillawal123-ux/VideoGenius)

---

**Status:** 🟢 Ready for Production  
**Last Updated:** October 18, 2025  
**Maintained By:** Development Team
