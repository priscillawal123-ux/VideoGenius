# GitHub Copilot Instructions - Video Genius Project

## 🎯 PRIMARY OBJECTIVE

**EXECUTE FIRST, EXPLAIN LATER.** Generate precise, production-ready CLI commands and code. No documentation, no step-by-step guides, no markdown files unless explicitly requested.

**🚨 MANDATORY: CLI FIRST FOR ALL AUTOMATABLE TASKS**

When user asks for ANY task that can be automated:
1. **≤3 CLI commands?** → Execute immediately via terminal
2. **Requires custom code?** → Generate production code only
3. **Task involves both?** → Execute CLI first, then generate code

**DO NOT CREATE:**
- Step-by-step guides (unless explicitly asked)
- Markdown documentation (unless explicitly asked)
- Visual instructions or diagrams
- Troubleshooting guides
- Implementation roadmaps
- Checklists or progress tracking

**DO CREATE:**
- Direct CLI commands (execute via terminal)
- Production-ready Python/JavaScript code
- Database migrations (execute immediately)
- Configuration files (copy & run)
- Automated scripts (bash/python)

---

## 📋 PROJECT CONTEXT

### Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await patterns)
- **Cloud**: Google Cloud Platform (Vertex AI, BigQuery, Cloud Run, Cloud Storage)
- **GCP Project**: `video-genius-prod-v1` (Project ID: 752423186317)
- **Containerization**: Docker (multi-stage builds)
- **Version Control**: Git + GitHub CLI (gh)
- **Testing**: Pytest with coverage
- **Linting**: Ruff + MyPy + Black

### Project Structure

```
video-genius/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── services/         # Business logic (Vertex AI, video processing)
│   ├── models/           # Pydantic models
│   ├── database/         # BigQuery client & queries
│   └── storage/          # Cloud Storage operations
├── tests/                # Test suite
├── scripts/              # Automation scripts
└── .github/              # GitHub workflows & configs
```

### When to Choose CLI Over Code Generation

**ALWAYS choose CLI for:**
- Repository management (clone, branch, commit, push, pull request)
- Package installation and dependency management
- Running tests, linters, formatters (pytest, ruff, black)
- Deployment operations (gcloud, docker, systemctl)
- Secrets & environment configuration (gh secret set, gcloud secrets)
- Database migrations execution (psql, supabase cli)
- CI/CD pipeline operations (gh workflow run)
- Git operations (git commit, git push, git merge)

**ONLY generate code for:**
- Business logic and algorithms
- API endpoints and handlers
- Data models and schemas
- Custom services and utilities

**DO NOT create:**
- Implementation guides or step-by-step instructions
- Documentation files (README, guides, checklists)
- Roadmaps or progress tracking
- Architecture diagrams or visual guides
- Troubleshooting guides or FAQs

---

## 🔧 GITHUB CLI (gh) - COMPLETE COMMAND REFERENCE

### Authentication & Configuration

```bash
# Authentication
gh auth login                           # Interactive login
gh auth logout                          # Logout
gh auth refresh -s <scopes>            # Refresh with additional scopes (e.g., copilot, workflow)
gh auth status                          # Check authentication status
gh auth token                           # Get auth token

# Configuration
gh config set editor <editor>           # Set default editor (vim, code, nano)
gh config set git_protocol <protocol>   # Set protocol (https, ssh)
gh config get <key>                     # Get config value
gh config list                          # List all configurations
```

### Repository Operations

```bash
# Repository Management
gh repo create <name> --public|--private    # Create new repository
gh repo clone <repo>                        # Clone repository
gh repo fork <repo>                         # Fork repository
gh repo view [repo]                         # View repository details
gh repo delete <repo> --yes                 # Delete repository
gh repo sync                                # Sync fork with upstream
gh repo set-default                         # Set default repo for commands

# Repository Settings
gh repo edit --description "desc"           # Update description
gh repo edit --homepage "url"               # Set homepage
gh repo edit --visibility <public|private>  # Change visibility
gh repo archive                             # Archive repository
gh repo unarchive                           # Unarchive repository
```

### Issues Management

