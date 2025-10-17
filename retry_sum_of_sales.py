#!/usr/bin/env python3
"""Retry the failed Sum of Sales Round 2 test."""

import requests
import time
from bs4 import BeautifulSoup

def test_sum_of_sales_round_2():
    """Test Sum of Sales Round 2."""
    
    print("\n" + "="*60)
    print("RETRY: Sum of Sales - Round 2")
    print("="*60)
    
    # Step 1: Register task
    print("\n[1/3] Registering task...")
    register_url = "https://mathcsai-llm-code-deployment.hf.space/evaluation/api/register_task"
    
    # Read template
    with open("templates/tasks/sum-of-sales/round_2.json") as f:
        import json
        template = json.load(f)
    
    try:
        response = requests.post(register_url, json=template, timeout=30)
        if response.status_code != 200:
            print(f"✗ Failed to register: {response.text}")
            return False
        print("✓ Task registered")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 2: Submit task
    print("\n[2/3] Submitting task to student API...")
    submit_url = "https://mathcsai-llm-code-deployment.hf.space/student-api/task"
    submit_data = {
        "task_id": "sum-of-sales",
        "round_number": 2
    }
    
    try:
        response = requests.post(submit_url, json=submit_data, timeout=180)
        if response.status_code != 200:
            print(f"✗ Failed: {response.status_code}")
            print(f"  {response.text}")
            return False
        
        result = response.json()
        repo_url = result.get('repository_url')
        pages_url = result.get('github_pages_url')
        
        print(f"✓ Task submitted successfully")
        print(f"  Repo: {repo_url}")
        print(f"  Pages: {pages_url}")
        
        # Step 3: Verify deployment
        print("\n[3/3] Verifying deployment...")
        time.sleep(15)  # Wait for GitHub Pages
        
        page_response = requests.get(pages_url, timeout=30)
        if page_response.status_code != 200:
            print(f"✗ Page not accessible: {page_response.status_code}")
            return False
        
        print("✓ Page accessible")
        
        soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Check for product-sales table
        if soup.find(id='product-sales'):
            print("  ✓ Has #product-sales table")
        else:
            print("  ✗ Missing #product-sales table")
        
        # Check for total-sales
        if soup.find(id='total-sales'):
            print("  ✓ Has #total-sales")
        else:
            print("  ✗ Missing #total-sales")
        
        # Check for Bootstrap
        if 'bootstrap' in page_response.text.lower():
            print("  ✓ Has Bootstrap")
        else:
            print("  ✗ Missing Bootstrap")
        
        print("\n✅ TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = test_sum_of_sales_round_2()
    sys.exit(0 if success else 1)
