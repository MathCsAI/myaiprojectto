# 📑 File Index - LLM Code Deployment System

Complete index of all project files with descriptions.

## 📁 Project Root

| File | Size | Description |
|------|------|-------------|
| `app.py` | Main | FastAPI + Gradio application entry point |
| `requirements.txt` | 438B | Python package dependencies |
| `Dockerfile` | - | Docker container configuration |
| `Makefile` | - | Build and run commands |
| `LICENSE` | - | MIT License |
| `.gitignore` | - | Git ignore rules |
| `.dockerignore` | - | Docker ignore rules |

## 📚 Documentation (30KB+)

| File | Size | Description |
|------|------|-------------|
| `README.md` | 15KB | Main documentation and user guide |
| `QUICKSTART.md` | 2.6KB | 5-minute quick start guide |
| `DEPLOYMENT.md` | 4.9KB | Production deployment guide |
| `PROJECT_STRUCTURE.md` | 8.9KB | Architecture and structure overview |
| `PROJECT_COMPLETE.md` | 7.9KB | Project completion summary |
| `CONTRIBUTING.md` | 5.6KB | Contribution guidelines |
| `README_HF.md` | 1.2KB | HuggingFace Spaces README |

## 🛠️ Scripts

| File | Description |
|------|-------------|
| `setup.sh` | Automated setup script |
| `demo.sh` | Quick demo/test script |
| `test_system.py` | Comprehensive test suite |

## 📋 Examples & Templates

| File | Description |
|------|-------------|
| `submissions.csv.example` | Example student submissions |
| `test_task.json` | Example task for testing |
| `config/.env.example` | Environment variables template |

## 🔧 Configuration (`config/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `config.py` | ~80 | Configuration management with validation |
| `.env.example` | ~30 | Environment variables template |

## 🗄️ Database (`database/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `models.py` | ~150 | SQLAlchemy models (Task, Repo, Result, Submission) |
| `db.py` | ~50 | Database connection and session management |

## 🌐 API (`api/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `student_api.py` | ~150 | Student endpoint for task processing |
| `evaluation_api.py` | ~100 | Evaluation endpoint for submissions |

## 📜 Scripts (`scripts/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `round1.py` | ~120 | Send Round 1 tasks to students |
| `round2.py` | ~100 | Send Round 2 revision tasks |
| `evaluate.py` | ~300 | Automated evaluation engine |

## 📋 Templates (`templates/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `task_loader.py` | ~200 | Template loader and task generator |

### Task Templates (`templates/tasks/`)

| File | Description |
|------|-------------|
| `sum-of-sales.json` | CSV processing & visualization task |
| `markdown-to-html.json` | Markdown rendering task |
| `github-user-created.json` | GitHub API integration task |

## 🛠️ Utilities (`utils/`)

| File | Lines | Description |
|------|-------|-------------|
| `__init__.py` | 1 | Package init |
| `llm_client.py` | ~200 | LLM API client (OpenAI/Anthropic) |
| `github_helper.py` | ~200 | GitHub API helper functions |
| `retry_helper.py` | ~80 | HTTP retry with exponential backoff |

## 📊 Summary

### By File Type

| Type | Count | Total Lines |
|------|-------|-------------|
| Python (`.py`) | 21 | 2,272 |
| Documentation (`.md`) | 7 | ~1,000 lines |
| JSON (`.json`) | 3 | ~150 |
| Configuration | 6 | ~200 |
| Scripts (`.sh`) | 2 | ~100 |
| **Total** | **39+** | **~3,700+** |

### By Component

| Component | Files | Purpose |
|-----------|-------|---------|
| Core Application | 1 | Main app entry point |
| APIs | 2 | Student & Evaluation endpoints |
| Database | 2 | Models & connection |
| Scripts | 3 | Round 1, Round 2, Evaluate |
| Templates | 4 | Task loader + 3 templates |
| Utilities | 3 | LLM, GitHub, Retry helpers |
| Configuration | 2 | Config management |
| Documentation | 7 | Comprehensive guides |
| Deployment | 3 | Docker, Makefile, Setup |
| Testing | 3 | Test suite, examples |

## 🎯 Key Files to Know

### For Getting Started
1. `QUICKSTART.md` - Start here
2. `setup.sh` - Run this first
3. `config/.env.example` - Configure this
4. `app.py` - Run this to start

### For Understanding
1. `README.md` - Complete documentation
2. `PROJECT_STRUCTURE.md` - Architecture
3. `DEPLOYMENT.md` - How to deploy

### For Development
1. `api/student_api.py` - Student endpoint logic
2. `utils/llm_client.py` - Code generation
3. `scripts/evaluate.py` - Evaluation logic
4. `templates/task_loader.py` - Task system

### For Deployment
1. `Dockerfile` - Container setup
2. `requirements.txt` - Dependencies
3. `Makefile` - Commands
4. `DEPLOYMENT.md` - Deploy guides

## 🔍 Finding What You Need

### "How do I...?"

| Question | File to Check |
|----------|---------------|
| Start the system? | `QUICKSTART.md` |
| Configure settings? | `config/config.py`, `.env.example` |
| Add a new task? | `templates/tasks/*.json` |
| Modify evaluation? | `scripts/evaluate.py` |
| Change LLM provider? | `utils/llm_client.py` |
| Deploy to production? | `DEPLOYMENT.md` |
| Run tests? | `test_system.py` |
| Add new features? | `CONTRIBUTING.md` |

## 📦 Import Structure

```python
# Configuration
from config.config import config

# Database
from database.db import get_db, init_db
from database.models import Task, Repo, Result, Submission

# Utilities
from utils.llm_client import llm_client
from utils.github_helper import github_helper
from utils.retry_helper import retry_request

# Templates
from templates.task_loader import task_loader
```

## 🚀 Execution Flow

```
1. setup.sh               → Initial setup
2. config/.env            → Configuration
3. app.py                 → Start application
4. scripts/round1.py      → Send tasks
5. api/student_api.py     → Process tasks
6. api/evaluation_api.py  → Receive submissions
7. scripts/evaluate.py    → Evaluate results
8. scripts/round2.py      → Send revisions
```

---

**Total Project Size**: ~40 files, 3,700+ lines, 50KB+ documentation

**Status**: ✅ Complete and Ready for Production
