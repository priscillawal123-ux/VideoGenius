# 🔧 Systemd Configuration - 24/7 Service Setup

**Status**: ✅ Ready to Deploy  
**Date**: 18 de outubro de 2025  
**Goal**: Run Video Genius Backend & Frontend as permanent systemd services

---

## 📋 Overview

Video Genius will run 24/7 with:
- ✅ Automatic restart on failure
- ✅ Process supervision
- ✅ Log aggregation via journalctl
- ✅ Resource limits protection
- ✅ Security hardening

---

## 🚀 Installation Steps

### Step 1: Create Systemd Configuration Directory

```bash
sudo mkdir -p /etc/systemd/system
cd /home/walland/Downloads/Video-Genius
```

### Step 2: Copy Service Files

#### Backend Service

```bash
# Copy service file
sudo cp systemd/video-genius-backend.service /etc/systemd/system/

# Verify
sudo cat /etc/systemd/system/video-genius-backend.service
```

#### Frontend Service

```bash
# Copy service file
sudo cp systemd/video-genius-frontend.service /etc/systemd/system/

# Verify
sudo cat /etc/systemd/system/video-genius-frontend.service
```

### Step 3: Reload Systemd

```bash
# Reload daemon
sudo systemctl daemon-reload

# Verify services are recognized
sudo systemctl list-unit-files | grep video-genius
```

**Expected Output:**
```
video-genius-backend.service    disabled
video-genius-frontend.service   disabled
```

### Step 4: Create Environment File

```bash
# Create production environment file
sudo tee /home/walland/Downloads/Video-Genius/.env.production > /dev/null << 'EOF'
# API Configuration
ENVIRONMENT=production
LOG_LEVEL=info
DEBUG=false

# Supabase
SUPABASE_URL=https://dfxffpdhxrqzybzjsyxg.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your-webhook-secret-32-chars
GITHUB_REPO_OWNER=priscillawal123-ux
GITHUB_REPO_NAME=VideoGenius

# Google Cloud
GOOGLE_PROJECT_ID=video-genius-prod-v1

# Frontend
VITE_API_URL=https://api.videogenius.com.br

# Server Configuration
PORT=8000
WORKERS=4
EOF

# Set proper permissions
sudo chmod 600 /home/walland/Downloads/Video-Genius/.env.production
sudo chown www-data:www-data /home/walland/Downloads/Video-Genius/.env.production
```

### Step 5: Verify Service Configuration

```bash
# Check backend service
sudo systemd-analyze verify video-genius-backend.service

# Check frontend service
sudo systemd-analyze verify video-genius-frontend.service
```

### Step 6: Enable and Start Services

#### Start Backend

```bash
# Enable on boot
sudo systemctl enable video-genius-backend.service

# Start service
sudo systemctl start video-genius-backend.service

# Check status
sudo systemctl status video-genius-backend.service

# View logs
sudo journalctl -u video-genius-backend -f
```

#### Start Frontend

```bash
# Enable on boot
sudo systemctl enable video-genius-frontend.service

# Start service
sudo systemctl start video-genius-frontend.service

# Check status
sudo systemctl status video-genius-frontend.service

# View logs
sudo journalctl -u video-genius-frontend -f
```

---

## 📊 Service Management

### View Service Status

```bash
# Both services
sudo systemctl status video-genius-{backend,frontend}.service

# Pretty output
sudo systemctl -l --all | grep video-genius
```

### View Logs

```bash
# Backend logs (real-time)
sudo journalctl -u video-genius-backend -f

# Frontend logs (real-time)
sudo journalctl -u video-genius-frontend -f

# Combined logs
sudo journalctl -u video-genius-backend -u video-genius-frontend -f

# Last 100 lines
sudo journalctl -u video-genius-backend -n 100

# With timestamps
sudo journalctl -u video-genius-backend --since "2 hours ago"

# Search for errors
sudo journalctl -u video-genius-backend -p err -f
```

### Control Services

```bash
# Stop services
sudo systemctl stop video-genius-backend
sudo systemctl stop video-genius-frontend

# Restart services
sudo systemctl restart video-genius-backend
sudo systemctl restart video-genius-frontend

# Reload configuration (without restart)
sudo systemctl reload video-genius-backend

# Disable on boot
sudo systemctl disable video-genius-backend
sudo systemctl disable video-genius-frontend
```

### Check Resource Usage

```bash
# Monitor service resources
sudo systemctl status video-genius-backend -l

# View memory and CPU
ps aux | grep video-genius

# Monitor in real-time
top -p $(pgrep -f video-genius-backend)
```

---

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check for syntax errors
sudo systemd-analyze verify video-genius-backend.service

# View error logs
sudo journalctl -u video-genius-backend -n 50

# Test service manually
cd /home/walland/Downloads/Video-Genius
source .venv/bin/activate
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

### Permission Denied

```bash
# Check file ownership
ls -la /home/walland/Downloads/Video-Genius/

# Fix permissions
sudo chown -R www-data:www-data /home/walland/Downloads/Video-Genius/

# Check systemd unit permissions
sudo ls -la /etc/systemd/system/video-genius-*
```

### Environment Variables Not Loading

```bash
# Verify .env.production exists and is readable
sudo cat /home/walland/Downloads/Video-Genius/.env.production

# Test with cat
EnvironmentFile=-/path/to/file  # - means fail silently if missing
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Change port in service file
sudo systemctl edit video-genius-backend
```

---

## 🔐 Security Hardening

### File Permissions

