"""Evaluate student submissions."""
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page
from sqlalchemy.orm import Session

from database.db import get_db, init_db
from database.models import Repo, Result, Task
from utils.github_helper import github_helper
from utils.llm_client import llm_client
from config.config import config


class Evaluator:
    """Evaluator for student submissions."""
    
    def __init__(self):
        self.browser: Browser = None
    
    async def init_browser(self):
        """Initialize Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
    
    async def close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()
    
    def check_repo_created_after_task(self, repo: Repo, task: Task) -> Dict[str, Any]:
        """Check if repository was created after task was sent."""
        check_name = "Repo created after task"
        
        try:
            # Extract repo name from URL
            repo_name = repo.repo_url.split("/")[-1]
            gh_repo = github_helper.gh.get_user(config.GITHUB_USERNAME).get_repo(repo_name)
            
            created_at = gh_repo.created_at
            task_sent_at = task.timestamp
            
            if created_at > task_sent_at:
                return {
                    "check": check_name,
                    "score": 1.0,
                    "reason": f"Repo created at {created_at}, task sent at {task_sent_at}",
                    "logs": ""
                }
            else:
                return {
                    "check": check_name,
                    "score": 0.0,
                    "reason": f"Repo created at {created_at} (before task at {task_sent_at})",
                    "logs": ""
                }
        except Exception as e:
            return {
                "check": check_name,
                "score": 0.0,
                "reason": f"Error: {str(e)}",
                "logs": str(e)
            }
    
    def check_license(self, repo: Repo) -> Dict[str, Any]:
        """Check if repository has MIT LICENSE."""
        check_name = "MIT LICENSE in root"
        
        try:
            repo_name = repo.repo_url.split("/")[-1]
            license_content = github_helper.get_file_content(
                repo_name,
                "LICENSE",
                repo.commit_sha
            )
            
            if license_content and "MIT" in license_content:
                return {
                    "check": check_name,
                    "score": 1.0,
                    "reason": "MIT LICENSE found",
                    "logs": ""
                }
            else:
                return {
                    "check": check_name,
                    "score": 0.0,
                    "reason": "MIT LICENSE not found or invalid",
                    "logs": ""
                }
        except Exception as e:
            return {
                "check": check_name,
                "score": 0.0,
                "reason": f"Error: {str(e)}",
                "logs": str(e)
            }
    
    def check_readme_quality(self, repo: Repo) -> Dict[str, Any]:
        """Check README.md quality using LLM."""
        check_name = "README.md quality"
        
        try:
            repo_name = repo.repo_url.split("/")[-1]
            readme_content = github_helper.get_file_content(
                repo_name,
                "README.md",
                repo.commit_sha
            )
            
            if not readme_content:
                return {
                    "check": check_name,
                    "score": 0.0,
                    "reason": "README.md not found",
                    "logs": ""
                }
            
            prompt = f"""Evaluate the quality of this README.md file on a scale of 0.0 to 1.0.

Criteria:
- Has clear title and description (0.2)
- Includes setup instructions (0.2)
- Includes usage instructions (0.2)
- Has code explanation (0.2)
- Mentions license (0.1)
- Professional formatting (0.1)

README.md content:
{readme_content[:2000]}

Respond with ONLY a JSON object:
{{"score": 0.0-1.0, "reason": "brief explanation"}}
"""
            
            response = llm_client.generate_code(prompt)
            # Parse JSON from response
            import json
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "check": check_name,
                    "score": float(result.get("score", 0.0)),
                    "reason": result.get("reason", ""),
                    "logs": response
                }
            else:
                return {
                    "check": check_name,
                    "score": 0.5,
                    "reason": "Could not parse LLM response",
                    "logs": response
                }
        
        except Exception as e:
            return {
                "check": check_name,
                "score": 0.0,
                "reason": f"Error: {str(e)}",
                "logs": str(e)
            }
    
    def check_code_quality(self, repo: Repo) -> Dict[str, Any]:
        """Check code quality using LLM."""
        check_name = "Code quality"
        
        try:
            repo_name = repo.repo_url.split("/")[-1]
            html_content = github_helper.get_file_content(
                repo_name,
                "index.html",
                repo.commit_sha
            )
            
            if not html_content:
                return {
                    "check": check_name,
                    "score": 0.0,
                    "reason": "index.html not found",
                    "logs": ""
                }
            
            prompt = f"""Evaluate the quality of this code on a scale of 0.0 to 1.0.

Criteria:
- Clean, readable code (0.3)
- Proper structure and organization (0.2)
- Error handling (0.2)
- Comments/documentation (0.1)
- Best practices followed (0.2)

Code content:
{html_content[:3000]}

