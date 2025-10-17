#!/usr/bin/env python3
"""Quick script to list available Gemini models."""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")

if not api_key:
    print("Error: LLM_API_KEY not set")
    exit(1)

import google.generativeai as genai

genai.configure(api_key=api_key)

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
        print(f"    Display Name: {model.display_name}")
        print(f"    Description: {model.description[:80]}...")
        print()
