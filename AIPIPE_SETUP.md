# 🚀 AIPipe Configuration Guide

This guide explains how to configure the LLM Code Deployment System to use **AIPipe** as your LLM provider.

## 📋 What is AIPipe?

AIPipe is an OpenAI-compatible API service that provides access to various LLM models through a unified interface. This system is pre-configured to work seamlessly with AIPipe.

## ⚙️ Configuration

### 1. Get Your AIPipe API Key

1. Sign up at [AIPipe](https://aipipe.com)
2. Navigate to API Keys section
3. Generate a new API key
4. Copy the key (starts with `ap_` or similar)

### 2. Configure Environment Variables

Edit `config/.env`:

```env
# LLM Settings - AIPipe Configuration
LLM_API_KEY=your_aipipe_api_key_here
LLM_API_PROVIDER=aipipe
LLM_API_BASE_URL=https://api.aipipe.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

### 3. Available Models

AIPipe supports various models. Common options:

```env
# OpenAI Models
LLM_MODEL=gpt-4-turbo-preview
LLM_MODEL=gpt-4
LLM_MODEL=gpt-3.5-turbo

# Other providers through AIPipe
LLM_MODEL=claude-3-opus-20240229
LLM_MODEL=claude-3-sonnet-20240229
```

Check [AIPipe documentation](https://docs.aipipe.com) for the complete list of available models.

## 🧪 Testing AIPipe Connection

After configuration, test the connection:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test
python -c "
from utils.llm_client import llm_client
result = llm_client.generate_code('Say hello in one word')
print(f'✓ AIPipe connected! Response: {result}')
"
```

## 🔧 Advanced Configuration

### Custom Base URL

If you're using a custom AIPipe endpoint:

```env
LLM_API_BASE_URL=https://custom.aipipe.endpoint.com/v1
```

### Rate Limiting

Configure request limits in `config/config.py`:

```python
# Add these settings
MAX_REQUESTS_PER_MINUTE = 60
REQUEST_TIMEOUT = 30  # seconds
```

### Model Parameters

Customize generation parameters in `utils/llm_client.py`:

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    temperature=0.7,      # Adjust creativity (0.0-1.0)
    max_tokens=4000,      # Maximum response length
    top_p=1.0,           # Nucleus sampling
    frequency_penalty=0,  # Reduce repetition
    presence_penalty=0    # Encourage new topics
)
```

## 🌐 Using with GitHub Actions

The system includes GitHub Actions workflows that automatically deploy when you push to the repository. Make sure to set these secrets:

### GitHub Secrets Setup

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add these secrets:

#### For HuggingFace Deployment
```
HF_TOKEN=your_huggingface_token
HF_USERNAME=your_huggingface_username
HF_SPACE_NAME=llm-deployment
```

#### For Railway Deployment
```
RAILWAY_TOKEN=your_railway_token
RAILWAY_SERVICE_NAME=llm-deployment
```

#### For Docker Hub
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password
```

#### For Render
```
RENDER_DEPLOY_HOOK=your_render_deploy_hook_url
```

### Environment Secrets (All Platforms)

Also configure these in your deployment platform:

```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
LLM_API_KEY=your_aipipe_api_key
LLM_API_PROVIDER=aipipe
LLM_API_BASE_URL=https://api.aipipe.com/v1
DATABASE_URL=your_database_url
```

## 📊 Monitoring AIPipe Usage

### Check API Usage

Create a monitoring script:

```python
# monitor_aipipe.py
from utils.llm_client import llm_client
import time

def test_aipipe():
    start = time.time()
    response = llm_client.generate_code("Test")
    duration = time.time() - start
    
    print(f"✓ Response time: {duration:.2f}s")
    print(f"✓ Provider: {llm_client.provider}")
    print(f"✓ Model: {llm_client.model}")
    
if __name__ == "__main__":
    test_aipipe()
```

### Cost Tracking

Monitor your AIPipe dashboard for:
- Token usage
- Request count
- Estimated costs
- Rate limit status

## 🔒 Security Best Practices

1. **Never commit API keys**
   ```bash
   # Verify .env is in .gitignore
   grep -q "^\.env$" .gitignore && echo "✓ Safe" || echo "⚠️ Add .env to .gitignore"
   ```

2. **Use environment-specific keys**
   - Development: Limited quota key
   - Production: Full access key

3. **Rotate keys regularly**
   - Set calendar reminder for monthly rotation
   - Update in all deployment platforms

4. **Monitor for anomalies**
   - Set up alerts in AIPipe dashboard
   - Monitor unexpected usage spikes

## 🚀 Deployment with AIPipe

### HuggingFace Spaces

1. Push to GitHub (workflow auto-deploys)
2. Or manually:
   ```bash
   # Set secrets in HF Space settings
   git push hf main
   ```

### Railway

1. Connect GitHub repo
2. Set environment variables
3. Auto-deploys on push to main

### Docker

1. Build with AIPipe config:
   ```bash
   docker build -t llm-deployment .
   docker run -p 7860:7860 \
     -e LLM_API_KEY=your_aipipe_key \
     -e LLM_API_PROVIDER=aipipe \
     -e LLM_API_BASE_URL=https://api.aipipe.com/v1 \
     llm-deployment
   ```

## 🐛 Troubleshooting

### Connection Issues

```python
# Test connection
python -c "
import requests
response = requests.get('https://api.aipipe.com/v1/models', 
                       headers={'Authorization': 'Bearer YOUR_KEY'})
print(response.json())
"
```

### Common Errors

**Error: Invalid API Key**
- Verify key in AIPipe dashboard
- Check for extra spaces in `.env`
- Ensure key hasn't expired

**Error: Rate Limit Exceeded**
- Check AIPipe dashboard quota
- Implement request throttling
- Upgrade AIPipe plan

**Error: Model Not Found**
- Verify model name in AIPipe docs
- Check model availability in your region
- Try alternative model

## 📞 Support

- **AIPipe Documentation**: https://docs.aipipe.com
- **AIPipe Support**: support@aipipe.com
- **Project Issues**: GitHub Issues tab

## 🎯 Quick Reference

```bash
# Test AIPipe
python test_system.py

# Start with AIPipe
python app.py

# Deploy to HuggingFace
git push origin main  # Auto-deploys via GitHub Actions

# Manual deploy
git push hf main
```

---

**✅ AIPipe is now configured and ready to use!**

For questions or issues, check the [main README](README.md) or open a GitHub issue.
