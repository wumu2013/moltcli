"""Moltbook API client."""
import requests
from typing import Optional

from .errors import RateLimitError, AuthError, NotFoundError


class MoltbookClient:
    """HTTP client for Moltbook API."""

    BASE_URL = "https://www.moltbook.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request and handle errors."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=self.headers,
            timeout=30,
        )

        if not response.ok:
            self._handle_error_response(response, endpoint)

        return response.json()

    def _handle_error_response(self, response, endpoint: str = ""):
        """Handle API error response."""
        status = response.status_code
        try:
            body = response.json()
            message = body.get("error") or body.get("message") or response.text
            retry_after = body.get("retry_after_seconds") or body.get("retry_after")
        except Exception:
            message = response.text or f"API error {status}"
            retry_after = None

        # Extract rate limit info from headers if not in body
        limit = None
        remaining = None
        if status == 429:
            if "Retry-After" in response.headers:
                retry_after = int(response.headers["Retry-After"])
            if "X-RateLimit-Limit" in response.headers:
                limit = int(response.headers["X-RateLimit-Limit"])
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
            raise RateLimitError(message=message, retry_after=retry_after, limit=limit, remaining=remaining)

        # Authentication errors (401, 403)
        if status in (401, 403):
            raise AuthError(message)

        # Not found (404) - parse error message to determine type
        if status == 404:
            msg_lower = message.lower()
            if "submolt" in msg_lower or "m/" in msg_lower:
                raise NotFoundError("submolt")
            elif "comment" in msg_lower:
                raise NotFoundError("comment")
            elif "/posts/" in endpoint or "/post/" in endpoint:
                raise NotFoundError("post")
            else:
                raise NotFoundError("resource")

        # Other errors (400, 405, 500, etc.)
        raise Exception(message)

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """GET request."""
        return self._request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, json_data: Optional[dict] = None
    ) -> dict:
        """POST request."""
        return self._request("POST", endpoint, json_data=json_data)

    def delete(self, endpoint: str) -> dict:
        """DELETE request."""
        return self._request("DELETE", endpoint)

    def patch(self, endpoint: str, json_data: Optional[dict] = None) -> dict:
        """PATCH request."""
        return self._request("PATCH", endpoint, json_data=json_data)
