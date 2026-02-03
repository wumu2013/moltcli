"""Submolts core logic."""
from typing import Optional
from ..utils.api_client import MoltbookClient


class SubmoltsCore:
    """Handle submolt operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def list(self, limit: int = 50) -> dict:
        """List all submolts."""
        return self._client.get("/submolts", params={"limit": limit})

    def get(self, name: str) -> dict:
        """Get a submolt by name."""
        return self._client.get(f"/submolts/{name}")

    def create(self, name: str, display_name: str, description: str = "") -> dict:
        """Create a new submolt.

        Args:
            name: Unique name (e.g., "aithoughts")
            display_name: Display name (e.g., "AI Thoughts")
            description: Submolt description
        """
        return self._client.post("/submolts", json_data={
            "name": name,
            "display_name": display_name,
            "description": description,
        })

    def feed(self, name: str, sort: str = "hot", limit: int = 20) -> dict:
        """Get feed from a specific submolt.

        Args:
            name: Submolt name
            sort: Sort order (hot, new, top, rising)
            limit: Max posts to return
        """
        return self._client.get(
            f"/submolts/{name}/feed",
            params={"sort": sort, "limit": limit}
        )

    def subscribe(self, name: str) -> dict:
        """Subscribe to a submolt."""
        return self._client.post(f"/submolts/{name}/subscribe?action=subscribe")

    def unsubscribe(self, name: str) -> dict:
        """Unsubscribe from a submolt."""
        return self._client.delete(f"/submolts/{name}/subscribe")

    def get_subscribed(self) -> dict:
        """Get user's subscribed submolts."""
        return self._client.get("/user/subscriptions")

    def trending(self, limit: int = 10) -> dict:
        """Get trending submolts."""
        return self._client.get("/submolts/trending", params={"limit": limit})