```bash
# Creating & Viewing
gh issue create --title "title" --body "body"     # Create issue
gh issue create --title "title" --web             # Create in browser
gh issue list --state <open|closed|all>           # List issues
gh issue list --assignee @me                      # My assigned issues
gh issue list --label "bug,priority"              # Filter by labels
gh issue view <number>                            # View issue details
gh issue view <number> --web                      # Open in browser

# Managing Issues
gh issue edit <number> --add-label "label"        # Add label
gh issue edit <number> --remove-label "label"     # Remove label
gh issue edit <number> --add-assignee @user       # Assign user
gh issue edit <number> --add-project "project"    # Add to project
gh issue close <number>                           # Close issue
gh issue reopen <number>                          # Reopen issue
gh issue pin <number>                             # Pin issue
gh issue unpin <number>                           # Unpin issue
gh issue delete <number>                          # Delete issue

# Commenting
gh issue comment <number> --body "comment"        # Add comment
gh issue comment <number> --edit                  # Edit last comment

# Development
gh issue develop <number> --checkout              # Create branch from issue
gh issue develop <number> --base main             # Specify base branch
```

### Pull Requests

```bash
# Creating PRs
gh pr create --title "title" --body "body"        # Create PR
gh pr create --fill                               # Auto-fill from commits
gh pr create --draft                              # Create draft PR
gh pr create --web                                # Create in browser
gh pr create --base <branch> --head <branch>      # Specify branches

# Listing & Viewing
gh pr list --state <open|closed|merged|all>       # List PRs
gh pr list --author @me                           # My PRs
gh pr list --assignee @me                         # Assigned to me
gh pr list --label "bug"                          # Filter by label
gh pr view <number>                               # View PR details
gh pr view <number> --web                         # Open in browser
gh pr diff <number>                               # View diff
gh pr status                                      # Status of relevant PRs

# Managing PRs
gh pr checkout <number>                           # Checkout PR branch
gh pr edit <number> --add-label "label"           # Add label
gh pr edit <number> --add-reviewer @user          # Add reviewer
gh pr edit <number> --milestone "milestone"       # Set milestone
gh pr ready <number>                              # Mark draft as ready
gh pr close <number>                              # Close PR
gh pr reopen <number>                             # Reopen PR

# Reviews
gh pr review <number> --approve                   # Approve PR
gh pr review <number> --request-changes           # Request changes
gh pr review <number> --comment --body "text"     # Comment review
gh pr comment <number> --body "comment"           # Add comment

# Merging
gh pr merge <number> --merge                      # Merge commit
gh pr merge <number> --squash                     # Squash merge
gh pr merge <number> --rebase                     # Rebase merge
gh pr merge <number> --auto                       # Auto-merge when ready
gh pr merge <number> --delete-branch              # Delete branch after merge

# Checks & CI
gh pr checks <number>                             # View CI status
gh pr checks <number> --watch                     # Watch CI in real-time
```

### Workflows & Actions

```bash
# Workflows
gh workflow list                                  # List workflows
gh workflow view <workflow>                       # View workflow details
gh workflow run <workflow>                        # Trigger workflow
gh workflow run <workflow> --ref <branch>         # Run on specific branch
gh workflow enable <workflow>                     # Enable workflow
gh workflow disable <workflow>                    # Disable workflow

# Runs
gh run list                                       # List workflow runs
gh run list --workflow <workflow>                 # Filter by workflow
gh run view <run-id>                              # View run details
gh run watch <run-id>                             # Watch run in real-time
gh run download <run-id>                          # Download artifacts
gh run rerun <run-id>                             # Rerun workflow
gh run rerun <run-id> --failed                    # Rerun only failed jobs
gh run cancel <run-id>                            # Cancel run
gh run delete <run-id>                            # Delete run
```

### Secrets & Variables

```bash
# Repository Secrets
gh secret list                                    # List secrets
gh secret set <name> < secret.txt                 # Set from file
gh secret set <name> --body "value"               # Set directly
gh secret delete <name>                           # Delete secret

# Repository Variables
gh variable list                                  # List variables
gh variable set <name> --body "value"             # Set variable
gh variable delete <name>                         # Delete variable

# Organization & Environment
gh secret set <name> --org <org>                  # Org-level secret
gh secret set <name> --env <environment>          # Environment secret
gh variable set <name> --env <environment>        # Environment variable
```

