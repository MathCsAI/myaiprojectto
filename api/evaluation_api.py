"""Evaluation API endpoint for receiving repository submissions."""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, HttpUrl
from sqlalchemy.orm import Session
from datetime import datetime

from database.db import get_db_session, init_db
from database.models import Task, Repo

app = FastAPI(title="Evaluation API")


class RepoSubmission(BaseModel):
    email: EmailStr
    task: str
    round: int
    nonce: str
    repo_url: HttpUrl
    commit_sha: str
    pages_url: HttpUrl


class SubmissionResponse(BaseModel):
    status: str
    message: str


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Evaluation API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/register_task")
async def register_task(
    email: str,
    task: str,
    round: int,
    nonce: str,
    brief: str,
    checks: list,
    evaluation_url: str,
    endpoint: str,
    secret: str,
    attachments: list = None,
    db: Session = Depends(get_db_session)
):
    """
    Register a task in the database (for testing purposes).
    In production, tasks are registered via round1.py/round2.py scripts.
    """
    try:
        # Check if task already exists
        existing = db.query(Task).filter(
            Task.email == email,
            Task.task == task,
            Task.round == round,
            Task.nonce == nonce
        ).first()
        
        if existing:
            return {"status": "exists", "message": "Task already registered"}
        
        # Create new task
        new_task = Task(
            timestamp=datetime.utcnow(),
            email=email,
            task=task,
            round=round,
            nonce=nonce,
            brief=brief,
            attachments=attachments or [],
            checks=checks,
            evaluation_url=evaluation_url,
            endpoint=endpoint,
            statuscode=None,
            secret=secret
        )
        db.add(new_task)
        db.commit()
        
        return {"status": "success", "message": "Task registered successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register task: {str(e)}")


@app.post("/api/evaluate", response_model=SubmissionResponse)
async def submit_repo(
    submission: RepoSubmission,
    db: Session = Depends(get_db_session)
):
    """
    Accept repository submission from students.
    
    This endpoint:
    1. Validates that the task exists and matches
    2. Stores the submission in the repos table
    3. Returns 200 on success, 400 on validation error
    """
    try:
        # Step 1: Find matching task
        task = db.query(Task).filter(
            Task.email == submission.email,
            Task.task == submission.task,
            Task.round == submission.round,
            Task.nonce == submission.nonce
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=400,
                detail="No matching task found. Invalid email, task, round, or nonce."
            )
        
        # Step 2: Check if already submitted
        existing = db.query(Repo).filter(
            Repo.email == submission.email,
            Repo.task == submission.task,
            Repo.round == submission.round,
            Repo.nonce == submission.nonce
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Submission already received for this task."
            )
        
        # Step 3: Create repo entry
        repo = Repo(
            timestamp=datetime.utcnow(),
            email=submission.email,
            task=submission.task,
            round=submission.round,
            nonce=submission.nonce,
            repo_url=str(submission.repo_url),
            commit_sha=submission.commit_sha,
            pages_url=str(submission.pages_url)
        )
        
        db.add(repo)
        db.commit()
        
        return SubmissionResponse(
            status="success",
            message="Repository submission received and queued for evaluation."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/submissions/{email}")
async def get_submissions(
    email: str,
    db: Session = Depends(get_db_session)
):
    """Get all submissions for a student."""
    repos = db.query(Repo).filter(Repo.email == email).all()
    return {"submissions": [repo.to_dict() for repo in repos]}


@app.get("/api/results/{email}")
async def get_results(
    email: str,
    db: Session = Depends(get_db_session)
):
    """Get evaluation results for a student."""
    from database.models import Result
    results = db.query(Result).filter(Result.email == email).all()
    return {"results": [result.to_dict() for result in results]}


if __name__ == "__main__":
    import uvicorn
    from config.config import config
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT + 1)
