"""Round 2: Send revision tasks to students."""
import sys
import hashlib
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from database.db import get_db, init_db
from database.models import Task, Repo
from utils.retry_helper import retry_request
from config.config import config
from templates.task_loader import TaskLoader


def generate_task_id(template_id: str, brief: str, attachments: list) -> str:
    """Generate unique task ID."""
    content = f"{brief}{str(attachments)}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:5]
    return f"{template_id}-{hash_value}"


def send_round2_tasks():
    """
    Send Round 2 tasks to students who completed Round 1.
    """
    init_db()
    task_loader = TaskLoader()
    
    with get_db() as db:
        # Get all Round 1 repos
        repos = db.query(Repo).filter(Repo.round == 1).all()
        
        print(f"Found {len(repos)} Round 1 submissions")
        
        for repo in repos:
            email = repo.email
            task_id_base = repo.task.rsplit("-", 1)[0]  # Remove hash suffix
            
            # Check if round 2 already sent successfully
            existing = db.query(Task).filter(
                Task.email == email,
                Task.round == 2,
                Task.statuscode == 200
            ).first()
            
            if existing:
                print(f"Skipping {email} - Round 2 already completed")
                continue
            
            # Get the original task to find the template
            original_task = db.query(Task).filter(
                Task.email == email,
                Task.task == repo.task,
                Task.round == 1
            ).first()
            
            if not original_task:
                print(f"Warning: No original task found for {email}")
                continue
            
            # Find matching template
            template = task_loader.get_template_by_id(task_id_base)
            if not template:
                print(f"Warning: No template found for {task_id_base}")
                continue
            
            # Generate Round 2 task
            task_data = task_loader.generate_task(template, email, round_num=2)
            
            task_id = generate_task_id(
                template["id"],
                task_data["brief"],
                task_data["attachments"]
            )
            
            nonce = str(uuid.uuid4())
            evaluation_url = f"{config.EVALUATION_BASE_URL}/api/evaluate"
            
            # Create request payload
            payload = {
                "email": email,
                "secret": original_task.secret,
                "task": task_id,
                "round": 2,
                "nonce": nonce,
                "brief": task_data["brief"],
                "checks": task_data["checks"],
                "evaluation_url": evaluation_url,
                "attachments": task_data["attachments"]
            }
            
            # Send request to student endpoint
            print(f"Sending Round 2 task to {email}...")
            try:
                response = retry_request(
                    original_task.endpoint,
                    method="POST",
                    json_data=payload,
                    max_retries=3
                )
                status_code = response.status_code
                print(f"  ✓ Response: {status_code}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                status_code = None
            
            # Log to database
            task = Task(
                timestamp=datetime.utcnow(),
                email=email,
                task=task_id,
                round=2,
                nonce=nonce,
                brief=task_data["brief"],
                attachments=task_data["attachments"],
                checks=task_data["checks"],
                evaluation_url=evaluation_url,
                endpoint=original_task.endpoint,
                statuscode=status_code,
                secret=original_task.secret
            )
            db.add(task)
            db.commit()
    
    print("\nRound 2 tasks sent!")


if __name__ == "__main__":
    send_round2_tasks()
