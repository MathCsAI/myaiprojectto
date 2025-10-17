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
    max_retries: int = None,
    timeout: int = 30
) -> requests.Response:
    """
    Retry HTTP request with exponential backoff.
    
    Args:
        url: URL to send request to
        method: HTTP method (GET, POST, etc.)
        json_data: JSON data to send
        headers: HTTP headers
        max_retries: Maximum number of retries (uses config if None)
        timeout: Request timeout in seconds (default 30)
    
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
                response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
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
        # Use longer timeout for evaluation callbacks (they might be slow)
        response = retry_request(
            evaluation_url, 
            method="POST", 
            json_data=data,
            timeout=90  # Increased from 30 to 90 seconds
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send evaluation response: {e}")
        print("Warning: Failed to send evaluation response")
        # Don't fail the entire task if evaluation callback fails
        return False
