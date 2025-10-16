"""Main application entry point combining both APIs."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

from api.student_api import app as student_app
from api.evaluation_api import app as evaluation_app
from database.db import init_db
from config.config import config

# Initialize main app
app = FastAPI(
    title="LLM Code Deployment System",
    description="Automated code generation, deployment, and evaluation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount sub-applications
app.mount("/student", student_app)
app.mount("/evaluation", evaluation_app)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")
    print(f"✓ Server starting on {config.API_HOST}:{config.API_PORT}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "LLM Code Deployment System",
        "version": "1.0.0",
        "endpoints": {
            "student_api": "/student",
            "evaluation_api": "/evaluation",
            "dashboard": "/dashboard",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Create Gradio dashboard
def create_dashboard():
    """Create Gradio dashboard for monitoring."""
    with gr.Blocks(title="LLM Code Deployment Dashboard") as dashboard:
        gr.Markdown("# LLM Code Deployment System Dashboard")
        
        with gr.Tab("Overview"):
            gr.Markdown("""
            ## System Overview
            
            This system automates the process of:
            1. **Building**: Generate apps using LLM based on task briefs
            2. **Deploying**: Push to GitHub and enable GitHub Pages
            3. **Evaluating**: Run automated checks on submissions
            
            ### Components
            - **Student API** (`/student/api/task`): Receives tasks and deploys apps
            - **Evaluation API** (`/evaluation/api/evaluate`): Receives submissions
            - **Scripts**: Round 1, Round 2, and Evaluation scripts
            """)
        
        with gr.Tab("Statistics"):
            stats_button = gr.Button("Refresh Statistics")
            stats_output = gr.JSON(label="System Statistics")
            
            def get_stats():
                from database.db import get_db
                from database.models import Task, Repo, Result
                
                with get_db() as db:
                    total_tasks = db.query(Task).count()
                    total_repos = db.query(Repo).count()
                    total_results = db.query(Result).count()
                    
                    round1_tasks = db.query(Task).filter(Task.round == 1).count()
                    round2_tasks = db.query(Task).filter(Task.round == 2).count()
                    
                    return {
                        "total_tasks_sent": total_tasks,
                        "round_1_tasks": round1_tasks,
                        "round_2_tasks": round2_tasks,
                        "total_submissions": total_repos,
                        "total_evaluations": total_results
                    }
            
            stats_button.click(get_stats, outputs=stats_output)
        
        with gr.Tab("Recent Submissions"):
            refresh_button = gr.Button("Refresh Submissions")
            submissions_output = gr.Dataframe(
                headers=["Email", "Task", "Round", "Repo URL", "Timestamp"],
                label="Recent Submissions"
            )
            
            def get_recent_submissions():
                from database.db import get_db
                from database.models import Repo
                
                with get_db() as db:
                    repos = db.query(Repo).order_by(Repo.timestamp.desc()).limit(10).all()
                    return [
                        [r.email, r.task, r.round, r.repo_url, r.timestamp.isoformat()]
                        for r in repos
                    ]
            
            refresh_button.click(get_recent_submissions, outputs=submissions_output)
        
        with gr.Tab("Configuration"):
            gr.Markdown(f"""
            ## Current Configuration
            
            - **API Host**: `{config.API_HOST}`
            - **API Port**: `{config.API_PORT}`
            - **GitHub Username**: `{config.GITHUB_USERNAME}`
            - **LLM Provider**: `{config.LLM_API_PROVIDER}`
            - **LLM Model**: `{config.LLM_MODEL}`
            - **Database**: `{config.DATABASE_URL.split('@')[-1] if '@' in config.DATABASE_URL else 'Not configured'}`
            
            ### API Endpoints
            - Student API: `http://{config.API_HOST}:{config.API_PORT}/student/api/task`
            - Evaluation API: `http://{config.API_HOST}:{config.API_PORT}/evaluation/api/evaluate`
            """)
    
    return dashboard


# Mount Gradio app
dashboard = create_dashboard()
app = gr.mount_gradio_app(app, dashboard, path="/dashboard")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
