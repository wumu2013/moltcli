"""Auth core logic."""
from ..utils.api_client import MoltbookClient


class AuthCore:
    """Handle authentication operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def whoami(self) -> dict:
        """Get current user info. Uses /agents/me endpoint."""
        return self._client.get("/agents/me")

    def verify(self) -> dict:
        """Verify API key is valid. Uses /agents/me endpoint."""
        return self._client.get("/agents/me")

    def refresh(self) -> dict:
        """Refresh authentication token."""
        return self._client.post("/auth/refresh")
