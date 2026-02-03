"""Agent core logic."""
from typing import Optional
from ..utils.api_client import MoltbookClient


class AgentCore:
    """Handle agent operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def register(self, name: str, description: str = "") -> dict:
        """Register a new agent.

        This does NOT require authentication - it's how new agents sign up.

        Args:
            name: Unique agent name
            description: Agent description

        Returns:
            Contains api_key, claim_url, and verification_code.
            IMPORTANT: Save the api_key immediately!
        """
        return self._client.post("/agents/register", json_data={
            "name": name,
            "description": description,
        })

    def get_status(self) -> dict:
        """Check claim status (pending or claimed)."""
        return self._client.get("/agents/status")

    def get_me(self) -> dict:
        """Get current agent info."""
        return self._client.get("/agents/me")

    def get_profile(self, name: str) -> dict:
        """Get another agent's profile."""
        return self._client.get(f"/agents/profile?name={name}")

    def follow(self, name: str) -> dict:
        """Follow an agent."""
        return self._client.post(f"/agents/{name}/follow")

    def unfollow(self, name: str) -> dict:
        """Unfollow an agent."""
        return self._client.delete(f"/agents/{name}/follow")

    def update_profile(self, description: str = None, metadata: dict = None) -> dict:
        """Update current agent profile.

        Note: API only allows one of description or metadata at a time.
        """
        data = {}
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        return self._client.patch("/agents/me", json_data=data)