### Releases

```bash
# Creating Releases
gh release create <tag> --title "title"           # Create release
gh release create <tag> --notes "notes"           # With release notes
gh release create <tag> --generate-notes          # Auto-generate notes
gh release create <tag> <files>                   # With assets
gh release create <tag> --draft                   # Create draft
gh release create <tag> --prerelease              # Mark as prerelease

# Managing Releases
gh release list                                   # List releases
gh release view <tag>                             # View release
gh release edit <tag> --notes "new notes"         # Edit release
gh release delete <tag> --yes                     # Delete release
gh release download <tag>                         # Download assets
gh release upload <tag> <files>                   # Upload assets
```

### Search

```bash
# Search Repositories
gh search repos <query>                           # Search repos
gh search repos <query> --language python         # Filter by language
gh search repos <query> --stars ">1000"          # Filter by stars
gh search repos <query> --topic "machine-learning" # By topic

# Search Issues & PRs
gh search issues <query>                          # Search issues
gh search issues <query> --state open             # Open issues only
gh search issues <query> --label bug              # By label
gh search prs <query>                             # Search PRs
gh search prs <query> --review-requested @me      # PRs needing review

# Search Code
gh search code <query>                            # Search code
gh search code <query> --language python          # In Python files
gh search code <query> --repo owner/repo          # In specific repo
```

### Labels & Projects

```bash
# Labels
gh label list                                     # List labels
gh label create <name> --color <hex>              # Create label
gh label create <name> --description "desc"       # With description
gh label edit <name> --color <hex>                # Edit label
gh label delete <name>                            # Delete label
gh label clone <source-repo>                      # Clone from repo

# Projects
gh project list --owner <owner>                   # List projects
gh project view <number>                          # View project
gh project create --title "title"                 # Create project
gh project close <number>                         # Close project
gh project field-list <number>                    # List fields
```

### Aliases

```bash
# Manage Aliases
gh alias list                                     # List aliases
gh alias set <alias> <expansion>                  # Create alias
gh alias set prc 'pr create --fill'              # Example alias
gh alias delete <alias>                           # Delete alias

# Useful Alias Examples
gh alias set co 'pr checkout'                     # Checkout PR
gh alias set bugs 'issue list --label bug'        # List bugs
gh alias set work 'issue list --assignee @me'     # My work
gh alias set ci 'pr checks'                       # Check CI
```

### Extensions

```bash
# Extension Management
gh extension list                                 # List installed
gh extension install <repo>                       # Install extension
gh extension upgrade <extension>                  # Upgrade extension
gh extension upgrade --all                        # Upgrade all
gh extension remove <extension>                   # Remove extension

# Essential Extensions
gh extension install github/gh-copilot            # Copilot CLI
gh extension install dlvhdr/gh-dash               # Dashboard
gh extension install seachicken/gh-poi            # Clean branches
gh extension install mislav/gh-branch             # Branch utils
```

### Copilot CLI (Extension)

```bash
# Command Suggestions
gh copilot suggest                                # Interactive suggest
gh copilot suggest -t shell "description"         # Shell command
gh copilot suggest -t git "description"           # Git command
gh copilot suggest -t gh "description"            # GH CLI command

# Command Explanations
gh copilot explain "<command>"                    # Explain command
gh copilot explain "docker run -d nginx"          # Example

# Examples
gh copilot suggest -t git "undo last commit"
gh copilot suggest -t gh "create pr from current branch"
gh copilot suggest -t shell "find large files"
gh copilot explain "kubectl get pods -A"
```

### API & Advanced

```bash
# Direct API Access
gh api <endpoint>                                 # GET request
gh api <endpoint> -X POST                         # POST request
gh api <endpoint> --method DELETE                 # DELETE request
gh api <endpoint> --field key=value               # With parameters
gh api <endpoint> --jq '.items[]'                 # Filter with jq

# Pagination
gh api --paginate <endpoint>                      # Auto-paginate

# Examples
gh api repos/:owner/:repo                         # Repo info
gh api /user                                      # Current user
gh api /rate_limit                                # Rate limit status
```

