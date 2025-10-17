# Google Gemini Integration Guide

## Overview

The system has been updated to use **Google Gemini Free Tier** instead of AIPipe. This provides:

- ✅ **Free tier available** - 15 requests per minute, 1 million tokens per day
- ✅ **Higher token limit** - 8,192 output tokens (vs 4,000)
- ✅ **Better performance** - Gemini 1.5 Flash is optimized for speed
- ✅ **No credit card required** - Truly free tier

---

## 🔑 Step 1: Get Your Gemini API Key

### Option A: Google AI Studio (Easiest)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Click **"Create API key in new project"** (or select existing project)
5. Copy the API key (starts with `AIza...`)

### Option B: Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Generative Language API**
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > API Key**
6. Copy the API key

---

## 📝 Step 2: Update Configuration

### Update `.env` file

Replace the LLM settings in your `.env` file:

```bash
# LLM Settings (Required) - Using Google Gemini Free Tier
LLM_API_KEY=AIzaSyC...YOUR_ACTUAL_KEY_HERE
LLM_API_PROVIDER=gemini
LLM_API_BASE_URL=https://generativelanguage.googleapis.com
LLM_MODEL=gemini-1.5-flash
```

### Available Models

| Model | Description | Free Tier Limits |
|-------|-------------|------------------|
| `gemini-1.5-flash` | ✅ **Recommended** - Fast, efficient | 15 RPM, 1M TPM, 1500 RPD |
| `gemini-1.5-pro` | More capable, slower | 2 RPM, 32K TPM, 50 RPD |
| `gemini-1.0-pro` | Legacy model | 15 RPM, 32K TPM, 1500 RPD |

**RPM** = Requests Per Minute  
**TPM** = Tokens Per Minute  
**RPD** = Requests Per Day

---

## 📦 Step 3: Install Dependencies

### Local Development

```bash
pip install google-generativeai
```

### Hugging Face Spaces

The `requirements.txt` has been updated with `google-generativeai`. The Space will automatically install it on next deployment.

---

## 🚀 Step 4: Deploy to Hugging Face

### Update Environment Variables on HF Space

1. Go to your Space: https://huggingface.co/spaces/MathCsAI/llm-code-deployment
2. Click **Settings** tab
3. Scroll to **Environment Variables**
4. Update or add these variables:

```
LLM_API_KEY = AIzaSyC...YOUR_KEY
LLM_API_PROVIDER = gemini
LLM_MODEL = gemini-1.5-flash
```

5. Click **Save**
6. Space will automatically rebuild

---

## ✅ Step 5: Test the Integration

### Test Locally

```bash
# Set your API key
export LLM_API_KEY="AIzaSyC...YOUR_KEY"

# Run a simple test
python3 -c "
from utils.llm_client import llm_client
response = llm_client.generate_code('Say hello in one word')
print(response)
"
```

### Test via API

```bash
# Test task submission
curl -X POST https://mathcsai-llm-code-deployment.hf.space/student/api/task \
  -H "Content-Type: application/json" \
  -d @test_task.json
```

---

## 📊 What Changed

### Files Modified

1. **`utils/llm_client.py`**
   - Added Gemini provider support
   - Uses `google.generativeai` library
   - Handles Gemini's API format (no system role, combined prompts)
   - Increased max tokens to 8192

2. **`requirements.txt`**
   - Added `google-generativeai` package

3. **`.env` and `config/.env.example`**
   - Updated default provider to `gemini`
   - Updated default model to `gemini-1.5-flash`
   - Updated API base URL

4. **`config/config.py`**
   - Updated default values and comments

### Code Changes Summary

```python
# OLD (AIPipe)
if self.provider == "aipipe":
    from openai import OpenAI
    self.client = OpenAI(
        api_key=self.api_key,
        base_url=config.LLM_API_BASE_URL
    )

# NEW (Gemini)
if self.provider == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=self.api_key)
    self.client = genai.GenerativeModel(self.model)
```

---

## 🔄 Backward Compatibility

The system still supports all previous providers:

- ✅ **gemini** (new default)
- ✅ **aipipe** (if you have quota)
- ✅ **openai** (requires OpenAI API key)
- ✅ **anthropic** (requires Anthropic API key)

To switch back to any provider, just update `.env`:

```bash
LLM_API_PROVIDER=aipipe  # or openai, anthropic
```

---

## 💡 Gemini Free Tier Limits

### Rate Limits

- **15 requests per minute** (gemini-1.5-flash)
- **1 million tokens per day**
- **1,500 requests per day**

### Tips to Stay Within Limits

1. **Use gemini-1.5-flash** (faster, higher RPM)
2. **Add delays** between test runs (4+ seconds)
3. **Monitor usage** at [Google AI Studio](https://makersuite.google.com/)
4. **Upgrade if needed** ($0.00025/1K tokens for input)

### If You Hit Limits

```python
# Error: 429 Resource Exhausted
# Solution: Wait 1 minute, then retry
# Or upgrade to paid tier
```

---

## 🆚 Comparison: AIPipe vs Gemini

| Feature | AIPipe | Gemini Free |
|---------|--------|-------------|
| **Cost** | $1/week quota | Truly free |
| **Rate Limit** | Limited | 15 RPM |
| **Max Tokens** | 4,000 | 8,192 |
| **Model** | GPT-4 Turbo | Gemini 1.5 Flash |
| **Speed** | Medium | Fast |
| **Quality** | Excellent | Very Good |

---

## 🐛 Troubleshooting

### Error: "Module not found: google.generativeai"

```bash
pip install google-generativeai
```

### Error: "API key not valid"

1. Check your API key in `.env`
2. Ensure it starts with `AIza`
3. Regenerate key at [Google AI Studio](https://makersuite.google.com/app/apikey)

### Error: "429 Resource Exhausted"

- You've hit rate limits
- Wait 1 minute between requests
- Or upgrade to paid tier

### Error: "Permission denied"

- Enable **Generative Language API** in Google Cloud Console
- Or create API key through AI Studio instead

---

## 📚 Additional Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Python SDK Reference](https://ai.google.dev/api/python/google/generativeai)
- [Pricing](https://ai.google.dev/pricing)

---

## ✨ Benefits of Gemini

1. **No Credit Card Required** - Truly free tier
2. **Higher Token Limit** - 8K vs 4K output tokens
3. **Fast Performance** - Optimized for speed
4. **Google Integration** - Easy setup with Google account
5. **Generous Limits** - 1M tokens/day, 1500 requests/day

---

## 🎯 Next Steps

1. ✅ Get your Gemini API key
2. ✅ Update `.env` with your key
3. ✅ Install `google-generativeai` package
4. ✅ Test locally: `python3 test_evaluation_flow.py`
5. ✅ Deploy to HF Spaces with new env vars
6. ✅ Run template tests: `python3 test_all_templates.py`

---

## 📞 Support

If you encounter issues:

1. Check [Google AI Studio](https://makersuite.google.com/) for API status
2. Review [API Documentation](https://ai.google.dev/docs)
3. Check rate limits in AI Studio dashboard
4. Ensure `google-generativeai>=0.3.0` is installed

---

**System is now configured for Google Gemini Free Tier! 🎉**
