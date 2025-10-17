# Quick Reference: Gemini Migration

## 🔑 Get API Key (1 minute)
https://makersuite.google.com/app/apikey → Click "Create API Key" → Copy

## 📝 Update Local .env
```bash
LLM_API_KEY=AIzaSyC...YOUR_KEY_HERE
LLM_API_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```

## 🌐 Update Hugging Face Space
https://huggingface.co/spaces/MathCsAI/llm-code-deployment/settings
→ Environment Variables → Update 3 vars → Save

## 🧪 Test
```bash
python3 test_gemini_integration.py
```

## 📊 Limits
- 15 requests/minute
- 1M tokens/day
- 8,192 max tokens/request
- FREE tier

## 💡 Tips
- Use `gemini-1.5-flash` (fastest)
- Add 4-5 sec delays between tests
- Monitor at https://makersuite.google.com/

## 🐛 Troubleshooting
- "Module not found" → `pip install google-generativeai`
- "API key invalid" → Regenerate at AI Studio
- "429 error" → Wait 60 seconds, you hit rate limit

## 📚 Docs
- Setup: `GEMINI_SETUP_GUIDE.md`
- Changes: `GEMINI_MIGRATION_SUMMARY.md`
- Test: `test_gemini_integration.py`

## ✅ What Changed
- Provider: aipipe → gemini
- Model: gpt-4-turbo → gemini-1.5-flash
- Tokens: 4K → 8K
- Cost: $1/week → FREE!

That's it! 🚀