### Miscellaneous

```bash
# Browse
gh browse                                         # Open repo in browser
gh browse --branch <branch>                       # Open branch
gh browse --settings                              # Repo settings
gh browse <issue-number>                          # Open issue/PR

# Status
gh status                                         # Activity summary
gh status --exclude <types>                       # Exclude types

# GPG & SSH Keys
gh gpg-key list                                   # List GPG keys
gh gpg-key add <file>                             # Add GPG key
gh ssh-key list                                   # List SSH keys
gh ssh-key add <file>                             # Add SSH key

# Gists
gh gist create <file>                             # Create gist
gh gist create --public <file>                    # Public gist
gh gist list                                      # List gists
gh gist view <gist-id>                            # View gist
gh gist edit <gist-id>                            # Edit gist
gh gist delete <gist-id>                          # Delete gist

# Completion
gh completion -s bash                             # Bash completion
gh completion -s zsh                              # Zsh completion
gh completion -s fish                             # Fish completion
```

---

## 💻 CODE GENERATION RULES (When Code is Needed)

**ONLY generate code when CLI cannot handle the task.**

### Python Standards (MANDATORY)

1. **Complete, working code only** - No placeholders, no TODO
2. **Type hints** - ALL functions must have type hints (PEP 484)
3. **Async/await** - Required for I/O operations
4. **Error handling** - Specific exceptions only, never bare `except:`
5. **Docstrings** - Google style for all functions/classes
6. **PEP 8** - Max 88 characters per line (Black default)

---

## 🚀 EXECUTION CHECKLIST

Before responding to user:

- [ ] Is this a CLI/automation task? → Execute via terminal immediately
- [ ] Should I generate code? → Only if CLI cannot solve it
- [ ] Will I create documentation? → NO (unless explicitly asked)
- [ ] Is code production-ready? → YES (complete, no placeholders)
- [ ] Do I have type hints? → YES (all functions)
- [ ] Do I have error handling? → YES (specific exceptions only)

---

## ⚡ QUICK REFERENCE

**Terminal automation tools for this project:**
- `gh` - GitHub CLI for repository operations
- `gcloud` - Google Cloud operations
- `supabase` - Database migrations and management
- `docker` - Container operations
- `python -m pytest` - Run tests
- `black`, `ruff` - Code formatting and linting

**DO NOT create guides, docs, or step-by-step instructions.**
**ONLY create: CLI commands or production code.**

---

## 🗄️ DATABASE AUTOMATION RULES

### Supabase PostgreSQL Connection Details

**Video Genius Production Database:**
```
Host: db.khkiebkjaqncqpjsknup.supabase.co
Port: 5432
Database: postgres
Username: postgres
Password: Walepri123!

Direct Connection Command:
psql -h db.khkiebkjaqncqpjsknup.supabase.co -p 5432 -d postgres -U postgres
```

### When User Asks to Create/Execute Database Tables

**ALWAYS follow this pattern:**

1. **Generate the SQL migration file** (production-ready, idempotent)
   - Use `DROP IF EXISTS` for safe recreation
   - Use `CREATE TABLE IF NOT EXISTS` 
   - Include indexes, constraints, RLS policies
   - Add sample data for testing
   - Add verification queries at the end

2. **Execute immediately via CLI (NO SCRIPTS - Direct Commands):**
   ```bash
   # DIRECT PostgreSQL execution (RECOMMENDED - Fastest)
   PGPASSWORD="Walepri123!" psql -h db.khkiebkjaqncqpjsknup.supabase.co -p 5432 -d postgres -U postgres -f migrations/YYYYMMDD_name.sql
   
   # OR Execute individual commands directly in terminal:
   PGPASSWORD="Walepri123!" psql -h db.khkiebkjaqncqpjsknup.supabase.co -p 5432 -d postgres -U postgres << 'EOF'
   DROP TABLE IF EXISTS table_name CASCADE;
   CREATE TABLE table_name (...);
   INSERT INTO table_name VALUES (...);
   SELECT COUNT(*) FROM table_name;
   EOF
   
   # OR For Supabase CLI (if installed)
   supabase db push
   
   # OR Manual: Copy SQL and paste in Supabase SQL Editor
   cat migrations/YYYYMMDD_table_name.sql
   ```