Respond with ONLY a JSON object:
{{"score": 0.0-1.0, "reason": "brief explanation"}}
"""
            
            response = llm_client.generate_code(prompt)
            import json
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "check": check_name,
                    "score": float(result.get("score", 0.0)),
                    "reason": result.get("reason", ""),
                    "logs": response
                }
            else:
                return {
                    "check": check_name,
                    "score": 0.5,
                    "reason": "Could not parse LLM response",
                    "logs": response
                }
        
        except Exception as e:
            return {
                "check": check_name,
                "score": 0.0,
                "reason": f"Error: {str(e)}",
                "logs": str(e)
            }
    
    async def check_dynamic(self, repo: Repo, checks: List[str]) -> List[Dict[str, Any]]:
        """Run dynamic checks using Playwright."""
        results = []
        
        try:
            page = await self.browser.new_page()
            await page.goto(repo.pages_url, timeout=config.PLAYWRIGHT_TIMEOUT)
            
            for check in checks:
                check_result = await self._evaluate_check(page, check)
                results.append(check_result)
            
            await page.close()
        
        except Exception as e:
            results.append({
                "check": "Dynamic checks",
                "score": 0.0,
                "reason": f"Error loading page: {str(e)}",
                "logs": str(e)
            })
        
        return results
    
    async def _evaluate_check(self, page: Page, check: str) -> Dict[str, Any]:
        """Evaluate a single check."""
        # Check if it's a JS check
        if check.startswith("js:"):
            js_code = check[3:].strip()
            check_name = f"JS: {js_code[:50]}..."
            
            try:
                result = await page.evaluate(js_code)
                if result:
                    return {
                        "check": check_name,
                        "score": 1.0,
                        "reason": "Check passed",
                        "logs": f"Result: {result}"
                    }
                else:
                    return {
                        "check": check_name,
                        "score": 0.0,
                        "reason": "Check failed",
                        "logs": f"Result: {result}"
                    }
            except Exception as e:
                return {
                    "check": check_name,
                    "score": 0.0,
                    "reason": f"Error: {str(e)}",
                    "logs": str(e)
                }
        else:
            # Text-based check
            return {
                "check": check,
                "score": 0.5,
                "reason": "Manual review required",
                "logs": ""
            }
    
    async def evaluate_repo(self, repo: Repo, task: Task, db: Session):
        """Evaluate a single repository."""
        print(f"\nEvaluating {repo.email} - {repo.task} (Round {repo.round})")
        
        results = []
        
        # Static checks
        results.append(self.check_repo_created_after_task(repo, task))
        results.append(self.check_license(repo))
        results.append(self.check_readme_quality(repo))
        results.append(self.check_code_quality(repo))
        
        # Dynamic checks
        dynamic_results = await self.check_dynamic(repo, task.checks)
        results.extend(dynamic_results)
        
        # Save results to database
        for result_data in results:
            result = Result(
                timestamp=datetime.utcnow(),
                email=repo.email,
                task=repo.task,
                round=repo.round,
                repo_url=repo.repo_url,
                commit_sha=repo.commit_sha,
                pages_url=repo.pages_url,
                check=result_data["check"],
                score=result_data["score"],
                reason=result_data["reason"],
                logs=result_data["logs"]
            )
            db.add(result)
        
        db.commit()
        
        # Print summary
        total_score = sum(r["score"] for r in results) / len(results) if results else 0
        print(f"  Overall score: {total_score:.2f}")
        for r in results:
            status = "✓" if r["score"] >= 0.7 else "✗"
            print(f"  {status} {r['check']}: {r['score']:.2f} - {r['reason']}")


async def evaluate_all():
    """Evaluate all submitted repositories."""
    init_db()
    evaluator = Evaluator()
    await evaluator.init_browser()
    
    try:
        with get_db() as db:
            # Get all repos that haven't been evaluated yet
            repos = db.query(Repo).all()
            
            print(f"Found {len(repos)} repositories to evaluate")
            
            for repo in repos:
                # Check if already evaluated
                existing_results = db.query(Result).filter(
                    Result.email == repo.email,
                    Result.task == repo.task,
                    Result.round == repo.round
                ).count()
                
                if existing_results > 0:
                    print(f"Skipping {repo.email} - {repo.task} (already evaluated)")
                    continue
                
                # Get corresponding task
                task = db.query(Task).filter(
                    Task.email == repo.email,
                    Task.task == repo.task,
                    Task.round == repo.round
                ).first()
                
                if not task:
                    print(f"Warning: No task found for {repo.email} - {repo.task}")
                    continue
                
                await evaluator.evaluate_repo(repo, task, db)
    
    finally:
        await evaluator.close_browser()
    
    print("\n✓ Evaluation complete!")


if __name__ == "__main__":
    asyncio.run(evaluate_all())
