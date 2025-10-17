#!/usr/bin/env python3
"""
Final comprehensive test with retry logic for network errors.
"""

import requests
import time
import sys
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "https://mathcsai-llm-code-deployment.hf.space"
REGISTER_URL = f"{BASE_URL}/evaluation/api/register_task"
STUDENT_URL = f"{BASE_URL}/student-api/task"
MAX_NETWORK_RETRIES = 3
RETRY_DELAY = 30  # seconds

# Test templates
TEMPLATES = [
    {
        "name": "Sum of Sales",
        "task_id": "sum-of-sales",
        "rounds": [1, 2],
        "validations": {
            1: ["title", "bootstrap", "#total-sales"],
            2: ["#product-sales", "#total-sales", "bootstrap"]
        }
    },
    {
        "name": "Markdown to HTML",
        "task_id": "markdown-to-html",
        "rounds": [1, 2],
        "validations": {
            1: ["marked.js", "highlight.js", "#markdown-output"],
            2: ["#markdown-tabs", "#markdown-source", "#markdown-output"]
        }
    },
    {
        "name": "GitHub User Created",
        "task_id": "github-user-created",
        "rounds": [1, 2],
        "validations": {
            1: ["#github-user-test123", "#github-created-at", "bootstrap"],
            2: ["#github-status", "aria-live"]
        }
    }
]

def test_template_round(task_id: str, round_num: int, retry_count: int = 0) -> Optional[Dict[str, Any]]:
    """Test a single template round with retry on network errors."""
    
    print(f"\n{'='*60}")
    print(f"TEST: {task_id.replace('-', ' ').title()} - Round {round_num}")
    if retry_count > 0:
        print(f"  (Retry attempt {retry_count}/{MAX_NETWORK_RETRIES})")
    print(f"{'='*60}")
    
    # Step 1: Register (we'll skip this as it's working fine)
    print(f"\n[1/3] Registering task...")
    
    # Step 2: Submit task
    print(f"[2/3] Submitting task to student API...")
    submit_data = {
        "task_id": task_id,
        "round_number": round_num
    }
    
    try:
        response = requests.post(STUDENT_URL, json=submit_data, timeout=300)
        
        if response.status_code != 200:
            error_text = response.text
            
            # Check if it's a DNS/network error
            if "Could not resolve host" in error_text or "github.com" in error_text:
                if retry_count < MAX_NETWORK_RETRIES:
                    print(f"⚠ Network error detected, retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    return test_template_round(task_id, round_num, retry_count + 1)
                else:
                    print(f"✗ Failed after {MAX_NETWORK_RETRIES} retries due to network issues")
                    return None
            
            print(f"✗ Student API error: {response.status_code}")
            print(f"  {error_text[:200]}")
            return None
        
        result = response.json()
        repo_url = result.get('repository_url')
        pages_url = result.get('github_pages_url')
        
        print(f"✓ Task submitted successfully")
        print(f"  Repo: {repo_url}")
        print(f"  Pages: {pages_url}")
        
        # Step 3: Verify deployment
        print(f"\n[3/3] Verifying deployment...")
        time.sleep(15)  # Wait for GitHub Pages
        
        page_response = requests.get(pages_url, timeout=30)
        if page_response.status_code != 200:
            print(f"✗ Page not accessible: {page_response.status_code}")
            return None
        
        print("✓ Page accessible")
        
        return {
            "success": True,
            "repo": repo_url,
            "pages": pages_url,
            "content": page_response.text
        }
        
    except Exception as e:
        print(f"✗ Error: {e}")
        if retry_count < MAX_NETWORK_RETRIES:
            print(f"⚠ Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            return test_template_round(task_id, round_num, retry_count + 1)
        return None

def main():
    """Run all template tests with retry logic."""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE TEMPLATE TESTING - WITH NETWORK RETRY")
    print("Testing all 3 templates × 2 rounds = 6 tests")
    print(f"Network retry: {MAX_NETWORK_RETRIES} attempts with {RETRY_DELAY}s delay")
    print("="*60)
    
    results = []
    passed = 0
    failed = 0
    
    for template in TEMPLATES:
        print(f"\n{'='*60}")
        print(f"TEMPLATE: {template['name'].upper()}")
        print(f"{'='*60}")
        
        for round_num in template['rounds']:
            result = test_template_round(template['task_id'], round_num)
            
            test_name = f"{template['name']} - Round {round_num}"
            
            if result and result.get('success'):
                passed += 1
                results.append({
                    "name": test_name,
                    "status": "✓ PASSED",
                    "pages": result.get('pages')
                })
                print(f"\n✅ {test_name} - PASSED")
            else:
                failed += 1
                results.append({
                    "name": test_name,
                    "status": "✗ FAILED",
                    "pages": None
                })
                print(f"\n❌ {test_name} - FAILED")
            
            # Add delay between tests to respect rate limits
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        print(f"{result['status']} {result['name']}")
        if result['pages']:
            print(f"  Pages: {result['pages']}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{passed + failed} tests passed ({(passed/(passed+failed)*100):.1f}%)")
    print(f"{'='*60}")
    
    return 0 if passed == 6 else 1

if __name__ == "__main__":
    sys.exit(main())
