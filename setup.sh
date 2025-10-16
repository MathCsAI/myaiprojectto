#!/bin/bash

# Setup script for LLM Code Deployment System

echo "🚀 Setting up LLM Code Deployment System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Copy example env file
if [ ! -f config/.env ]; then
    echo "Creating .env file from example..."
    cp config/.env.example config/.env
    echo "⚠️  Please edit config/.env with your API keys and tokens"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data

# Initialize database (SQLite for development)
echo "Initializing database..."
export DATABASE_URL="sqlite:///./data/llm_deployment.db"
python -c "from database.db import init_db; init_db(); print('✓ Database initialized')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/.env with your API keys:"
echo "   - GITHUB_TOKEN: Your GitHub Personal Access Token"
echo "   - GITHUB_USERNAME: Your GitHub username"
echo "   - LLM_API_KEY: Your LLM API key (OpenAI, Anthropic, etc.)"
echo ""
echo "2. Start the application:"
echo "   python app.py"
echo ""
echo "3. Access the dashboard:"
echo "   http://localhost:7860/dashboard"
echo ""