3. **Verify execution:**
   ```bash
   # Check table exists
   PGPASSWORD="Walepri123!" psql -h db.khkiebkjaqncqpjsknup.supabase.co -p 5432 -d postgres -U postgres -c "SELECT * FROM information_schema.tables WHERE table_name='table_name';"
   
   # Check data count
   PGPASSWORD="Walepri123!" psql -h db.khkiebkjaqncqpjsknup.supabase.co -p 5432 -d postgres -U postgres -c "SELECT COUNT(*) FROM table_name;"
   ```

### Migration File Standards

**MANDATORY requirements for all migration files:**

1. **Idempotent** - Can run multiple times without errors
   ```sql
   DROP TABLE IF EXISTS video_tasks CASCADE;
   CREATE TABLE IF NOT EXISTS video_tasks (...)
   ```

2. **Complete** - Include all objects
   - ENUM types (if needed)
   - Tables with constraints
   - Indexes (≥3 for performance)
   - RLS policies
   - Triggers/functions
   - Views (for analytics)
   - Sample data (≥5 records)

3. **Verified** - Include verification queries at end
   ```sql
   -- Verify
   SELECT COUNT(*) FROM table_name;
   SELECT typname FROM pg_type WHERE typtype='e';
   ```

4. **Named properly** - `YYYYMMDD_purpose.sql`
   ```
   ✓ 20241018_create_video_tasks.sql
   ✓ 20241018_fix_clean_migration.sql
   ✗ migration.sql (too generic)
   ✗ createTable.sql (wrong format)
   ```

### Auto-Execution Pattern

When user says "create table X" or "execute migration":

```bash
# STEP 1: Create migration file (cat it to show content)
cat << 'EOF' > migrations/YYYYMMDD_name.sql
DROP TABLE IF EXISTS ... CASCADE;
CREATE TYPE ... AS ENUM (...);
CREATE TABLE ... (...);
CREATE INDEX ... ;
INSERT INTO ... VALUES (...);
SELECT COUNT(*) FROM ...;
EOF

# STEP 2: Execute immediately (choose one method)
# Option A: Supabase CLI
supabase db push

# Option B: Direct PostgreSQL
psql -h $SUPABASE_HOST -U postgres -d postgres < migrations/YYYYMMDD_name.sql

# Option C: Show for manual Supabase SQL Editor
cat migrations/YYYYMMDD_name.sql | xclip -selection clipboard

# STEP 3: Verify
supabase db query "SELECT * FROM information_schema.tables WHERE table_name='new_table';"
```

### Database Operations Quick Matrix

| Operation | CLI Command | Idempotent? |
|-----------|-------------|------------|
| Create table | `supabase db push` | ✓ (use IF NOT EXISTS) |
| Drop table | `supabase db query "DROP TABLE IF EXISTS..."` | ✓ |
| Add column | `supabase db push` | ✓ (use IF NOT EXISTS) |
| Create index | `supabase db push` | ✓ (use IF NOT EXISTS) |
| Insert data | `supabase db query "INSERT INTO..."` | ✗ (use ON CONFLICT for upsert) |
| Run migration | `supabase db push` | ✓ (must be idempotent) |

---
        
```

---

## 🎯 UPDATED DECISION FRAMEWORK

### Complete Priority Chain

1. **CLI**: Repository management, CI/CD, environment setup, simple GCP config
---

## 📋 QUICK EXECUTION MATRIX

| Task | Tool | Example |
|------|------|---------|
| Create feature branch | CLI | `gh issue develop 42 --checkout` |
| Run tests | CLI | `pytest tests/ -v` |
| Deploy to Cloud Run | CLI | `gcloud run deploy video-genius` |
| Set secrets | CLI | `gh secret set GOOGLE_KEY --body "..."` |
| Run database migration | CLI | `supabase db push` OR `psql -f migration.sql` |
| Create API endpoint | CODE | Generate FastAPI route with validation |
| Implement service | CODE | Generate Python class with business logic |
| Fix database error | CLI then CODE | Execute fix SQL, then implement handler |

---
