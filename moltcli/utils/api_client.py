"""Moltbook API client."""
import requests
from typing import Any, Optional

from .errors import RateLimitError, AuthError, NotFoundError, parse_rate_limit_from_response


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
        """Handle API error response with specific error types."""
        status = response.status_code
        response_text = response.text.strip()

        # Determine endpoint type for rate limit
        endpoint_type = "general"
        if "/posts" in endpoint or "/post" in endpoint:
            endpoint_type = "post"
        elif "/vote" in endpoint or "/upvote" in endpoint or "/downvote" in endpoint:
            endpoint_type = "vote"

        # Rate limit (429)
        if status == 429:
            retry_after, limit, remaining = parse_rate_limit_from_response(response)
            raise RateLimitError(
                retry_after=retry_after,
                limit=limit,
                remaining=remaining,
                endpoint_type=endpoint_type,
            )

        # Authentication errors (401, 403)
        if status in (401, 403):
            raise AuthError(f"Authentication failed: {response_text or 'No response body'}")

        # Not found (404)
        if status == 404:
            # Try to determine resource type from URL
            url = response.request.url
            if "/posts/" in url:
                raise NotFoundError("post")
            elif "/submolts/" in url:
                raise NotFoundError("submolt")
            else:
                raise NotFoundError("resource")

        # Method not allowed (405)
        if status == 405:
            # Try to get error message from response body
            try:
                error_body = response.json()
                error_msg = error_body.get("error", error_body.get("message", response_text))
            except Exception:
                error_msg = response_text or f"Method not allowed for {endpoint}"
            raise Exception(f"API error {status}: {error_msg}")

        # Other errors
        raise Exception(f"API error {status}: {response_text or 'No response body'}")

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
