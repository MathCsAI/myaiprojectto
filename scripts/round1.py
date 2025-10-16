"""Round 1: Send initial tasks to students."""
import sys
import csv
import hashlib
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from database.db import get_db, init_db
from database.models import Task, Submission
from utils.retry_helper import retry_request
from config.config import config
from templates.task_loader import TaskLoader


def generate_task_id(template_id: str, brief: str, attachments: list) -> str:
    """Generate unique task ID."""
    content = f"{brief}{str(attachments)}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:5]
    return f"{template_id}-{hash_value}"


def send_round1_tasks(submissions_csv: str = "submissions.csv"):
    """
    Send Round 1 tasks to all students in submissions.csv.
    
    Args:
        submissions_csv: Path to CSV file with columns: timestamp,email,endpoint,secret
    """
    init_db()
    task_loader = TaskLoader()
    
    # Load submissions
    try:
        with open(submissions_csv, "r") as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
    except FileNotFoundError:
        print(f"Error: {submissions_csv} not found")
        return
    
    print(f"Found {len(submissions)} submissions")
    
    with get_db() as db:
        for submission_data in submissions:
            email = submission_data["email"]
            endpoint = submission_data["endpoint"]
            secret = submission_data["secret"]
            
            # Check if round 1 already sent successfully
            existing = db.query(Task).filter(
                Task.email == email,
                Task.round == 1,
                Task.statuscode == 200
            ).first()
            
            if existing:
                print(f"Skipping {email} - Round 1 already completed")
                continue
            
            # Store submission in database
            sub = db.query(Submission).filter(Submission.email == email).first()
            if not sub:
                sub = Submission(
                    email=email,
                    endpoint=endpoint,
                    secret=secret,
                    timestamp=datetime.utcnow()
                )
                db.add(sub)
                db.commit()
            
            # Generate task from random template
            template = task_loader.get_random_template()
            task_data = task_loader.generate_task(template, email, round_num=1)
            
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
                "secret": secret,
                "task": task_id,
                "round": 1,
                "nonce": nonce,
                "brief": task_data["brief"],
                "checks": task_data["checks"],
                "evaluation_url": evaluation_url,
                "attachments": task_data["attachments"]
            }
            
            # Send request to student endpoint
            print(f"Sending Round 1 task to {email}...")
            try:
                response = retry_request(
                    endpoint,
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
                round=1,
                nonce=nonce,
                brief=task_data["brief"],
                attachments=task_data["attachments"],
                checks=task_data["checks"],
                evaluation_url=evaluation_url,
                endpoint=endpoint,
                statuscode=status_code,
                secret=secret
            )
            db.add(task)
            db.commit()
    
    print("\nRound 1 tasks sent!")


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "submissions.csv"
    send_round1_tasks(csv_file)
