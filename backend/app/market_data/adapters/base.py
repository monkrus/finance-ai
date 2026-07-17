import httpx
from typing import Any, Dict, Optional
from app.core.exceptions import FinPilotException

class BaseAdapter:
    """
    Base HTTP client logic for all Market Data Adapters.
    Encapsulates connection pooling, timeouts, and JSON parsing.
    """
    def __init__(self, base_url: str, api_key: str = "", timeout: int = 10):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Handle standard HTTP errors
                status = e.response.status_code
                if status == 404:
                    return None
                if status == 429:
                    raise FinPilotException(status_code=429, message=f"Rate limit exceeded for provider at {url}")
                if status == 401 or status == 403:
                    raise FinPilotException(status_code=500, message=f"Authentication error with external provider.")
                raise FinPilotException(status_code=502, message=f"External provider error: {status}")
            except httpx.RequestError as e:
                raise FinPilotException(status_code=504, message=f"Failed to connect to external provider: {str(e)}")
