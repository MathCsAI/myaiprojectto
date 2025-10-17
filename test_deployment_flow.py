#!/usr/bin/env python3
"""
Automated test script for LLM Code Deployment System:
1. Registers the task in the database (so evaluation API can validate it)
2. Submits a task to the student API
3. Waits for deployment
4. Submits deployment results to the evaluation API
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STUDENT_API_URL = "https://mathcsai-llm-code-deployment.hf.space/student/api/task"
EVALUATION_API_URL = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/evaluate"
TASK_FILE = "test_task.json"

# Load task data
with open(TASK_FILE, "r") as f:
    task_data = json.load(f)

# Step 1: Register the task in the database first
print("Registering task in database...")
try:
    from database.db import get_db, init_db
    from database.models import Task
    
    init_db()
    
    with get_db() as db:
        # Check if task already exists
        existing = db.query(Task).filter(
            Task.email == task_data["email"],
            Task.task == task_data["task"],
            Task.round == task_data["round"],
            Task.nonce == task_data["nonce"]
        ).first()
        
        if not existing:
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
            print("✓ Task registered in database")
        else:
            print("✓ Task already exists in database")
except Exception as e:
    print(f"✗ Failed to register task in database: {e}")
    print("  Continuing anyway (evaluation may fail)...")

except Exception as e:
    print(f"✗ Failed to register task in database: {e}")
    print("  Continuing anyway (evaluation may fail)...")

# Step 2: Submit task to student API
print("\nSubmitting task to student API...")
resp = requests.post(STUDENT_API_URL, json=task_data)
if resp.status_code != 200:
    print(f"Student API error: {resp.status_code}", resp.text)
    exit(1)
result = resp.json()
print("Student API response:", result)

# Robustly extract repo_url, pages_url, and commit_sha from the message string
import re
msg = result.get("message", "")
repo_url_match = re.search(r"Repo: (https?://[\w./-]+)", msg)
pages_url_match = re.search(r"Pages: (https?://[\w./-]+)", msg)
commit_sha_match = re.search(r"Commit: ([a-f0-9]{7,40})", msg)

if not repo_url_match or not pages_url_match:
    print("Could not extract repo_url or pages_url from response.")
    exit(3)

repo_url = repo_url_match.group(1)
pages_url = pages_url_match.group(1)
commit_sha = commit_sha_match.group(1) if commit_sha_match else "unknown"

submission = {
    "email": task_data["email"],
    "task": task_data["task"],
    "round": task_data["round"],
    "nonce": task_data["nonce"],
    "repo_url": repo_url,
    "commit_sha": commit_sha,
    "pages_url": pages_url
}

print("\nSubmitting deployment results to evaluation API...")
eval_resp = requests.post(EVALUATION_API_URL, json=submission)
print("Evaluation API response:", eval_resp.status_code)
if eval_resp.status_code == 200:
    print("✓ Evaluation successful!")
    print(eval_resp.json())
else:
    print("✗ Evaluation failed:")
    print(eval_resp.text)
