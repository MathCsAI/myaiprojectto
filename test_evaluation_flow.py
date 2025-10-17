#!/usr/bin/env python3
"""
Complete test: Register task -> Deploy via student API -> Evaluate
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# Force reload of environment
if 'database' in sys.modules:
    del sys.modules['database']
if 'config' in sys.modules:
    del sys.modules['config']

# Set environment variable to ensure SQLite is used
os.environ['DATABASE_URL'] = 'sqlite:///./data/app.db'

# Now import after setting env
from database.db import get_db, init_db
from database.models import Task

STUDENT_API_URL = "https://mathcsai-llm-code-deployment.hf.space/student/api/task"
EVALUATION_API_URL = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/evaluate"
REGISTER_TASK_URL = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/register_task"
TASK_FILE = "test_task.json"

# Load task data
with open(TASK_FILE, "r") as f:
    task_data = json.load(f)

print("=" * 60)
print("LLM Code Deployment - Full Evaluation Test")
print("=" * 60)

# Step 1: Register task on HF Space evaluation API
print("\n[1/4] Registering task on HF Space...")
try:
    register_payload = {
        "email": task_data["email"],
        "task": task_data["task"],
        "round": task_data["round"],
        "nonce": task_data["nonce"],
        "brief": task_data["brief"],
        "checks": task_data["checks"],
        "evaluation_url": task_data["evaluation_url"],
        "endpoint": "https://mathcsai-llm-code-deployment.hf.space/student/api/task",
        "secret": task_data["secret"],
        "attachments": task_data.get("attachments", [])
    }
    
    reg_resp = requests.post(REGISTER_TASK_URL, json=register_payload, timeout=30)
    if reg_resp.status_code == 200:
        reg_result = reg_resp.json()
        print(f"✓ {reg_result['message']}")
        print(f"  Email: {task_data['email']}")
        print(f"  Task: {task_data['task']}")
        print(f"  Round: {task_data['round']}")
        print(f"  Nonce: {task_data['nonce']}")
    else:
        print(f"✗ Registration failed: {reg_resp.status_code}")
        print(reg_resp.text)
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed to register task: {e}")
    sys.exit(1)

# Step 2: Also register locally for reference
print("\n[2/4] Registering task in local database...")
try:
    init_db()
    
    with get_db() as db:
        # Delete existing task if present (for testing)
        existing = db.query(Task).filter(
            Task.email == task_data["email"],
            Task.task == task_data["task"],
            Task.round == task_data["round"],
            Task.nonce == task_data["nonce"]
        ).first()
        
        if existing:
            db.delete(existing)
            db.commit()
            print("  Removed existing task entry")
        
        # Create new task entry
        task = Task(
            timestamp=datetime.utcnow(),
            email=task_data["email"],
            task=task_data["task"],
            round=task_data["round"],
            nonce=task_data["nonce"],
            brief=task_data["brief"],
            attachments=task_data["attachments"],
            checks=task_data["checks"],
            evaluation_url=task_data["evaluation_url"],
            endpoint="https://mathcsai-llm-code-deployment.hf.space/student/api/task",
            statuscode=None,
            secret=task_data["secret"]
        )
        db.add(task)
        db.commit()
        print("✓ Task registered locally")
except Exception as e:
    print(f"⚠ Local registration skipped: {e}")

# Step 3: Submit to student API
print("\n[3/4] Submitting task to student API...")
try:
    resp = requests.post(STUDENT_API_URL, json=task_data, timeout=300)
    if resp.status_code != 200:
        print(f"✗ Student API error: {resp.status_code}")
        print(resp.text)
        sys.exit(2)
    
    result = resp.json()
    print("✓ Task submitted successfully")
    print(f"  Status: {result['status']}")
    
    # Extract deployment info
    import re
    msg = result.get("message", "")
    repo_url_match = re.search(r"Repo: (https?://[\w./-]+)", msg)
    pages_url_match = re.search(r"Pages: (https?://[\w./-]+)", msg)
    
    if not repo_url_match or not pages_url_match:
        print("✗ Could not extract repo_url or pages_url from response")
        print(f"  Message: {msg}")
        sys.exit(3)
    
    repo_url = repo_url_match.group(1)
    pages_url = pages_url_match.group(1)
    
    print(f"  Repo: {repo_url}")
    print(f"  Pages: {pages_url}")
    
    # Get commit SHA from GitHub API
    import re
    repo_match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if repo_match:
        owner, repo = repo_match.groups()
        gh_api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/main"
        gh_resp = requests.get(gh_api_url)
        if gh_resp.status_code == 200:
            commit_sha = gh_resp.json()['sha'][:7]
        else:
            commit_sha = "unknown"
    else:
        commit_sha = "unknown"
    
except Exception as e:
    print(f"✗ Student API request failed: {e}")
    sys.exit(2)

# Step 4: Submit to evaluation API
print("\n[4/4] Submitting to evaluation API...")
submission = {
    "email": task_data["email"],
    "task": task_data["task"],
    "round": task_data["round"],
    "nonce": task_data["nonce"],
    "repo_url": repo_url,
    "commit_sha": commit_sha,
    "pages_url": pages_url
}

print(f"  Email: {submission['email']}")
print(f"  Task: {submission['task']}")
print(f"  Round: {submission['round']}")
print(f"  Nonce: {submission['nonce']}")
print(f"  Repo: {submission['repo_url']}")
print(f"  Commit: {submission['commit_sha']}")
print(f"  Pages: {submission['pages_url']}")

try:
    eval_resp = requests.post(EVALUATION_API_URL, json=submission, timeout=30)
    print(f"\nEvaluation API response: {eval_resp.status_code}")
    
    if eval_resp.status_code == 200:
        print("✓ Evaluation successful!")
        print(json.dumps(eval_resp.json(), indent=2))
    else:
        print("✗ Evaluation failed")
        print(eval_resp.text)
        sys.exit(4)
        
except Exception as e:
    print(f"✗ Evaluation request failed: {e}")
    sys.exit(4)

print("\n" + "=" * 60)
print("✓ Full test completed successfully!")
print("=" * 60)
