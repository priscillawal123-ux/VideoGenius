#!/bin/bash
# ============================================================================
# Phase 3: GitHub Integration Test Suite
# ============================================================================
# Tests for GitHub sync service and webhook handler
# Run with: bash scripts/test_phase3.sh

# Allow errors - we handle them in tests
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
SKIPPED=0

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

test_start() {
    echo -n "  ▸ $1 ... "
}

test_pass() {
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

test_skip() {
    echo -e "${YELLOW}⏭️  SKIP${NC}: $1"
    ((SKIPPED++))
}

# ============================================================================
# Phase 3 Tests
# ============================================================================

print_header "🧪 PHASE 3: GitHub Integration Test Suite"

# Test 1: Check GitHub Sync Service exists
print_header "TEST 1: GitHub Sync Service"

test_start "GitHub sync service file exists"
if [ -f "backend/services/github_sync.py" ]; then
    test_pass
else
    test_fail "github_sync.py not found"
fi

test_start "GitHubSyncService class defined"
if grep -q "class GitHubSyncService" backend/services/github_sync.py; then
    test_pass
else
    test_fail "GitHubSyncService class not found"
fi

test_start "sync_issues_to_tasks method exists"
if grep -q "async def sync_issues_to_tasks" backend/services/github_sync.py; then
    test_pass
else
    test_fail "sync_issues_to_tasks method not found"
fi

test_start "create_issue_from_task method exists"
if grep -q "async def create_issue_from_task" backend/services/github_sync.py; then
    test_pass
else
    test_fail "create_issue_from_task method not found"
fi

test_start "update_issue_from_task method exists"
if grep -q "async def update_issue_from_task" backend/services/github_sync.py; then
    test_pass
else
    test_fail "update_issue_from_task method not found"
fi

# Test 2: Check Webhook Handler
print_header "TEST 2: Webhook Handler"

test_start "Webhook routes file exists"
if [ -f "backend/api/routes/webhooks.py" ]; then
    test_pass
else
    test_fail "webhooks.py not found"
fi

test_start "GitHub webhook endpoint defined"
if grep -q "POST /api/v1/webhooks/github" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "GitHub webhook endpoint not found"
fi

test_start "Signature verification function exists"
if grep -q "def verify_github_webhook" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "verify_github_webhook function not found"
fi

test_start "Issue event handler exists"
if grep -q "async def _handle_issue_event" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "Issue event handler not found"
fi

test_start "Comment event handler exists"
if grep -q "async def _handle_comment_event" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "Comment event handler not found"
fi

# Test 3: Check API Integration
print_header "TEST 3: API Integration"

test_start "Webhooks router imported in main.py"
if grep -q "from backend.api.routes.webhooks import router as webhooks_router" backend/api/main.py; then
    test_pass
else
    test_fail "webhooks_router import not found"
fi

test_start "Webhooks router registered in main.py"
if grep -q "app.include_router(webhooks_router" backend/api/main.py; then
    test_pass
else
    test_fail "webhooks_router not registered"
fi

test_start "Tasks router still registered"
if grep -q "app.include_router(tasks_router" backend/api/main.py; then
    test_pass
else
    test_fail "tasks_router registration missing"
fi

# Test 4: Check Pydantic Models
print_header "TEST 4: Data Models"

test_start "GitHubIssue dataclass exists"
if grep -q "class GitHubIssue" backend/services/github_sync.py; then
    test_pass
else
    test_fail "GitHubIssue class not found"
fi

test_start "TaskCreateFromIssueModel exists"
if grep -q "class TaskCreateFromIssueModel" backend/services/github_sync.py; then
    test_pass
else
    test_fail "TaskCreateFromIssueModel not found"
fi

test_start "GitHubWebhookPayload model exists"
if grep -q "class GitHubWebhookPayload" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "GitHubWebhookPayload not found"
fi

# Test 5: Check Label Mappings
print_header "TEST 5: Label Mappings"

test_start "Priority label mappings defined"
if grep -q "PRIORITY_LABELS = {" backend/services/github_sync.py; then
    test_pass
else
    test_fail "Priority mappings not found"
fi

test_start "Phase label mappings defined"
if grep -q "PHASE_LABELS = {" backend/services/github_sync.py; then
    test_pass
else
    test_fail "Phase mappings not found"
fi

test_start "Status label mappings defined"
if grep -q "STATUS_LABELS = {" backend/services/github_sync.py; then
    test_pass
else
    test_fail "Status mappings not found"
fi

# Test 6: Documentation
print_header "TEST 6: Documentation"

test_start "Migration instructions file exists"
if [ -f "MIGRATION_INSTRUCTIONS.md" ]; then
    test_pass
else
    test_fail "MIGRATION_INSTRUCTIONS.md not found"
fi

test_start "Phase 3 documentation exists"
if [ -f "PHASE_3_GITHUB_INTEGRATION.md" ]; then
    test_pass
else
    test_fail "PHASE_3_GITHUB_INTEGRATION.md not found"
fi

test_start "Phase 3 doc has setup instructions"
if grep -q "GitHub Personal Access Token" PHASE_3_GITHUB_INTEGRATION.md; then
    test_pass
else
    test_fail "Setup instructions not found"
fi

test_start "Phase 3 doc has webhook reference"
if grep -q "POST /api/v1/webhooks/github" PHASE_3_GITHUB_INTEGRATION.md; then
    test_pass
else
    test_fail "Webhook reference not found"
fi

# Test 7: Code Quality
print_header "TEST 7: Code Quality"

test_start "GitHub sync has type hints"
if grep -q "-> Dict\|-> str\|-> List\|-> Optional" backend/services/github_sync.py; then
    test_pass
else
    test_fail "Type hints missing"
fi

test_start "Webhook handler has docstrings"
if grep -q '"""' backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "Docstrings missing"
fi

test_start "Logging configured in sync service"
if grep -q "logger = logging.getLogger" backend/services/github_sync.py; then
    test_pass
else
    test_fail "Logging not configured"
fi

test_start "Error handling in webhook"
if grep -q "except Exception\|HTTPException" backend/api/routes/webhooks.py; then
    test_pass
else
    test_fail "Error handling missing"
fi

# Test 8: Python Import Check
print_header "TEST 8: Python Imports"

test_start "Backend app imports successfully"
if python -c "from backend.api.main import app; print('✓ App imported')" 2>/dev/null | grep -q "App imported"; then
    test_pass
else
    test_fail "App import failed"
fi

test_start "GitHub sync module imports"
if python -c "from backend.services.github_sync import GitHubSyncService; print('✓ Imported')" 2>/dev/null | grep -q "Imported"; then
    test_pass
else
    test_fail "GitHub sync import failed - check dependencies"
fi

test_start "Webhook routes import"
if python -c "from backend.api.routes.webhooks import router; print('✓ Imported')" 2>/dev/null | grep -q "Imported"; then
    test_pass
else
    test_fail "Webhook routes import failed"
fi

# Test 9: Line Counts
print_header "TEST 9: Code Statistics"

test_start "GitHub sync service size (200+ lines)"
LINES=$(wc -l < backend/services/github_sync.py)
if [ "$LINES" -gt 200 ]; then
    echo -ne "\n  ▸ Found $LINES lines"
    test_pass
else
    test_fail "GitHub sync too short ($LINES lines)"
fi

test_start "Webhook handler size (150+ lines)"
LINES=$(wc -l < backend/api/routes/webhooks.py)
if [ "$LINES" -gt 150 ]; then
    echo -ne "\n  ▸ Found $LINES lines"
    test_pass
else
    test_fail "Webhook handler too short ($LINES lines)"
fi

test_start "Phase 3 documentation size (500+ lines)"
LINES=$(wc -l < PHASE_3_GITHUB_INTEGRATION.md)
if [ "$LINES" -gt 500 ]; then
    echo -ne "\n  ▸ Found $LINES lines"
    test_pass
else
    test_fail "Documentation too short ($LINES lines)"
fi

# ============================================================================
# Summary
# ============================================================================

print_header "📊 TEST SUMMARY"

TOTAL=$((PASSED + FAILED + SKIPPED))

echo ""
echo -e "  ${GREEN}✅ PASSED: $PASSED${NC}"
echo -e "  ${RED}❌ FAILED: $FAILED${NC}"
echo -e "  ${YELLOW}⏭️  SKIPPED: $SKIPPED${NC}"
echo -e "  📋 TOTAL:  $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Phase 3: GitHub Integration is ready! 🚀"
    echo ""
    echo "Next steps:"
    echo "  1. Set GitHub token: export GITHUB_TOKEN=ghp_xxxx"
    echo "  2. Set webhook secret: export GITHUB_WEBHOOK_SECRET=xxxx"
    echo "  3. Configure GitHub webhook (see PHASE_3_GITHUB_INTEGRATION.md)"
    echo "  4. Test with: curl http://localhost:8000/api/v1/webhooks/github"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
