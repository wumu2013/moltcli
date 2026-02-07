"""Comment core logic."""

from typing import Optional
from ..utils.api_client import MoltbookClient


class CommentCore:
    """Handle comment operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def create(
        self,
        post_id: str,
        content: str,
        parent_id: Optional[str] = None,
    ) -> dict:
        """Create a comment on a post."""
        data = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id
        return self._client.post(f"/posts/{post_id}/comments", json_data=data)

    def get(self, comment_id: str) -> dict:
        """Get a comment by ID."""
        return self._client.get(f"/comments/{comment_id}")

    def delete(self, comment_id: str) -> dict:
        """Delete a comment."""
        return self._client.delete(f"/comments/{comment_id}")

    def list_by_post(self, post_id: str, limit: int = 50) -> dict:
        """List comments for a post."""
        return self._client.get(f"/posts/{post_id}/comments", params={"limit": limit})