```bash
# Set correct ownership
sudo chown -R www-data:www-data /home/walland/Downloads/Video-Genius/

# Set directory permissions (755)
sudo chmod 755 /home/walland/Downloads/Video-Genius/

# Set private file permissions (640)
sudo chmod 640 /home/walland/Downloads/Video-Genius/.env.production

# Set executable permissions for scripts
sudo chmod 755 /home/walland/Downloads/Video-Genius/scripts/*.sh
```

### Firewall Configuration

```bash
# Allow port 8000 from localhost only
sudo ufw allow 127.0.0.1:8000

# Allow port 8000 from specific IP
sudo ufw allow from 192.168.1.100 to any port 8000

# Allow port 3000 for frontend
sudo ufw allow 3000
```

### SELinux Configuration (if enabled)

```bash
# Check if SELinux is enabled
getenforce

# Set appropriate context (if needed)
sudo semanage fcontext -a -t httpd_var_run_t "/home/walland/Downloads/Video-Genius(/.*)?"
```

---

## 📈 Monitoring & Alerts

### Setup Log Rotation

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/video-genius > /dev/null << 'EOF'
/var/log/video-genius/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload video-genius-backend > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Setup Monitoring

```bash
# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Monitor services
htop -p $(pgrep -f video-genius)

# Monitor network
nethogs
```

### Health Checks

```bash
# Create health check script
cat > /home/walland/Downloads/Video-Genius/scripts/health-check.sh << 'EOF'
#!/bin/bash

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
echo "Backend: $BACKEND_STATUS"

# Check frontend health
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
echo "Frontend: $FRONTEND_STATUS"

# Combined status
if [ "$BACKEND_STATUS" = "200" ] && [ "$FRONTEND_STATUS" = "200" ]; then
    exit 0
else
    exit 1
fi
EOF

chmod +x /home/walland/Downloads/Video-Genius/scripts/health-check.sh

# Run health check
/home/walland/Downloads/Video-Genius/scripts/health-check.sh
```

### Setup Cron Jobs

```bash
# Edit crontab
sudo crontab -e

# Add health check (every 5 minutes)
*/5 * * * * /home/walland/Downloads/Video-Genius/scripts/health-check.sh >> /var/log/video-genius-health.log 2>&1

# Add log cleanup (daily at 2 AM)
0 2 * * * journalctl --vacuum-time=7d
```

---

## 🧪 Testing

### Manual Service Test

```bash
# Start backend service
sudo systemctl start video-genius-backend

# Wait 3 seconds
sleep 3

# Test API
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","message":"Server is running",...}
```

### Load Test

```bash
# Install Apache Bench
sudo apt-get install -y apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/health

# Expected: No errors, response time < 100ms
```

### Process Monitoring

```bash
# Watch service in real-time
watch -n 1 'sudo systemctl status video-genius-backend | head -10'

# Monitor logs
tail -f <(sudo journalctl -u video-genius-backend -f)
```

---

## 📊 Systemd Features Used

### Restart Policies

```ini
# Restart on failure (up to 3 times in 60 seconds)
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
```

### Resource Limits

```ini
# File descriptors (65536 = maximum safe value)
LimitNOFILE=65536

# Process limit
LimitNPROC=65536
```

### Security

```ini
# No new privileges
NoNewPrivileges=true

# Read-only system directories
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true

# Specific read-write paths
ReadWritePaths=/home/walland/Downloads/Video-Genius
```

### Logging

```ini
# Send to journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=video-genius-api
```

---

## 🎯 Complete Setup Script

```bash
#!/bin/bash
# Complete systemd setup script

echo "🔧 Setting up Video Genius systemd services..."

# 1. Copy service files
echo "1. Installing service files..."
sudo cp /home/walland/Downloads/Video-Genius/systemd/video-genius-backend.service /etc/systemd/system/
sudo cp /home/walland/Downloads/Video-Genius/systemd/video-genius-frontend.service /etc/systemd/system/

# 2. Reload daemon
echo "2. Reloading systemd daemon..."
sudo systemctl daemon-reload

# 3. Verify configuration
echo "3. Verifying service configuration..."
sudo systemd-analyze verify video-genius-backend.service
sudo systemd-analyze verify video-genius-frontend.service

# 4. Enable services
echo "4. Enabling services..."
sudo systemctl enable video-genius-backend.service
sudo systemctl enable video-genius-frontend.service

# 5. Start services
echo "5. Starting services..."
sudo systemctl start video-genius-backend.service
sudo systemctl start video-genius-frontend.service

# 6. Check status
echo "6. Checking service status..."
sudo systemctl status video-genius-backend.service
sudo systemctl status video-genius-frontend.service

echo "✅ Setup complete!"
echo ""
echo "To view logs:"
echo "  Backend:  sudo journalctl -u video-genius-backend -f"
echo "  Frontend: sudo journalctl -u video-genius-frontend -f"
```

---

## ✅ Verification Checklist

- [ ] Service files copied to `/etc/systemd/system/`
- [ ] Systemd daemon reloaded
- [ ] Service configuration verified
- [ ] Services enabled for boot
- [ ] Services started successfully
- [ ] Logs show no errors
- [ ] Health check passing
- [ ] Load test successful
- [ ] Resource usage normal
- [ ] File permissions correct

---

## 🚀 What's Next

1. ✅ Execute database migration
2. ✅ Deploy to Cloud Run (production)
3. ✅ Configure DNS pointing to services
4. ✅ Test end-to-end
5. ✅ Monitor 24/7

---

## 📚 Additional Resources

- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Uvicorn with Systemd](https://www.uvicorn.org/#running-with-systemd)
- [Security Hardening](https://wiki.ubuntu.com/Security/Hardening)

---

**Status**: Ready to Install ✅  
**Last Updated**: 18 de outubro de 2025
