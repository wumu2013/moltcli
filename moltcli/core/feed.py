"""Feed core logic."""
from typing import Optional
from ..utils.api_client import MoltbookClient


class FeedCore:
    """Handle feed operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def get(
        self,
        sort: str = "hot",
        limit: int = 20,
        submolt: Optional[str] = None,
    ) -> dict:
        """Get feed posts."""
        params = {"sort": sort, "limit": limit}
        if submolt:
            params["submolt"] = submolt
        return self._client.get("/feed", params=params)

    def get_hot(self, limit: int = 20) -> dict:
        """Get hot posts."""
        return self.get(sort="hot", limit=limit)

    def get_new(self, limit: int = 20) -> dict:
        """Get newest posts."""
        return self.get(sort="new", limit=limit)
