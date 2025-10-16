"""Student API endpoint for receiving and processing requests."""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import hashlib
import uuid
from datetime import datetime

from utils.llm_client import llm_client
from utils.github_helper import github_helper
from utils.retry_helper import send_evaluation_response
from config.config import config

app = FastAPI(title="Student LLM Code Deployment API")


class Attachment(BaseModel):
    name: str
    url: str  # data URI


class TaskRequest(BaseModel):
    email: EmailStr
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[List[Attachment]] = []


class TaskResponse(BaseModel):
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Student LLM Code Deployment API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    gh_ok = github_helper.has_credentials()
    status = {"status": "healthy", "github": github_helper.credentials_status()}
    return status


@app.post("/api/task", response_model=TaskResponse)
async def receive_task(task: TaskRequest):
    """
    Receive and process a task request.
    
    This endpoint:
    1. Validates the secret
    2. Uses LLM to generate the app
    3. Creates a GitHub repository
    4. Pushes the code
    5. Enables GitHub Pages
    6. Sends evaluation response
    """
    try:
        # Step 1: Validate secret
        # In production, load secrets from database
        # For now, we'll accept any secret (you should implement proper validation)
        expected_secret = config.STUDENT_SECRETS.get(task.email)
        if expected_secret and task.secret != expected_secret:
            raise HTTPException(status_code=401, detail="Invalid secret")
        
        # Step 2: Ensure GitHub credentials are present before attempting GH operations
        if not github_helper.has_credentials():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "GitHub credentials are not configured",
                    "hint": "Set GITHUB_TOKEN and GITHUB_USERNAME to enable deployment to GitHub",
                },
            )

        # Step 3: Generate app using LLM
        print(f"Generating app for task: {task.task}")
        files = llm_client.generate_app(
            brief=task.brief,
            checks=task.checks,
            attachments=[att.dict() for att in task.attachments]
        )
        
        # Step 4: Create unique repository name
        repo_name = f"{task.task}-{task.round}"
        repo_name = repo_name.replace("_", "-").lower()
        
        print(f"Creating repository: {repo_name}")
        repo_url = github_helper.create_repo(
            repo_name=repo_name,
            description=f"Task: {task.task} Round {task.round}"
        )
        
        # Step 5: Push files to repository
        print(f"Pushing files to repository")
        commit_sha = github_helper.push_files(repo_name, files)
        
        # Step 6: Enable GitHub Pages
        print(f"Enabling GitHub Pages")
        pages_url = github_helper.enable_github_pages(repo_name)
        
        # Wait for Pages to be available and capture status
        print(f"Waiting for GitHub Pages to be available")
        ready = github_helper.wait_for_pages(pages_url, timeout=config.GITHUB_PAGES_TIMEOUT)
        pages_status = github_helper.get_pages_build_status(repo_name)
        
        # Step 7: Send evaluation response
        evaluation_data = {
            "email": task.email,
            "task": task.task,
            "round": task.round,
            "nonce": task.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        
        print(f"Sending evaluation response to {task.evaluation_url}")
        success = send_evaluation_response(task.evaluation_url, evaluation_data)
        
        if not success:
            print(f"Warning: Failed to send evaluation response")
        
        return TaskResponse(
            status="success",
            message=f"App deployed successfully. Repo: {repo_url}, Pages: {pages_url} | PagesReady={ready} BuildStatus={pages_status.get('status')}"
        )
    
    except Exception as e:
        print(f"Error processing task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/secret")
async def set_secret(email: EmailStr, secret: str):
    """Set or update student secret."""
    # In production, store in database
    config.STUDENT_SECRETS[email] = secret
    return {"status": "success", "message": "Secret updated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
