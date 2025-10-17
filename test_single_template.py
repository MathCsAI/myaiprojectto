#!/usr/bin/env python3
"""Test a single template with detailed error logging."""

import requests
import time
import sys

def test_sum_of_sales():
    """Test the sum-of-sales template."""
    
    print("\n" + "="*60)
    print("TESTING: Sum of Sales - Round 1")
    print("="*60)
    
    # Step 1: Register task
    print("\n[1/2] Registering task...")
    register_url = "https://mathcsai-llm-code-deployment.hf.space/evaluation/register-task"
    register_data = {
        "task_id": "sum-of-sales",
        "task_name": "Sum of Sales",
        "description": "Calculate total sales",
        "max_round": 2
    }
    
    try:
        response = requests.post(register_url, json=register_data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print(f"✗ Failed to register task")
            return False
            
        print("✓ Task registered")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 2: Submit task
    print("\n[2/2] Submitting task to student API...")
    submit_url = "https://mathcsai-llm-code-deployment.hf.space/student-api/task"
    submit_data = {
        "task_id": "sum-of-sales",
        "round_number": 1
    }
    
    try:
        response = requests.post(submit_url, json=submit_data, timeout=120)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print(f"✗ Failed to submit task")
            return False
            
        result = response.json()
        print(f"✓ Task submitted successfully")
        print(f"  Repo: {result.get('repository_url')}")
        print(f"  Pages: {result.get('github_pages_url')}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_sum_of_sales()
    sys.exit(0 if success else 1)
