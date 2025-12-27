"""
Base OPLAB API Client

Provides HTTP request methods with authentication, retry logic, and error handling.
"""
import os
import requests
import time
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

from .exceptions import (
    OPLABException,
    OPLABUnauthorizedError,
    OPLABPaymentRequiredError,
    OPLABForbiddenError,
    OPLABNotFoundError,
    OPLABPreconditionFailedError,
    OPLABUnprocessableEntityError,
    OPLABRateLimitError,
    OPLABServerError,
)

load_dotenv()


class OPLABClient:
    """Base client for OPLAB API v3."""
    
    BASE_URL = "https://api.oplab.com.br/v3"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize OPLAB client.
        
        Args:
            access_token: API access token. If None, reads from OPLAB_ACCESS_TOKEN env var.
            
        Raises:
            ValueError: If access token is not provided and not found in environment.
        """
        self.access_token = access_token or os.getenv('OPLAB_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError(
                "OPLAB_ACCESS_TOKEN must be provided or set as environment variable"
            )
        
        self.headers = {
            'Access-Token': self.access_token
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        max_retries: int = 3,
        delay: int = 5,
        timeout: int = 30
    ) -> Optional[Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint (without base URL).
            params: Query parameters.
            data: Request body data.
            max_retries: Maximum number of retry attempts.
            delay: Delay between retries in seconds.
            timeout: Request timeout in seconds.
            
        Returns:
            Response JSON data or None if request fails.
            
        Raises:
            OPLABUnauthorizedError: If authentication fails (401).
            OPLABPaymentRequiredError: If subscription expired (402).
            OPLABForbiddenError: If plan doesn't allow access (403).
            OPLABNotFoundError: If resource not found (404).
            OPLABPreconditionFailedError: If action requirements not met (412).
            OPLABUnprocessableEntityError: If request cannot be processed (422).
            OPLABRateLimitError: If rate limit exceeded (429).
            OPLABServerError: If server error occurs (500, 503).
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=timeout
                )
                
                # Handle successful responses
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 204:
                    return None  # No content
                
                # Handle error responses
                elif response.status_code == 400:
                    error_msg = response.json().get('error', 'Bad Request') if response.content else 'Bad Request'
                    raise OPLABException(f"Bad Request: {error_msg}")
                elif response.status_code == 401:
                    raise OPLABUnauthorizedError("Unauthorized: Invalid access token")
                elif response.status_code == 402:
                    raise OPLABPaymentRequiredError("Payment Required: Subscription expired")
                elif response.status_code == 403:
                    raise OPLABForbiddenError("Forbidden: Plan doesn't allow access to this resource")
                elif response.status_code == 404:
                    raise OPLABNotFoundError(f"Not Found: {endpoint}")
                elif response.status_code == 412:
                    raise OPLABPreconditionFailedError("Precondition Failed: Action requirements not met")
                elif response.status_code == 422:
                    error_msg = response.json().get('error', 'Unprocessable Entity') if response.content else 'Unprocessable Entity'
                    raise OPLABUnprocessableEntityError(f"Unprocessable Entity: {error_msg}")
                elif response.status_code == 429:
                    raise OPLABRateLimitError("Too Many Requests: Rate limit exceeded")
                elif response.status_code in (500, 503):
                    raise OPLABServerError(f"Server Error ({response.status_code}): {response.text}")
                else:
                    response.raise_for_status()
                    
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed after {max_retries} attempts: {str(e)}")
                    raise OPLABException(f"Request failed after {max_retries} attempts: {str(e)}")
            except (OPLABException, OPLABUnauthorizedError, OPLABPaymentRequiredError, 
                    OPLABForbiddenError, OPLABNotFoundError, OPLABPreconditionFailedError,
                    OPLABUnprocessableEntityError, OPLABRateLimitError, OPLABServerError):
                # Re-raise OPLAB exceptions immediately (don't retry)
                raise
        
        return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Optional[Any]:
        """Make GET request."""
        return self._request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Optional[Any]:
        """Make POST request."""
        return self._request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Optional[Any]:
        """Make PUT request."""
        return self._request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Optional[Any]:
        """Make DELETE request."""
        return self._request('DELETE', endpoint, **kwargs)

