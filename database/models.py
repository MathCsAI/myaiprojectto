"""Database models for the LLM Code Deployment project."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    """Tasks sent to students."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    email = Column(String(255), index=True, nullable=False)
    task = Column(String(255), index=True, nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String(255), unique=True, nullable=False)
    brief = Column(Text, nullable=False)
    attachments = Column(JSON, default=list)
    checks = Column(JSON, default=list)
    evaluation_url = Column(String(512), nullable=False)
    endpoint = Column(String(512), nullable=False)
    statuscode = Column(Integer)
    secret = Column(String(255), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "email": self.email,
            "task": self.task,
            "round": self.round,
            "nonce": self.nonce,
            "brief": self.brief,
            "attachments": self.attachments,
            "checks": self.checks,
            "evaluation_url": self.evaluation_url,
            "endpoint": self.endpoint,
            "statuscode": self.statuscode,
        }


class Repo(Base):
    """Repositories submitted by students."""
    __tablename__ = "repos"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    email = Column(String(255), index=True, nullable=False)
    task = Column(String(255), index=True, nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String(255), index=True, nullable=False)
    repo_url = Column(String(512), nullable=False)
    commit_sha = Column(String(255), nullable=False)
    pages_url = Column(String(512), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "email": self.email,
            "task": self.task,
            "round": self.round,
            "nonce": self.nonce,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "pages_url": self.pages_url,
        }


class Result(Base):
    """Evaluation results."""
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    email = Column(String(255), index=True, nullable=False)
    task = Column(String(255), index=True, nullable=False)
    round = Column(Integer, nullable=False)
    repo_url = Column(String(512), nullable=False)
    commit_sha = Column(String(255), nullable=False)
    pages_url = Column(String(512), nullable=False)
    check = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text)
    logs = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "email": self.email,
            "task": self.task,
            "round": self.round,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "pages_url": self.pages_url,
            "check": self.check,
            "score": self.score,
            "reason": self.reason,
            "logs": self.logs,
        }


class Submission(Base):
    """Student submissions from Google Form."""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    endpoint = Column(String(512), nullable=False)
    secret = Column(String(255), nullable=False)
    github_url = Column(String(512))
    active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "email": self.email,
            "endpoint": self.endpoint,
            "github_url": self.github_url,
            "active": self.active,
        }
