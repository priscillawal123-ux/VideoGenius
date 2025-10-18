#!/bin/bash
# ============================================================================
# Complete Video Genius Systemd Setup Script
# ============================================================================
# This script sets up Video Genius to run 24/7 via systemd
# Run with: sudo bash install-systemd.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
PROJECT_DIR="/home/walland/Downloads/Video-Genius"
SYSTEMD_DIR="/etc/systemd/system"

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_step() {
    echo -e "${YELLOW}▸ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# Main Setup
# ============================================================================

print_header "🔧 VIDEO GENIUS SYSTEMD SETUP"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_step "Checking prerequisites..."

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi
print_success "Project directory exists"

# Check if www-data user exists
if ! id -u www-data > /dev/null 2>&1; then
    print_step "Creating www-data user..."
    useradd -r -s /bin/false www-data
    print_success "www-data user created"
else
    print_success "www-data user exists"
fi

# ============================================================================
# Step 1: Copy Service Files
# ============================================================================

print_header "📋 STEP 1: Installing Service Files"

if [ -f "$PROJECT_DIR/systemd/video-genius-backend.service" ]; then
    print_step "Copying backend service..."
    cp "$PROJECT_DIR/systemd/video-genius-backend.service" "$SYSTEMD_DIR/"
    print_success "Backend service installed"
else
    print_error "Backend service file not found"
    exit 1
fi

if [ -f "$PROJECT_DIR/systemd/video-genius-frontend.service" ]; then
    print_step "Copying frontend service..."
    cp "$PROJECT_DIR/systemd/video-genius-frontend.service" "$SYSTEMD_DIR/"
    print_success "Frontend service installed"
else
    print_error "Frontend service file not found"
    exit 1
fi

# ============================================================================
# Step 2: Set File Permissions
# ============================================================================

print_header "🔐 STEP 2: Setting File Permissions"

print_step "Setting project directory ownership to www-data..."
chown -R www-data:www-data "$PROJECT_DIR"
print_success "Ownership set"

print_step "Setting directory permissions (755)..."
chmod 755 "$PROJECT_DIR"
print_success "Permissions set"

print_step "Setting executable permissions for scripts..."
chmod 755 "$PROJECT_DIR/scripts"/*.sh 2>/dev/null || true
print_success "Script permissions set"

# ============================================================================
# Step 3: Create Environment File
# ============================================================================

print_header "⚙️  STEP 3: Creating Environment File"

ENV_FILE="$PROJECT_DIR/.env.production"

if [ -f "$ENV_FILE" ]; then
    print_step ".env.production already exists"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_step "Skipping environment file creation"
    else
        cat > "$ENV_FILE" << 'ENVEOF'
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
ENVEOF
        print_success "Environment file created"
    fi
else
    print_step "Creating .env.production..."
    cat > "$ENV_FILE" << 'ENVEOF'
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
ENVEOF
    print_success "Environment file created"
fi

chmod 600 "$ENV_FILE"
chown www-data:www-data "$ENV_FILE"
print_success "Environment file permissions set"

# ============================================================================
# Step 4: Reload Systemd
# ============================================================================

print_header "🔄 STEP 4: Reloading Systemd"

print_step "Reloading systemd daemon..."
systemctl daemon-reload
print_success "Daemon reloaded"

# ============================================================================
# Step 5: Verify Configuration
# ============================================================================

print_header "✅ STEP 5: Verifying Configuration"

print_step "Verifying backend service..."
if systemd-analyze verify video-genius-backend.service; then
    print_success "Backend service configuration valid"
else
    print_error "Backend service configuration invalid"
    exit 1
fi

print_step "Verifying frontend service..."
if systemd-analyze verify video-genius-frontend.service; then
    print_success "Frontend service configuration valid"
else
    print_error "Frontend service configuration invalid"
    exit 1
fi

# ============================================================================
# Step 6: Enable Services
# ============================================================================

print_header "🚀 STEP 6: Enabling Services"

print_step "Enabling backend service..."
systemctl enable video-genius-backend.service
print_success "Backend service enabled"

print_step "Enabling frontend service..."
systemctl enable video-genius-frontend.service
print_success "Frontend service enabled"

# ============================================================================
# Step 7: Start Services
# ============================================================================

print_header "▶️  STEP 7: Starting Services"

print_step "Starting backend service..."
if systemctl start video-genius-backend.service; then
    print_success "Backend service started"
    sleep 2
else
    print_error "Failed to start backend service"
    systemctl status video-genius-backend.service
    exit 1
fi

print_step "Starting frontend service..."
if systemctl start video-genius-frontend.service; then
    print_success "Frontend service started"
    sleep 2
else
    print_error "Failed to start frontend service"
    systemctl status video-genius-frontend.service
    exit 1
fi

# ============================================================================
# Step 8: Verify Services Running
# ============================================================================

print_header "🔍 STEP 8: Verifying Services"

print_step "Checking backend service status..."
if systemctl is-active --quiet video-genius-backend.service; then
    print_success "Backend service is running"
else
    print_error "Backend service is not running"
    systemctl status video-genius-backend.service
fi

print_step "Checking frontend service status..."
if systemctl is-active --quiet video-genius-frontend.service; then
    print_success "Frontend service is running"
else
    print_error "Frontend service is not running"
    systemctl status video-genius-frontend.service
fi

# ============================================================================
# Step 9: Test Endpoints
# ============================================================================

print_header "🧪 STEP 9: Testing Endpoints"

print_step "Waiting for services to be ready..."
sleep 3

print_step "Testing backend health check..."
if RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null); then
    if echo "$RESPONSE" | grep -q '"status":"healthy"'; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed: $RESPONSE"
    fi
else
    print_error "Could not reach backend"
fi

# ============================================================================
# Summary
# ============================================================================

print_header "📊 SETUP SUMMARY"

echo ""
echo "✅ Services installed and running:"
echo "   - video-genius-backend.service"
echo "   - video-genius-frontend.service"
echo ""
echo "📍 Service locations:"
echo "   - $SYSTEMD_DIR/video-genius-backend.service"
echo "   - $SYSTEMD_DIR/video-genius-frontend.service"
echo ""
echo "📝 Environment file:"
echo "   - $ENV_FILE"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env.production with actual secrets:"
echo "      sudo nano $ENV_FILE"
echo "   2. View backend logs:"
echo "      sudo journalctl -u video-genius-backend -f"
echo "   3. View frontend logs:"
echo "      sudo journalctl -u video-genius-frontend -f"
echo "   4. Restart services:"
echo "      sudo systemctl restart video-genius-backend video-genius-frontend"
echo ""
echo "🔗 Useful commands:"
echo "   Status:   sudo systemctl status video-genius-backend"
echo "   Logs:     sudo journalctl -u video-genius-backend -f"
echo "   Stop:     sudo systemctl stop video-genius-backend"
echo "   Restart:  sudo systemctl restart video-genius-backend"
echo ""
echo -e "${GREEN}✅ SYSTEMD SETUP COMPLETE!${NC}"
echo ""
