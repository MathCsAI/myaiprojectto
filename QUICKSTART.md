# Quick Start Guide

This guide will help you get the LLM Code Deployment System up and running quickly.

## Prerequisites

✅ Python 3.9 or higher
✅ Git installed
✅ GitHub account with Personal Access Token
✅ LLM API key (OpenAI or Anthropic)

## 5-Minute Setup

### Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
cd /workspaces/myaiprojectto

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure (2 minutes)

Edit `config/.env`:

```bash
# Required - Get from https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_username

# Required - Get from https://platform.openai.com/api-keys
LLM_API_KEY=sk-your_key_here
LLM_API_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview

# Optional - Use SQLite for testing
DATABASE_URL=sqlite:///./data/llm_deployment.db
```

### Step 3: Run (1 minute)

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python app.py
```

Visit: **http://localhost:7860/dashboard**

## First Task (Testing)

### Create a test submission

Create `submissions.csv`:
```csv
timestamp,email,endpoint,secret
2024-10-16T10:00:00Z,test@example.com,http://localhost:7860/student/api/task,test123
```

### Send a test task

```bash
# Configure student secret first
curl -X POST http://localhost:7860/student/api/secret \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "secret": "test123"}'

# Send Round 1 tasks
python scripts/round1.py submissions.csv
```

### Check results

```bash
# View submissions
curl http://localhost:7860/evaluation/api/submissions/test@example.com

# Run evaluation
python scripts/evaluate.py

# View results
curl http://localhost:7860/evaluation/api/results/test@example.com
```

## Next Steps

- 📖 Read the full [README.md](README.md)
- 🎓 Create custom [task templates](templates/tasks/)
- 🔧 Configure for production deployment
- 📊 Monitor via the [dashboard](http://localhost:7860/dashboard)

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### GitHub API errors
- Verify `GITHUB_TOKEN` is valid
- Check token has `repo` and `delete_repo` scopes

### LLM API errors
- Verify `LLM_API_KEY` is valid
- Check you have API credits/quota

### Database errors
- For testing, use SQLite: `DATABASE_URL=sqlite:///./data/llm_deployment.db`
- Create data directory: `mkdir -p data`

## Getting Help

- Check logs in console output
- Review [README.md](README.md) for detailed documentation
- Open an issue on GitHub

---

**Ready to deploy!** 🎉
