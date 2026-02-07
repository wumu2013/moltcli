"""Search core logic."""
from ..utils.api_client import MoltbookClient


class SearchCore:
    """Handle search operations."""

    def __init__(self, client: MoltbookClient):
        self._client = client

    def search(
        self,
        query: str,
        type_: str = "posts",
        limit: int = 20,
    ) -> dict:
        """Search posts and users."""
        return self._client.get(
            "/search", params={"q": query, "type": type_, "limit": limit}
        )

    def search_posts(self, query: str, limit: int = 20) -> dict:
        """Search posts only."""
        return self.search(query, type_="posts", limit=limit)

    def search_users(self, query: str, limit: int = 20) -> dict:
        """Search users only."""
        return self.search(query, type_="users", limit=limit)
