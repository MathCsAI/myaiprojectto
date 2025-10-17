#!/usr/bin/env python3
"""Test only GitHub User Created Round 2 to verify the fix."""

import requests
import time
from bs4 import BeautifulSoup

def test_github_round_2():
    """Test GitHub User Created Round 2."""
    
    print("\n" + "="*60)
    print("TESTING: GitHub User Created - Round 2")
    print("Verifying #github-created-at is preserved")
    print("="*60)
    
    # Submit task
    print("\n[1/2] Submitting task to student API...")
    submit_url = "https://mathcsai-llm-code-deployment.hf.space/student/api/task"
    submit_data = {
        "task_id": "github-user-created",
        "round_number": 2
    }
    
    try:
        response = requests.post(submit_url, json=submit_data, timeout=300)
        
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
        
        # Verify deployment
        print(f"\n[2/2] Verifying deployment...")
        time.sleep(15)  # Wait for GitHub Pages
        
        page_response = requests.get(pages_url, timeout=30)
        if page_response.status_code != 200:
            print(f"✗ Page not accessible: {page_response.status_code}")
            return False
        
        print("✓ Page accessible")
        
        soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Check for #github-status (Round 2 requirement)
        status_elem = soup.find(id='github-status')
        if status_elem:
            aria_live = status_elem.get('aria-live')
            if aria_live == 'polite':
                print("  ✓ Has #github-status with aria-live='polite'")
            else:
                print(f"  ⚠ Has #github-status but aria-live='{aria_live}' (expected 'polite')")
        else:
            print("  ✗ Missing #github-status")
        
        # Check for #github-created-at (Round 1 requirement - MUST be preserved)
        created_elem = soup.find(id='github-created-at')
        if created_elem:
            print("  ✅ Has #github-created-at (Round 1 element PRESERVED!)")
            return True
        else:
            print("  ❌ Missing #github-created-at (Round 1 element not preserved)")
            print("\n  Page HTML snippet:")
            # Show relevant part of the page
            body = soup.find('body')
            if body:
                print(f"  {str(body)[:500]}...")
            return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = test_github_round_2()
    if success:
        print("\n🎉 TEST PASSED - Round 1 elements preserved in Round 2!")
    else:
        print("\n❌ TEST FAILED - Round 1 elements NOT preserved")
    sys.exit(0 if success else 1)
