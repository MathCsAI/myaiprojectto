#!/bin/bash

# Quick demo script for LLM Code Deployment System
# This demonstrates the basic workflow

echo "🚀 LLM Code Deployment System - Demo"
echo "===================================="
echo ""

# Check if setup has been run
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "1️⃣  Checking system configuration..."
python -c "from config.config import config; print('✓ Configuration loaded')" 2>/dev/null || {
    echo "❌ Configuration error. Please check config/.env"
    exit 1
}

echo ""
echo "2️⃣  Testing database connection..."
python -c "from database.db import init_db; init_db(); print('✓ Database initialized')"

echo ""
echo "3️⃣  Testing LLM connection..."
python -c "from utils.llm_client import llm_client; print('✓ LLM client ready')" 2>/dev/null || {
    echo "⚠️  LLM client not configured (set LLM_API_KEY in .env)"
}

echo ""
echo "4️⃣  Testing GitHub connection..."
python -c "from utils.github_helper import github_helper; print('✓ GitHub connected')" 2>/dev/null || {
    echo "⚠️  GitHub not configured (set GITHUB_TOKEN in .env)"
}

echo ""
echo "5️⃣  Loading task templates..."
python -c "from templates.task_loader import task_loader; print(f'✓ Loaded {len(task_loader.templates)} templates')"

echo ""
echo "✅ Demo complete!"
echo ""
echo "Next steps:"
echo "  • Start the application: python app.py"
echo "  • Open dashboard: http://localhost:7860/dashboard"
echo "  • Run full tests: python test_system.py"
echo "  • Send tasks: python scripts/round1.py submissions.csv"
echo ""
