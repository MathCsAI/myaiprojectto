# Deployment Guide

## Deploying to HuggingFace Spaces

### Option 1: Web Interface

1. **Create a new Space**
   - Go to https://huggingface.co/new-space
   - Choose "Gradio" SDK
   - Set to "Public" or "Private"

2. **Upload files**
   - Use the web interface to upload all project files
   - Or connect your GitHub repository

3. **Configure secrets**
   - Go to Space Settings → Repository secrets
   - Add these secrets:
     - `GITHUB_TOKEN`: Your GitHub Personal Access Token
     - `GITHUB_USERNAME`: Your GitHub username
     - `LLM_API_KEY`: Your LLM API key
     - `DATABASE_URL`: PostgreSQL connection string (optional)

4. **Deploy**
   - Space will automatically build and deploy
   - Access at `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

### Option 2: Git Push

```bash
# Add HuggingFace remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push to deploy
git push hf main
```

## Deploying to Railway

1. **Create new project**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"

2. **Configure**
   - Add environment variables in Railway dashboard
   - Set start command: `python app.py`

3. **Deploy**
   - Railway will automatically deploy on git push

## Deploying to Render

1. **Create new Web Service**
   - Go to https://render.com
   - Connect GitHub repository

2. **Configure**
   ```
   Build Command: pip install -r requirements.txt && playwright install chromium
   Start Command: python app.py
   ```

3. **Add environment variables**
   - Set all required variables in Render dashboard

## Deploying to Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/llm-deployment

# Deploy
gcloud run deploy llm-deployment \
  --image gcr.io/PROJECT_ID/llm-deployment \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GITHUB_TOKEN=xxx,LLM_API_KEY=xxx
```

## Deploying with Docker

### Build image

```bash
docker build -t llm-deployment .
```

### Run container

```bash
docker run -p 7860:7860 \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_USERNAME=xxx \
  -e LLM_API_KEY=xxx \
  -e DATABASE_URL=xxx \
  llm-deployment
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_USERNAME=${GITHUB_USERNAME}
      - LLM_API_KEY=${LLM_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/llm_deployment
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=llm_deployment
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

## Production Checklist

### Security
- [ ] Change `SECRET_KEY` in production
- [ ] Use strong database password
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Set up firewall rules
- [ ] Use secrets management (AWS Secrets Manager, etc.)

### Database
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Enable SSL for database connections

### Performance
- [ ] Use a CDN for static assets
- [ ] Enable response caching
- [ ] Set up load balancing (if needed)
- [ ] Configure worker processes (Gunicorn/uWSGI)

### Monitoring
- [ ] Set up logging (CloudWatch, Datadog, etc.)
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Create alerts for failures

### Scaling
- [ ] Use managed database service (RDS, Cloud SQL)
- [ ] Consider Redis for caching
- [ ] Set up background job queue (Celery, RQ)
- [ ] Use managed Playwright service (Browserless)

## Environment-Specific Configs

### Development
```env
DATABASE_URL=sqlite:///./data/llm_deployment.db
API_HOST=127.0.0.1
API_PORT=7860
```

### Staging
```env
DATABASE_URL=postgresql://user:pass@staging-db:5432/llm_deployment
API_HOST=0.0.0.0
API_PORT=7860
EVALUATION_BASE_URL=https://staging.example.com
```

### Production
```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/llm_deployment
API_HOST=0.0.0.0
API_PORT=7860
EVALUATION_BASE_URL=https://production.example.com
```

## Updating Deployment

### HuggingFace Spaces
```bash
git push hf main
```

### Railway/Render
```bash
git push origin main
# Automatic deployment
```

### Docker
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Rollback

### HuggingFace Spaces
- Go to Space Settings → Factory Reboot
- Or revert git commit and push

### Railway/Render
- Use platform's rollback feature in dashboard

### Docker
```bash
docker-compose down
git checkout <previous-commit>
docker-compose build
docker-compose up -d
```

## Support

For deployment issues:
- Check platform-specific documentation
- Review application logs
- Test locally first with Docker
- Verify all environment variables are set
