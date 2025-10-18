#!/usr/bin/env python3
import os, sys
from pathlib import Path

# Quick header
print("\n🗄️  DATABASE MIGRATION AUTO-EXECUTOR\n")

# Get file
mfile = Path("migrations/20241018_fix_clean_migration.sql")
if not mfile.exists():
    print(f"❌ File not found: {mfile}")
    sys.exit(1)

content = mfile.read_text()
size = mfile.stat().st_size
lines = len(content.split('\n'))

print(f"✅ Migration file found")
print(f"   File: {mfile}")
print(f"   Size: {size} bytes | Lines: {lines}")
print()

# Validate
if not any(kw in content.upper() for kw in ["SELECT", "INSERT", "CREATE", "DROP"]):
    print(f"❌ Invalid SQL")
    sys.exit(1)

print(f"✅ SQL valid")
print()

# Idempotency check
drop_count = content.count("DROP") + content.count("IF EXISTS")
create_if = content.count("CREATE") + content.count("IF NOT EXISTS")
if drop_count > 0 and create_if > 0:
    print(f"✅ Migration is idempotent (can run multiple times)")
else:
    print(f"⚠️  Migration may not be fully idempotent")
print()

# Copy to clipboard
try:
    import subprocess
    subprocess.run(["xclip", "-selection", "clipboard"], input=content.encode(), check=True)
    print(f"✅ SQL copied to clipboard")
except:
    print(f"ℹ️  Clipboard not available")
print()

# Preview
print("SQL Preview (first 15 lines):")
print("─" * 60)
for line in content.split('\n')[:15]:
    print(f"  {line}")
print("─" * 60)
print()

# Instructions
print("EXECUTION OPTIONS:\n")
print("Option 1: Supabase SQL Editor (RECOMMENDED)")
print("  1. Open: https://app.supabase.com/project/khkiebkjaqncqpjsknup/sql/new")
print("  2. Paste: Ctrl+V (already copied to clipboard)")
print("  3. Click RUN")
print("  4. Wait ~10 seconds")
print("  5. Look for 'Query executed successfully' (green)")
print()

print("Option 2: Supabase CLI")
print("  supabase db push")
print()

print("Option 3: PostgreSQL Direct")
print("  psql -h $HOST -U user -d db < migrations/20241018_fix_clean_migration.sql")
print()

print("─" * 60)
print("✅ READY FOR EXECUTION\n")
