"""Retry helper with exponential backoff."""
import time
import requests
from typing import Dict, Any, Optional
from config.config import config


def retry_request(
    url: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = None
) -> requests.Response:
    """
    Retry HTTP request with exponential backoff.
    
    Args:
        url: URL to send request to
        method: HTTP method (GET, POST, etc.)
        json_data: JSON data to send
        headers: HTTP headers
        max_retries: Maximum number of retries (uses config if None)
    
    Returns:
        Response object
    
    Raises:
        Exception if all retries fail
    """
    if max_retries is None:
        max_retries = config.MAX_RETRIES
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=json_data, headers=headers, timeout=30)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if successful
            if response.status_code == 200:
                return response
            
            last_error = f"HTTP {response.status_code}: {response.text}"
            
            # If not the last attempt, wait and retry
            if attempt < max_retries:
                delay = config.RETRY_DELAYS[min(attempt, len(config.RETRY_DELAYS) - 1)]
                print(f"Request failed, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            
            if attempt < max_retries:
                delay = config.RETRY_DELAYS[min(attempt, len(config.RETRY_DELAYS) - 1)]
                print(f"Request error: {e}, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
    
    raise Exception(f"Failed after {max_retries} retries. Last error: {last_error}")


def send_evaluation_response(
    evaluation_url: str,
    data: Dict[str, Any]
) -> bool:
    """
    Send evaluation response with retry logic.
    
    Args:
        evaluation_url: URL to send evaluation data to
        data: Evaluation data
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = retry_request(evaluation_url, method="POST", json_data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send evaluation response: {e}")
        return False
