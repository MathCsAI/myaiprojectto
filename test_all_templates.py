#!/usr/bin/env python3
"""
Comprehensive test suite for all task templates - Round 1 and Round 2
Tests: sum-of-sales, markdown-to-html, github-user-created
"""
import sys
import os
import time
import requests
import json
import base64
import hashlib
from datetime import datetime
import uuid

# Set environment for SQLite
os.environ['DATABASE_URL'] = 'sqlite:///./data/app.db'

from database.db import get_db, init_db
from database.models import Task

# Configuration
STUDENT_API_URL = "https://mathcsai-llm-code-deployment.hf.space/student/api/task"
EVALUATION_API_URL = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/evaluate"
REGISTER_TASK_URL = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/register_task"

# Test email and secret
TEST_EMAIL = "test@example.com"
TEST_SECRET = "test123"

# Sample data for templates
SAMPLE_CSV = "product,region,sales\nWidget,North,500\nGadget,South,750\nTool,East,600\nDevice,West,850"
SAMPLE_MARKDOWN = """# Sample Document
This is a **sample** markdown document with:
- Lists
- Code blocks

```python
def hello():
    print("Hello, World!")
```
"""
GITHUB_USERNAME = "torvalds"  # Famous GitHub user for testing

def encode_base64(text):
    """Encode text to base64."""
    return base64.b64encode(text.encode()).decode()

def create_task_id(template_id, brief, attachments):
    """Create unique task ID."""
    content = f"{brief}{str(attachments)}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
    timestamp = int(time.time())
    return f"{template_id}-{hash_value}-{timestamp}"

