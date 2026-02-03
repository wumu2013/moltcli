"""Vote core logic."""
from ..utils.api_client import MoltbookClient


class VoteCore:
    """Handle vote operations."""

    UP = "up"
    DOWN = "down"

    def __init__(self, client: MoltbookClient):
        self._client = client

    def upvote(self, item_id: str, type_: str = "post") -> dict:
        """Upvote a post or comment."""
        return self._vote(item_id, self.UP, type_)

    def downvote(self, item_id: str, type_: str = "post") -> dict:
        """Downvote a post or comment."""
        return self._vote(item_id, self.DOWN, type_)

    def _vote(self, item_id: str, direction: str, type_: str) -> dict:
        """Internal vote method.

        Endpoints from skill.md:
        - POST /posts/{id}/upvote
        - POST /posts/{id}/downvote
        - POST /comments/{id}/upvote
        - POST /comments/{id}/downvote
        """
        direction_full = "upvote" if direction == "up" else "downvote"
        if type_ == "post":
            endpoint = f"/posts/{item_id}/{direction_full}"
        else:
            endpoint = f"/comments/{item_id}/{direction_full}"
        return self._client.post(endpoint)

    def upvote_comment(self, comment_id: str) -> dict:
        """Upvote a comment. Shortcut for: upvote(comment_id, type='comment')"""
        return self._vote(comment_id, self.UP, "comment")

    def downvote_comment(self, comment_id: str) -> dict:
        """Downvote a comment. Shortcut for: downvote(comment_id, type='comment')"""
        return self._vote(comment_id, self.DOWN, "comment")
