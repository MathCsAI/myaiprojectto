"""GitHub API helper functions."""
import time
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
    
    def push_files(self, repo_name: str, files: Dict[str, str]) -> str:
        """Push files to repository and return commit SHA."""
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
            
            # Add remote and push
            origin = repo.create_remote("origin", repo_url)
            origin.push(refspec="master:main")
            
            return commit.hexsha
        
        except Exception as e:
            raise Exception(f"Failed to push files: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def enable_github_pages(self, repo_name: str, branch: str = "main") -> str:
        """Enable GitHub Pages for a repository."""
        try:
            self._ensure_client()
            user = self.gh.get_user()
            repo = user.get_repo(repo_name)
            # Use the GitHub REST API to set the pages source
            # See: https://docs.github.com/en/rest/pages/pages?apiVersion=2022-11-28#update-information-about-a-github-pages-site
            repo._requester.requestJson(
                "PUT",
                f"/repos/{self.username}/{repo_name}/pages",
                input={
                    "source": {"branch": branch, "path": "/"}
                }
            )
            pages_url = f"https://{self.username}.github.io/{repo_name}/"
            return pages_url
        except GithubException as e:
            if hasattr(e, "status") and e.status == 409:  # Pages already enabled
                return f"https://{self.username}.github.io/{repo_name}/"
            raise Exception(f"Failed to enable GitHub Pages: {str(e)}")
    
    def wait_for_pages(self, pages_url: str, timeout: int = 300) -> bool:
        """Wait for GitHub Pages to be available."""
        import requests
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(pages_url, timeout=10)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            
            time.sleep(10)
        
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


# Singleton instance (no immediate GH API initialization)
github_helper = GitHubHelper()
