#!/usr/bin/env python3
"""
Test script to verify the LLM Code Deployment System is working correctly.
Run this after setup to ensure everything is configured properly.
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from config.config import config
        from database.models import Task, Repo, Result, Submission
        from utils.llm_client import llm_client
        from utils.github_helper import github_helper
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_config():
    """Test that configuration is valid."""
    print("\nTesting configuration...")
    try:
        from config.config import config
        
        errors = []
        if not config.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN not set")
        if not config.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME not set")
        if not config.LLM_API_KEY:
            errors.append("LLM_API_KEY not set")
        
        if errors:
            print(f"✗ Configuration errors: {', '.join(errors)}")
            return False
        
        print("✓ Configuration valid")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_database():
    """Test database connection and schema."""
    print("\nTesting database...")
    try:
        from database.db import init_db, get_db
        
        # Initialize database
        init_db()
        
        # Test connection
        with get_db() as db:
            from database.models import Task
            count = db.query(Task).count()
            print(f"✓ Database connected (found {count} tasks)")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_github_api():
    """Test GitHub API connection."""
    print("\nTesting GitHub API...")
    try:
        from utils.github_helper import github_helper
        
        user = github_helper.gh.get_user()
        print(f"✓ GitHub API connected as {user.login}")
        return True
    except Exception as e:
        print(f"✗ GitHub API error: {e}")
        return False


def test_llm_api():
    """Test LLM API connection."""
    print("\nTesting LLM API...")
    try:
        from utils.llm_client import llm_client
        
        response = llm_client.generate_code("Say 'Hello' in one word")
        if response:
            print(f"✓ LLM API connected (response: {response[:50]}...)")
            return True
        else:
            print("✗ LLM API returned empty response")
            return False
    except Exception as e:
        print(f"✗ LLM API error: {e}")
        return False


def test_task_templates():
    """Test task template loading."""
    print("\nTesting task templates...")
    try:
        from templates.task_loader import task_loader
        
        templates = task_loader.templates
        if not templates:
            print("✗ No templates found")
            return False
        
        print(f"✓ Found {len(templates)} task templates:")
        for template in templates:
            print(f"  - {template['id']}")
        
        # Test generation
        template = templates[0]
        task_data = task_loader.generate_task(template, "test@example.com", round_num=1)
        print(f"✓ Successfully generated task from template")
        
        return True
    except Exception as e:
        print(f"✗ Template error: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints (if server is running)."""
    print("\nTesting API endpoints...")
    try:
        from config.config import config
        base_url = f"http://{config.API_HOST}:{config.API_PORT}"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            return False
        
        # Test student API
        response = requests.get(f"{base_url}/student/", timeout=5)
        if response.status_code == 200:
            print(f"✓ Student API working")
        else:
            print(f"✗ Student API returned {response.status_code}")
        
        # Test evaluation API
        response = requests.get(f"{base_url}/evaluation/", timeout=5)
        if response.status_code == 200:
            print(f"✓ Evaluation API working")
        else:
            print(f"✗ Evaluation API returned {response.status_code}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("⚠ API server not running (this is OK if you haven't started it yet)")
        print("  Start the server with: python app.py")
        return True
    except Exception as e:
        print(f"✗ API error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("LLM Code Deployment System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("GitHub API", test_github_api),
        ("LLM API", test_llm_api),
        ("Task Templates", test_task_templates),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check configuration and dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
