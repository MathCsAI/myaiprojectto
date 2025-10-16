# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the LLM Code Deployment System.

## 📋 Available Workflows

### 🧪 Testing & Quality

#### `test.yml` - Run Tests
- **Trigger**: Push to main/develop, Pull requests
- **Purpose**: Run test suite on multiple Python versions
- **Matrix**: Python 3.9, 3.10, 3.11
- **Actions**: Syntax checks, import tests, dependency validation

#### `lint.yml` - Code Quality
- **Trigger**: Push to main/develop, Pull requests
- **Purpose**: Check code formatting and style
- **Tools**: Black, flake8, pylint

### 🚀 Deployment

#### `deploy-huggingface.yml` - HuggingFace Spaces
- **Trigger**: Push to main, Manual
- **Purpose**: Deploy to HuggingFace Spaces
- **Secrets Required**:
  - `HF_TOKEN` - HuggingFace API token
  - `HF_USERNAME` - HuggingFace username
  - `HF_SPACE_NAME` - Space name (e.g., llm-deployment)

#### `deploy-railway.yml` - Railway
- **Trigger**: Push to main, Manual
- **Purpose**: Deploy to Railway
- **Secrets Required**:
  - `RAILWAY_TOKEN` - Railway API token
  - `RAILWAY_SERVICE_NAME` - Service name

#### `deploy-render.yml` - Render
- **Trigger**: Push to main, Manual
- **Purpose**: Deploy to Render
- **Secrets Required**:
  - `RENDER_DEPLOY_HOOK` - Render deploy hook URL

#### `deploy-docker.yml` - Docker Hub
- **Trigger**: Push to main, Tags, Manual
- **Purpose**: Build and push Docker images
- **Secrets Required**:
  - `DOCKER_USERNAME` - Docker Hub username
  - `DOCKER_PASSWORD` - Docker Hub password/token
- **Features**:
  - Multi-tag support (latest, version tags)
  - Cache optimization
  - Automatic versioning

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets based on your deployment target:

#### For HuggingFace Spaces:
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
HF_USERNAME=your_username
HF_SPACE_NAME=llm-deployment
```

Get HF_TOKEN from: https://huggingface.co/settings/tokens

#### For Railway:
```
RAILWAY_TOKEN=xxxxxxxxxxxxxxxxxxxxx
RAILWAY_SERVICE_NAME=llm-deployment
```

Get RAILWAY_TOKEN from: https://railway.app/account/tokens

#### For Render:
```
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-xxxxx?key=xxxxx
```

Get deploy hook from: Render Dashboard → Service → Settings → Deploy Hook

#### For Docker Hub:
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
```

Create token at: https://hub.docker.com/settings/security

### 2. Enable Workflows

Workflows are automatically enabled when you push to your repository. You can also trigger them manually:

1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"

### 3. Monitor Deployments

- Check the Actions tab for workflow runs
- View logs for each step
- Get deployment URLs from workflow outputs

## 🎯 Workflow Triggers

### Automatic Triggers
- **Push to main**: Runs tests, quality checks, and deployments
- **Pull Request**: Runs tests and quality checks only
- **Push tags (v*)**: Builds versioned Docker images

### Manual Triggers
All workflows support `workflow_dispatch` for manual execution:
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow" button
4. Choose branch
5. Click "Run workflow"

## 🔄 Deployment Flow

```
┌─────────────────┐
│  Push to main   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Run Tests (Python 3.9, 3.10, 3.11) │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Code Quality   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│  Deploy (Parallel)           │
│  • HuggingFace Spaces       │
│  • Railway (if configured)   │
│  • Render (if configured)    │
│  • Docker Hub               │
└──────────────────────────────┘
```

## 🛠️ Customization

### Modify Deployment Triggers

Edit workflow files to change when they run:

```yaml
on:
  push:
    branches:
      - main
      - staging  # Add staging branch
  workflow_dispatch:
```

### Add Environment-Specific Deployments

Create separate workflows for different environments:

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging
on:
  push:
    branches:
      - develop
```

### Conditional Deployments

Add conditions to skip deployments:

```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: |
    # deployment commands
```

## 📊 Workflow Status Badges

Add status badges to your README:

```markdown
![Tests](https://github.com/USERNAME/REPO/workflows/Run%20Tests/badge.svg)
![Deploy](https://github.com/USERNAME/REPO/workflows/Deploy%20to%20HuggingFace%20Spaces/badge.svg)
![Docker](https://github.com/USERNAME/REPO/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)
```

## 🔒 Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets only
2. **Rotate tokens regularly** - Set reminders for monthly rotation
3. **Use minimal permissions** - Grant only necessary access
4. **Review workflow runs** - Check logs for suspicious activity
5. **Enable branch protection** - Require reviews before merging

## 🐛 Troubleshooting

### Workflow Fails

1. Check workflow logs in Actions tab
2. Verify all secrets are configured
3. Ensure secrets match platform requirements
4. Check for syntax errors in YAML

### Deployment Fails

1. Verify deployment platform is accessible
2. Check API tokens haven't expired
3. Ensure environment variables are set correctly
4. Review platform-specific logs

### Tests Fail

1. Run tests locally first: `python test_system.py`
2. Check Python version compatibility
3. Verify dependencies in requirements.txt
4. Review test logs for specific errors

## 📞 Support

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Project Issues**: Open a GitHub issue
- **Workflow Discussions**: Use GitHub Discussions

## 🎉 Quick Start

1. Configure secrets (see above)
2. Push to main branch
3. Watch the magic happen in Actions tab!

```bash
git add .
git commit -m "Configure GitHub Actions"
git push origin main
```

Your app will automatically deploy! 🚀
