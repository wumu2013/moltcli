"""Post core logic."""
from typing import Optional
from ..utils.api_client import MoltbookClient
from ..utils import normalize_submolt_name


class PostCore:
    """Handle post operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def create(
        self,
        submolt: str,
        title: str,
        content: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
        """Create a new post."""
        submolt = normalize_submolt_name(submolt)
        data = {"submolt": submolt, "title": title}
        if content:
            data["content"] = content
        if url:
            data["url"] = url
        return self._client.post("/posts", json_data=data)

    def get(self, post_id: str) -> dict:
        """Get a post by ID."""
        return self._client.get(f"/posts/{post_id}")

    def delete(self, post_id: str) -> dict:
        """Delete a post."""
        return self._client.delete(f"/posts/{post_id}")

    def list_by_submolt(
        self, submolt: str, limit: int = 20, offset: int = 0
    ) -> dict:
        """List posts in a submolt."""
        return self._client.get(
            f"/submolts/{submolt}/posts", params={"limit": limit, "offset": offset}
        )
