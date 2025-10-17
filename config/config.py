"""Configuration settings for the LLM Code Deployment project."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Main configuration class."""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "7860"))
    
    # Database
    # Default to SQLite for portability (e.g., Hugging Face Spaces)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/app.db"
    )
    
    # GitHub Settings
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
    
    # LLM Settings
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_API_PROVIDER = os.getenv("LLM_API_PROVIDER", "gemini")  # gemini, aipipe, openai, anthropic
    LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "https://generativelanguage.googleapis.com")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")  # gemini-1.5-flash (free tier) or gemini-1.5-pro
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    STUDENT_SECRETS = {}  # Will be loaded from database
    
    # Evaluation
    EVALUATION_BASE_URL = os.getenv("EVALUATION_BASE_URL", "http://localhost:7860")
    EVALUATION_TIMEOUT = int(os.getenv("EVALUATION_TIMEOUT", "600"))  # 10 minutes
    
    # GitHub Pages
    GITHUB_PAGES_BRANCH = os.getenv("GITHUB_PAGES_BRANCH", "gh-pages")
    GITHUB_PAGES_TIMEOUT = int(os.getenv("GITHUB_PAGES_TIMEOUT", "300"))  # 5 minutes
    
    # Playwright
    PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "15000"))  # 15 seconds
    
    # Task Templates
    TASK_TEMPLATES_DIR = os.getenv("TASK_TEMPLATES_DIR", "templates/tasks")
    
    # Retry Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAYS = [1, 2, 4, 8, 16]  # Exponential backoff in seconds
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is required")
        if not cls.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME is required")
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


config = Config()
