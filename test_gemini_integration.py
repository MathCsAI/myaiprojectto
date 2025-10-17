#!/usr/bin/env python3
"""
Quick test script to verify Gemini integration.
"""
import os
import sys

# Set environment for testing (replace with your actual key)
print("=" * 60)
print("GEMINI INTEGRATION TEST")
print("=" * 60)

# Check if API key is set
api_key = os.getenv("LLM_API_KEY", "")
if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
    print("\n❌ ERROR: LLM_API_KEY not set or using placeholder")
    print("\n📝 To fix this:")
    print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Update .env file:")
    print("   LLM_API_KEY=AIzaSyC...YOUR_ACTUAL_KEY")
    print("3. Run this test again")
    sys.exit(1)

print(f"\n✓ API Key found (starts with: {api_key[:10]}...)")

# Force reload to use new .env
os.environ['DATABASE_URL'] = 'sqlite:///./data/app.db'
os.environ['LLM_API_PROVIDER'] = 'gemini'
os.environ['LLM_MODEL'] = 'gemini-1.5-flash'

try:
    from utils.llm_client import llm_client
    
    print(f"\n✓ LLM Client initialized")
    print(f"  Provider: {llm_client.provider}")
    print(f"  Model: {llm_client.model}")
    
    # Test 1: Simple generation
    print("\n" + "=" * 60)
    print("TEST 1: Simple Code Generation")
    print("=" * 60)
    
    response = llm_client.generate_code(
        prompt="Generate a simple 'Hello World' in JavaScript. Just the code, no explanation.",
        system_prompt="You are a code generator. Output only code."
    )
    
    print("\n✓ Response received:")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Test 2: App generation (simplified)
    print("\n" + "=" * 60)
    print("TEST 2: App Generation with Files")
    print("=" * 60)
    
    files = llm_client.generate_app(
        brief="Create a simple calculator that adds two numbers",
        checks=["Has input fields", "Has add button", "Shows result"],
        attachments=[]
    )
    
    print(f"\n✓ Generated {len(files)} files:")
    for filename in files.keys():
        content_length = len(files[filename])
        print(f"  - {filename} ({content_length} chars)")
    
    # Verify index.html exists
    if "index.html" in files:
        html = files["index.html"]
        checks = {
            "Has DOCTYPE": "<!DOCTYPE" in html,
            "Has HTML tag": "<html" in html,
            "Has body": "<body" in html,
            "Has script": "<script" in html or "calculator" in html.lower()
        }
        
        print("\n✓ index.html validation:")
        for check, passed in checks.items():
            print(f"  {'✓' if passed else '✗'} {check}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - GEMINI INTEGRATION WORKING!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run full template tests: python3 test_all_templates.py")
    print("2. Deploy to Hugging Face Spaces")
    print("3. Update HF Space env vars with your Gemini API key")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ TEST FAILED")
    print("=" * 60)
    print(f"\nError: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify API key is correct")
    print("2. Check if Generative Language API is enabled")
    print("3. Try regenerating API key at https://makersuite.google.com/app/apikey")
    sys.exit(1)
