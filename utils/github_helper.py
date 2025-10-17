"""GitHub API helper functions."""
import time
from urllib.parse import urlparse
from typing import Dict, Optional
from github import Github, GithubException
from git import Repo as GitRepo
import os
import tempfile
import shutil
from config.config import config


class GitHubHelper:
    """Helper class for GitHub operations.

    This helper now lazily initializes the GitHub client so the app can start
    even when GITHUB_TOKEN is not provided (e.g., on Hugging Face Spaces).
    GitHub operations will raise a clear error if credentials are missing.
    """

    def __init__(self):
        # Defer client creation to allow runtime without GH credentials
        self.token = (getattr(config, "GITHUB_TOKEN", "") or os.getenv("GITHUB_TOKEN", "")).strip()
        self.username = (getattr(config, "GITHUB_USERNAME", "") or os.getenv("GITHUB_USERNAME", "")).strip()
        self.gh: Optional[Github] = None

    @staticmethod
    def _is_placeholder(value: str) -> bool:
        v = (value or "").strip().lower()
        return not v or v.startswith("your_") or v in {"username", "token"}

    def _ensure_client(self):
        """Ensure GitHub client exists and credentials are present."""
        if self.gh is not None:
            return
        if self._is_placeholder(self.token):
            raise RuntimeError(
                "GitHub token is not configured. Set GITHUB_TOKEN as a secret/env to use GitHub features."
            )
        try:
            self.gh = Github(self.token)
        except AssertionError:
            # PyGithub asserts non-empty token; convert to helpful error
            raise RuntimeError("Invalid or empty GITHUB_TOKEN provided. Please configure a valid token.")

    def has_credentials(self) -> bool:
        """Return True if both token and username appear configured."""
        return not self._is_placeholder(self.token) and not self._is_placeholder(self.username)

    def credentials_status(self) -> Dict[str, str]:
        """Return a structured status of credential configuration without revealing secrets."""
        return {
            "username_configured": "yes" if not self._is_placeholder(self.username) else "no",
            "token_configured": "yes" if not self._is_placeholder(self.token) else "no",
            "username": self.username if self.username and not self._is_placeholder(self.username) else "",
        }
    
    def create_repo(self, repo_name: str, description: str = "") -> str:
        """Create a new GitHub repository."""
        try:
            self._ensure_client()
            user = self.gh.get_user()
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=False,
                auto_init=False
            )
            return repo.html_url
        except GithubException as e:
            if e.status == 422:  # Repository already exists
                # Delete and recreate
                try:
                    user = self.gh.get_user()
                    existing_repo = user.get_repo(repo_name)
                    existing_repo.delete()
                    time.sleep(2)  # Wait for deletion
                    return self.create_repo(repo_name, description)
                except Exception:
                    raise Exception(f"Repository {repo_name} already exists")
            raise Exception(f"Failed to create repository: {str(e)}")
    
    def push_files(self, repo_name: str, files: Dict[str, str], also_gh_pages: bool = False) -> str:
        """Push files to repository and return commit SHA.
        
        Args:
            repo_name: Name of the repository
            files: Dict of filename -> content
            also_gh_pages: If True, also push to gh-pages branch for GitHub Pages
        
        Returns:
            Commit SHA of the main branch push
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            self._ensure_client()
            if self._is_placeholder(self.username):
                raise RuntimeError("GitHub username is not configured. Set GITHUB_USERNAME to use GitHub features.")
            # Clone the repository
            repo_url = f"https://{self.token}@github.com/{self.username}/{repo_name}.git"
            repo = GitRepo.init(temp_dir)
            
            # Create files
            for filename, content in files.items():
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            # Git operations
            repo.index.add(list(files.keys()))
            commit = repo.index.commit("Initial commit")
            
            # Add remote and push to main with retry logic for network issues
            origin = repo.create_remote("origin", repo_url)
            
            # Retry git push up to 3 times for DNS/network failures
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    origin.push(refspec="master:main")
                    break  # Success, exit retry loop
                except Exception as push_error:
                    error_msg = str(push_error)
                    if "Could not resolve host" in error_msg or "unable to access" in error_msg:
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # 1s, 2s, 4s
                            print(f"Git push failed (DNS/network issue), retrying in {wait_time}s... (attempt {attempt+1}/{max_retries})")
                            import time
                            time.sleep(wait_time)
                            continue
                    # Not a retryable error or max retries reached
                    raise
            
            # Also push to gh-pages if requested
            if also_gh_pages:
                print(f"Pushing to gh-pages branch for automatic GitHub Pages deployment")
                try:
                    # Create gh-pages branch from current state
                    repo.git.checkout('-b', 'gh-pages')
                    
                    # Retry gh-pages push with same logic
                    for attempt in range(max_retries):
                        try:
                            origin.push(refspec="gh-pages:gh-pages", force=True)
                            print(f"Successfully pushed to gh-pages branch")
                            break
                        except Exception as gh_push_error:
                            error_msg = str(gh_push_error)
                            if "Could not resolve host" in error_msg or "unable to access" in error_msg:
                                if attempt < max_retries - 1:
                                    wait_time = 2 ** attempt
                                    print(f"gh-pages push failed (DNS/network issue), retrying in {wait_time}s... (attempt {attempt+1}/{max_retries})")
                                    import time
                                    time.sleep(wait_time)
                                    continue
                            raise
                except Exception as gh_error:
                    print(f"Warning: Failed to push gh-pages branch: {gh_error}")
            
            return commit.hexsha
        
        except Exception as e:
            raise Exception(f"Failed to push files: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def enable_github_pages(self, repo_name: str, branch: str = "main") -> str:
        """Enable GitHub Pages for a repository.
        
        Tries to enable Pages via API, but returns the expected URL regardless of success.
        GitHub may auto-enable Pages for repos with gh-pages branch.
        """
        pages_url = f"https://{self.username}.github.io/{repo_name}/"
        
        try:
            self._ensure_client()
            user = self.gh.get_user()
            repo = user.get_repo(repo_name)
            
            # Try creating Pages (POST)
            try:
                print(f"Attempting to create GitHub Pages for {repo_name} via API...")
                repo._requester.requestJson(
                    "POST",
                    f"/repos/{self.username}/{repo_name}/pages",
                    input={
                        "source": {"branch": branch, "path": "/"}
                    }
                )
                print(f"✓ GitHub Pages created successfully for {repo_name}")
                return pages_url
            except GithubException as create_error:
                if hasattr(create_error, "status"):
                    if create_error.status == 409:
                        # Pages already exists
                        print(f"✓ GitHub Pages already exists for {repo_name}")
                        return pages_url
                    elif create_error.status == 404:
                        print(f"⚠ Pages API endpoint not available (404) - may need manual enablement or token lacks permissions")
                    elif create_error.status == 403:
                        print(f"⚠ Pages API forbidden (403) - token lacks required permissions (Pages/Administration)")
                    else:
                        print(f"⚠ Pages API error {create_error.status}: {str(create_error)}")
                else:
                    print(f"⚠ Pages API error: {str(create_error)}")
                
                # If gh-pages branch exists, GitHub may auto-enable Pages
                print(f"ℹ If gh-pages branch was pushed, GitHub will auto-enable Pages within a few minutes")
                return pages_url
                
        except Exception as e:
            print(f"⚠ Unexpected error enabling GitHub Pages: {str(e)}")
            print(f"ℹ Pages URL will be: {pages_url}")
            return pages_url
    
    def wait_for_pages(self, pages_url: str, timeout: int = 300) -> bool:
        """Wait for GitHub Pages to be available.

        Strategy:
        1) Infer repo name from pages_url and trigger a Pages build via REST API (if needed)
        2) Poll the latest Pages build status until built/succeeded
        3) Then poll the public pages_url until it returns HTTP 200
        """
        import requests
        start_time = time.time()

        # Infer repo name from pages_url: https://<user>.github.io/<repo_name>/
        repo_name = None
        try:
            path = urlparse(pages_url).path  # e.g., '/repo_name/'
            parts = [p for p in path.split('/') if p]
            if parts:
                repo_name = parts[0]
        except Exception:
            repo_name = None

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "llm-code-deployment-bot"
        }

        # Step 1 & 2: Trigger and/or poll the Pages build status
        if repo_name:
            build_url = f"https://api.github.com/repos/{self.username}/{repo_name}/pages/builds/latest"
            trigger_url = f"https://api.github.com/repos/{self.username}/{repo_name}/pages/builds"
            last_status = None
            while time.time() - start_time < timeout:
                try:
                    resp = requests.get(build_url, headers=headers, timeout=10)
                    if resp.status_code == 404:
                        # No build yet; trigger one
                        requests.post(trigger_url, headers=headers, timeout=10)
                        last_status = "triggered"
                    elif resp.ok:
                        data = resp.json() or {}
                        status = (data.get("status") or data.get("build") or "").lower()
                        last_status = status
                        if status in {"built", "succeeded", "success"}:
                            break
                        # If it's building/queued, continue polling
                    else:
                        # Non-OK; wait and retry
                        pass
                except Exception:
                    pass
                time.sleep(5)

        # Step 3: Poll the public URL until it returns 200
        while time.time() - start_time < timeout:
            try:
                response = requests.get(pages_url, timeout=10)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(5)

        return False
    
    def check_secrets_in_repo(self, repo_name: str) -> bool:
        """Check if repository contains secrets (basic check)."""
        try:
            self._ensure_client()
            user = self.gh.get_user()
            repo = user.get_repo(repo_name)
            
            # Check for common secret patterns in files
            contents = repo.get_contents("")
            
            dangerous_patterns = [
                "api_key",
                "secret_key",
                "password",
                "token",
                "sk-",  # OpenAI API key prefix
            ]
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    try:
                        content = file_content.decoded_content.decode("utf-8").lower()
                        for pattern in dangerous_patterns:
                            if pattern in content:
                                # Basic check - might need more sophisticated detection
                                return True
                    except Exception:
                        continue
            
            return False
        
        except Exception as e:
            print(f"Error checking for secrets: {str(e)}")
            return False
    
    def get_file_content(self, repo_name: str, file_path: str, commit_sha: str = None) -> Optional[str]:
        """Get content of a file from repository."""
        try:
            self._ensure_client()
            user = self.gh.get_user()
            repo = user.get_repo(repo_name)
            
            if commit_sha:
                file_content = repo.get_contents(file_path, ref=commit_sha)
            else:
                file_content = repo.get_contents(file_path)
            
            return file_content.decoded_content.decode("utf-8")
        
        except Exception as e:
            print(f"Error getting file content: {str(e)}")
            return None

    def get_pages_build_status(self, repo_name: str) -> Dict[str, Optional[str]]:
        """Get latest GitHub Pages build status for a repository.

        Returns a dict with keys: status, created_at, updated_at, url, error
        """
        import requests
        try:
            self._ensure_client()
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "llm-code-deployment-bot"
            }
            build_url = f"https://api.github.com/repos/{self.username}/{repo_name}/pages/builds/latest"
            resp = requests.get(build_url, headers=headers, timeout=10)
            if resp.status_code == 404:
                return {"status": "not_found", "created_at": None, "updated_at": None, "url": None, "error": None}
            if not resp.ok:
                return {"status": "unknown", "created_at": None, "updated_at": None, "url": None, "error": f"HTTP {resp.status_code}"}
            data = resp.json() or {}
            return {
                "status": str((data.get("status") or data.get("build") or "")).lower(),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "url": data.get("url"),
                "error": (data.get("error") or {}).get("message") if isinstance(data.get("error"), dict) else None
            }
        except Exception as e:
            return {"status": "error", "created_at": None, "updated_at": None, "url": None, "error": str(e)}


# Singleton instance (no immediate GH API initialization)
github_helper = GitHubHelper()