def register_and_deploy(task_data, test_name):
    """Register task and deploy app."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    # Step 1: Register task on HF Space
    print(f"\n[1/3] Registering task on HF Space...")
    try:
        register_payload = {
            "email": task_data["email"],
            "task": task_data["task"],
            "round": task_data["round"],
            "nonce": task_data["nonce"],
            "brief": task_data["brief"],
            "checks": task_data["checks"],
            "evaluation_url": task_data["evaluation_url"],
            "endpoint": STUDENT_API_URL,
            "secret": task_data["secret"],
            "attachments": task_data.get("attachments", [])
        }
        
        reg_resp = requests.post(REGISTER_TASK_URL, json=register_payload, timeout=30)
        if reg_resp.status_code == 200:
            reg_result = reg_resp.json()
            print(f"✓ {reg_result['message']}")
        else:
            print(f"✗ Registration failed: {reg_resp.status_code}")
            print(reg_resp.text)
            return None
    except Exception as e:
        print(f"✗ Failed to register task: {e}")
        return None
    
    # Step 2: Submit to student API
    print(f"\n[2/3] Submitting task to student API...")
    try:
        resp = requests.post(STUDENT_API_URL, json=task_data, timeout=300)
        if resp.status_code != 200:
            print(f"✗ Student API error: {resp.status_code}")
            print(resp.text)
            return None
        
        result = resp.json()
        print(f"✓ Task submitted successfully")
        
        # Extract deployment info
        import re
        msg = result.get("message", "")
        repo_url_match = re.search(r"Repo: (https?://[^\s]+)", msg)
        pages_url_match = re.search(r"Pages: (https?://[^\s]+)", msg)
        
        if not repo_url_match or not pages_url_match:
            print(f"✗ Could not extract URLs from response")
            print(f"  Message: {msg}")
            return None
        
        repo_url = repo_url_match.group(1)
        pages_url = pages_url_match.group(1)
        
        print(f"  Repo: {repo_url}")
        print(f"  Pages: {pages_url}")
        
        return {
            "repo_url": repo_url,
            "pages_url": pages_url,
            "task": task_data["task"],
            "round": task_data["round"]
        }
        
    except Exception as e:
        print(f"✗ Student API request failed: {e}")
        return None

def test_sum_of_sales_round1():
    """Test sum-of-sales template - Round 1"""
    seed = "test-seed-1"
    csv_data = SAMPLE_CSV
    expected_total = 2700  # 500+750+600+850
    
    task_id = create_task_id("sum-of-sales", "Sales summary", [])
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": str(uuid.uuid4()),
        "brief": f"Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to 'Sales Summary {seed}', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            f"js: document.title.includes('Sales Summary')",
            "js: !!document.querySelector(\"link[href*='bootstrap']\")",
            "js: !!document.querySelector(\"#total-sales\")"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": [
            {
                "name": "data.csv",
                "url": f"data:text/csv;base64,{encode_base64(csv_data)}"
            }
        ]
    }
    
    result = register_and_deploy(task_data, "Sum of Sales - Round 1")
    
    if result:
        print(f"\n[3/3] Verifying deployment...")
        time.sleep(5)  # Wait for pages to be ready
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    "Has title": "Sales Summary" in html,
                    "Has Bootstrap": "bootstrap" in html.lower(),
                    "Has #total-sales": "total-sales" in html
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def test_sum_of_sales_round2(round1_result):
    """Test sum-of-sales template - Round 2"""
    if not round1_result:
        print("\n⚠ Skipping Round 2 - Round 1 failed")
        return None
    
    seed = "test-seed-2"
    
    task_id = round1_result["task"]  # Same task ID
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 2,
        "nonce": str(uuid.uuid4()),
        "brief": "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "js: document.querySelectorAll(\"#product-sales tbody tr\").length >= 1",
            "js: !!document.querySelector(\"#total-sales\")"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": []
    }
    
    result = register_and_deploy(task_data, "Sum of Sales - Round 2")
    
    if result:
        print(f"\n[3/3] Verifying updated deployment...")
        time.sleep(5)
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    "Has #product-sales table": "product-sales" in html,
                    "Has #total-sales": "total-sales" in html,
                    "Has Bootstrap": "bootstrap" in html.lower()
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def test_markdown_to_html_round1():
    """Test markdown-to-html template - Round 1"""
    md_data = SAMPLE_MARKDOWN
    
    task_id = create_task_id("markdown-to-html", "Markdown converter", [])
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": str(uuid.uuid4()),
        "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "js: !!document.querySelector(\"script[src*='marked']\")",
            "js: !!document.querySelector(\"script[src*='highlight']\")",
            "js: document.querySelector(\"#markdown-output\").innerHTML.includes(\"<h\")"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": [
            {
                "name": "input.md",
                "url": f"data:text/markdown;base64,{encode_base64(md_data)}"
            }
        ]
    }
    
    result = register_and_deploy(task_data, "Markdown to HTML - Round 1")
    
    if result:
        print(f"\n[3/3] Verifying deployment...")
        time.sleep(5)
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    "Has marked.js": "marked" in html.lower(),
                    "Has highlight.js": "highlight" in html.lower(),
                    "Has #markdown-output": "markdown-output" in html
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def test_markdown_to_html_round2(round1_result):
    """Test markdown-to-html template - Round 2"""
    if not round1_result:
        print("\n⚠ Skipping Round 2 - Round 1 failed")
        return None
    
    task_id = round1_result["task"]
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 2,
        "nonce": str(uuid.uuid4()),
        "brief": "Add tabs #markdown-tabs that switch between rendered HTML in #markdown-output and the original Markdown in #markdown-source while keeping content in sync.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "js: document.querySelectorAll(\"#markdown-tabs button\").length >= 2",
            "js: document.querySelector(\"#markdown-source\").textContent.trim().length > 0"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": []
    }
    
    result = register_and_deploy(task_data, "Markdown to HTML - Round 2")
    
    if result:
        print(f"\n[3/3] Verifying updated deployment...")
        time.sleep(5)
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    "Has #markdown-tabs": "markdown-tabs" in html,
                    "Has #markdown-source": "markdown-source" in html,
                    "Has #markdown-output": "markdown-output" in html
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def test_github_user_round1():
    """Test github-user-created template - Round 1"""
    seed = "test123"
    
    task_id = create_task_id("github-user-created", "GitHub user lookup", [])
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": str(uuid.uuid4()),
        "brief": f"Publish a Bootstrap page with form id=\"github-user-{seed}\" that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            f"js: document.querySelector(\"#github-user-{seed}\").tagName === \"FORM\"",
            "js: document.querySelector(\"#github-created-at\").textContent.includes(\"20\")",
            "js: !!document.querySelector(\"script\").textContent.includes(\"https://api.github.com/users/\")"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": []
    }
    
    result = register_and_deploy(task_data, "GitHub User Created - Round 1")
    
    if result:
        print(f"\n[3/3] Verifying deployment...")
        time.sleep(5)
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    f"Has form #github-user-{seed}": f"github-user-{seed}" in html,
                    "Has #github-created-at": "github-created-at" in html,
                    "Has Bootstrap": "bootstrap" in html.lower(),
                    "Has GitHub API call": "api.github.com/users" in html
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def test_github_user_round2(round1_result):
    """Test github-user-created template - Round 2"""
    if not round1_result:
        print("\n⚠ Skipping Round 2 - Round 1 failed")
        return None
    
    seed = "test123"
    task_id = round1_result["task"]
    
    task_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 2,
        "nonce": str(uuid.uuid4()),
        "brief": "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "js: document.querySelector(\"#github-status\").getAttribute(\"aria-live\") === \"polite\"",
            "js: !!document.querySelector(\"script\").textContent.includes(\"github-status\")"
        ],
        "evaluation_url": EVALUATION_API_URL,
        "attachments": []
    }
    
    result = register_and_deploy(task_data, "GitHub User Created - Round 2")
    
    if result:
        print(f"\n[3/3] Verifying updated deployment...")
        time.sleep(5)
        
        try:
            page_resp = requests.get(result["pages_url"], timeout=10)
            if page_resp.status_code == 200:
                html = page_resp.text
                checks = {
                    "Has #github-status": "github-status" in html,
                    "Has aria-live": "aria-live" in html,
                    "Has #github-created-at": "github-created-at" in html
                }
                
                print("✓ Page accessible")
                for check, passed in checks.items():
                    print(f"  {'✓' if passed else '✗'} {check}")
            else:
                print(f"✗ Page not accessible: {page_resp.status_code}")
        except Exception as e:
            print(f"✗ Failed to verify page: {e}")
    
    return result

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEMPLATE TESTING SUITE")
    print("Testing all 3 templates × 2 rounds = 6 tests")
    print("="*60)
    
    init_db()
    
    results = {}
    
    # Test 1: Sum of Sales
    print("\n" + "="*60)
    print("TEMPLATE 1: SUM OF SALES")
    print("="*60)
    results['sum_r1'] = test_sum_of_sales_round1()
    time.sleep(10)  # Wait between tests
    results['sum_r2'] = test_sum_of_sales_round2(results['sum_r1'])
    
    # Test 2: Markdown to HTML
    print("\n" + "="*60)
    print("TEMPLATE 2: MARKDOWN TO HTML")
    print("="*60)
    time.sleep(10)
    results['md_r1'] = test_markdown_to_html_round1()
    time.sleep(10)
    results['md_r2'] = test_markdown_to_html_round2(results['md_r1'])
    
    # Test 3: GitHub User Created
    print("\n" + "="*60)
    print("TEMPLATE 3: GITHUB USER CREATED")
    print("="*60)
    time.sleep(10)
    results['gh_r1'] = test_github_user_round1()
    time.sleep(10)
    results['gh_r2'] = test_github_user_round2(results['gh_r1'])
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    test_names = {
        'sum_r1': 'Sum of Sales - Round 1',
        'sum_r2': 'Sum of Sales - Round 2',
        'md_r1': 'Markdown to HTML - Round 1',
        'md_r2': 'Markdown to HTML - Round 2',
        'gh_r1': 'GitHub User Created - Round 1',
        'gh_r2': 'GitHub User Created - Round 2'
    }
    
    passed = 0
    total = 0
    
    for key, name in test_names.items():
        total += 1
        if results.get(key):
            print(f"✓ {name}")
            print(f"  Pages: {results[key]['pages_url']}")
            passed += 1
        else:
            print(f"✗ {name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
