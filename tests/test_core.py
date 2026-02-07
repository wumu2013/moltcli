"""Tests for agent core module."""

import pytest
from unittest.mock import Mock, patch


class TestAgentCore:
    """Test AgentCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        """Create mock client."""
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def agent_core(self, mock_client):
        """Create AgentCore instance."""
        from moltcli.core.agent import AgentCore

        return AgentCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_register(self, mock_request, agent_core):
        """Test agent registration."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "agent": {
                "api_key": "test_key",
                "claim_url": "https://test.com/claim",
                "verification_code": "test-123",
            }
        }
        mock_request.return_value = mock_response

        result = agent_core.register("TestAgent", "Test description")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["json"] == {
            "name": "TestAgent",
            "description": "Test description",
        }
        assert "api_key" in result["agent"]

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_status(self, mock_request, agent_core):
        """Test get claim status."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "pending_claim"}
        mock_request.return_value = mock_response

        result = agent_core.get_status()

        mock_request.assert_called_once()
        assert result["status"] == "pending_claim"

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_me(self, mock_request, agent_core):
        """Test get current agent info."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "name": "TestAgent",
            "description": "Test",
            "karma": 100,
        }
        mock_request.return_value = mock_response

        result = agent_core.get_me()

        mock_request.assert_called_once()
        assert result["name"] == "TestAgent"

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_profile(self, mock_request, agent_core):
        """Test get another agent's profile."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"name": "OtherAgent", "karma": 50}
        mock_request.return_value = mock_response

        result = agent_core.get_profile("OtherAgent")

        mock_request.assert_called_once()
        assert "name=OtherAgent" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_follow(self, mock_request, agent_core):
        """Test follow an agent."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = agent_core.follow("OtherAgent")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "OtherAgent/follow" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_unfollow(self, mock_request, agent_core):
        """Test unfollow an agent."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = agent_core.unfollow("OtherAgent")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"
        assert "OtherAgent/follow" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_update_profile_description(self, mock_request, agent_core):
        """Test update profile with description."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = agent_core.update_profile(description="New description")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["json"] == {"description": "New description"}

    @patch("moltcli.utils.api_client.requests.request")
    def test_update_profile_metadata(self, mock_request, agent_core):
        """Test update profile with metadata."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = agent_core.update_profile(metadata={"key": "value"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["json"] == {"metadata": {"key": "value"}}

    @patch("moltcli.utils.api_client.requests.request")
    def test_update_profile_both(self, mock_request, agent_core):
        """Test update profile with both description and metadata."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = agent_core.update_profile(description="New", metadata={"k": "v"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "description" in call_args.kwargs["json"]
        assert "metadata" in call_args.kwargs["json"]


class TestPostCore:
    """Test PostCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def post_core(self, mock_client):
        from moltcli.core.post import PostCore

        return PostCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_create_post_with_content(self, mock_request, post_core):
        """Test create post with content."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "new_post_123", "success": True}
        mock_request.return_value = mock_response

        result = post_core.create("startups", "Test Title", content="Test content")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["json"]["submolt"] == "startups"
        assert call_args.kwargs["json"]["title"] == "Test Title"
        assert call_args.kwargs["json"]["content"] == "Test content"

    @patch("moltcli.utils.api_client.requests.request")
    def test_create_post_with_url(self, mock_request, post_core):
        """Test create post with URL."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "new_post_123"}
        mock_request.return_value = mock_response

        result = post_core.create("news", "Interesting Link", url="https://example.com")

        call_args = mock_request.call_args
        assert call_args.kwargs["json"]["url"] == "https://example.com"
        assert "content" not in call_args.kwargs["json"]

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_post(self, mock_request, post_core):
        """Test get post by ID."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "post_123", "title": "Test"}
        mock_request.return_value = mock_response

        result = post_core.get("post_123")

        mock_request.assert_called_once()
        assert "post_123" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_delete_post(self, mock_request, post_core):
        """Test delete post."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = post_core.delete("post_123")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"

    @patch("moltcli.utils.api_client.requests.request")
    def test_list_by_submolt(self, mock_request, post_core):
        """Test list posts in submolt."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        result = post_core.list_by_submolt("startups", limit=10)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 10


class TestCommentCore:
    """Test CommentCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def comment_core(self, mock_client):
        from moltcli.core.comment import CommentCore

        return CommentCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_create_comment(self, mock_request, comment_core):
        """Test create comment on post."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "comment_123", "success": True}
        mock_request.return_value = mock_response

        result = comment_core.create("post_123", "Great post!")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "post_123" in call_args.kwargs["url"]
        assert call_args.kwargs["json"]["content"] == "Great post!"

    @patch("moltcli.utils.api_client.requests.request")
    def test_create_reply(self, mock_request, comment_core):
        """Test create reply to comment."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "reply_456"}
        mock_request.return_value = mock_response

        result = comment_core.create("post_123", "I agree!", parent_id="comment_123")

        call_args = mock_request.call_args
        assert "post_123" in call_args.kwargs["url"]
        assert call_args.kwargs["json"]["parent_id"] == "comment_123"

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_comment(self, mock_request, comment_core):
        """Test get comment by ID."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "comment_123", "content": "Test"}
        mock_request.return_value = mock_response

        result = comment_core.get("comment_123")

        assert "comment_123" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_delete_comment(self, mock_request, comment_core):
        """Test delete comment."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = comment_core.delete("comment_123")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"

    @patch("moltcli.utils.api_client.requests.request")
    def test_list_by_post(self, mock_request, comment_core):
        """Test list comments for post."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"comments": []}
        mock_request.return_value = mock_response

        result = comment_core.list_by_post("post_123", limit=20)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 20


class TestVoteCore:
    """Test VoteCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def vote_core(self, mock_client):
        from moltcli.core.vote import VoteCore

        return VoteCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_upvote_post(self, mock_request, vote_core):
        """Test upvote a post."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = vote_core.upvote("post_123", type_="post")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "post_123/upvote" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_downvote_post(self, mock_request, vote_core):
        """Test downvote a post."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = vote_core.downvote("post_123", type_="post")

        call_args = mock_request.call_args
        assert "post_123/downvote" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_upvote_comment(self, mock_request, vote_core):
        """Test upvote a comment."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = vote_core.upvote_comment("comment_123")

        call_args = mock_request.call_args
        assert "comment_123/upvote" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_downvote_comment(self, mock_request, vote_core):
        """Test downvote a comment."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = vote_core.downvote_comment("comment_123")

        call_args = mock_request.call_args
        assert "comment_123/downvote" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_upvote_with_type_comment(self, mock_request, vote_core):
        """Test upvote with explicit type='comment'."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = vote_core.upvote("comment_123", type_="comment")

        call_args = mock_request.call_args
        assert "comment_123/upvote" in str(call_args)


class TestSearchCore:
    """Test SearchCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def search_core(self, mock_client):
        from moltcli.core.search import SearchCore

        return SearchCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_search_posts(self, mock_request, search_core):
        """Test search posts."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"results": [{"id": "p1"}, {"id": "p2"}]}
        mock_request.return_value = mock_response

        result = search_core.search("AI", type_="posts", limit=10)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["q"] == "AI"
        assert call_args.kwargs["params"]["type"] == "posts"
        assert call_args.kwargs["params"]["limit"] == 10

    @patch("moltcli.utils.api_client.requests.request")
    def test_search_users(self, mock_request, search_core):
        """Test search users."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"results": [{"name": "user1"}]}
        mock_request.return_value = mock_response

        result = search_core.search("test", type_="users", limit=5)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["type"] == "users"

    @patch("moltcli.utils.api_client.requests.request")
    def test_search_posts_convenience(self, mock_request, search_core):
        """Test search_posts convenience method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"results": []}
        mock_request.return_value = mock_response

        search_core.search_posts("query", limit=15)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["type"] == "posts"

    @patch("moltcli.utils.api_client.requests.request")
    def test_search_users_convenience(self, mock_request, search_core):
        """Test search_users convenience method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"results": []}
        mock_request.return_value = mock_response

        search_core.search_users("query")

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["type"] == "users"


class TestFeedCore:
    """Test FeedCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def feed_core(self, mock_client):
        from moltcli.core.feed import FeedCore

        return FeedCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_feed_default(self, mock_request, feed_core):
        """Test get feed with defaults."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        feed_core.get()

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["sort"] == "hot"
        assert call_args.kwargs["params"]["limit"] == 20

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_feed_custom(self, mock_request, feed_core):
        """Test get feed with custom params."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        feed_core.get(sort="new", limit=10, submolt="ai")

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["sort"] == "new"
        assert call_args.kwargs["params"]["limit"] == 10
        assert call_args.kwargs["params"]["submolt"] == "ai"

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_hot(self, mock_request, feed_core):
        """Test get hot posts."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        feed_core.get_hot(limit=5)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["sort"] == "hot"
        assert call_args.kwargs["params"]["limit"] == 5

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_new(self, mock_request, feed_core):
        """Test get newest posts."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        feed_core.get_new(limit=15)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["sort"] == "new"
        assert call_args.kwargs["params"]["limit"] == 15


class TestAuthCore:
    """Test AuthCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def auth_core(self, mock_client):
        from moltcli.core.auth import AuthCore

        return AuthCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_whoami(self, mock_request, auth_core):
        """Test whoami. Uses /agents/me endpoint per skill.md."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "name": "TestAgent",
            "email": "test@example.com",
        }
        mock_request.return_value = mock_response

        result = auth_core.whoami()

        mock_request.assert_called_once()
        assert "/agents/me" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_verify(self, mock_request, auth_core):
        """Test verify API key. Uses /agents/me endpoint per skill.md."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"valid": True}
        mock_request.return_value = mock_response

        result = auth_core.verify()

        mock_request.assert_called_once()
        assert "/agents/me" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_refresh(self, mock_request, auth_core):
        """Test refresh token."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = auth_core.refresh()

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"


class TestSubmoltsCore:
    """Test SubmoltsCore class."""

    @pytest.fixture
    def mock_client(self, mock_api_key):
        from moltcli.utils.api_client import MoltbookClient

        return MoltbookClient(mock_api_key)

    @pytest.fixture
    def submolts_core(self, mock_client):
        from moltcli.core.submolts import SubmoltsCore

        return SubmoltsCore(mock_client)

    @patch("moltcli.utils.api_client.requests.request")
    def test_list(self, mock_request, submolts_core):
        """Test list submolts."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"submolts": [{"name": "ai"}]}
        mock_request.return_value = mock_response

        submolts_core.list(limit=10)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 10

    @patch("moltcli.utils.api_client.requests.request")
    def test_get(self, mock_request, submolts_core):
        """Test get submolt info."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"name": "ai", "display_name": "AI"}
        mock_request.return_value = mock_response

        result = submolts_core.get("ai")

        assert "ai" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_create(self, mock_request, submolts_core):
        """Test create submolt."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True, "name": "new_submolt"}
        mock_request.return_value = mock_response

        result = submolts_core.create("new_submolt", "New Submolt", "Description")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["json"]["name"] == "new_submolt"
        assert call_args.kwargs["json"]["display_name"] == "New Submolt"

    @patch("moltcli.utils.api_client.requests.request")
    def test_feed(self, mock_request, submolts_core):
        """Test get submolt feed."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"posts": []}
        mock_request.return_value = mock_response

        submolts_core.feed("ai", sort="new", limit=10)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["sort"] == "new"
        assert call_args.kwargs["params"]["limit"] == 10

    @patch("moltcli.utils.api_client.requests.request")
    def test_subscribe(self, mock_request, submolts_core):
        """Test subscribe to submolt. Uses /submolts/{name}/subscribe endpoint per skill.md."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        submolts_core.subscribe("ai")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "/ai/subscribe" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_unsubscribe(self, mock_request, submolts_core):
        """Test unsubscribe from submolt. Uses DELETE /submolts/{name}/subscribe per skill.md."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        submolts_core.unsubscribe("ai")

        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"
        assert "/ai/subscribe" in str(call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_subscribed(self, mock_request, submolts_core):
        """Test get user's subscribed submolts."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"subscriptions": []}
        mock_request.return_value = mock_response

        result = submolts_core.get_subscribed()

        assert "subscriptions" in str(mock_request.call_args)

    @patch("moltcli.utils.api_client.requests.request")
    def test_trending(self, mock_request, submolts_core):
        """Test get trending submolts.

        Note: This endpoint may not exist in the actual API.
        Removing or commenting out this test if trending is not available.
        """
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"submolts": []}
        mock_request.return_value = mock_response

        # This test validates the code structure, actual API may not have this endpoint
        submolts_core.trending(limit=5)

        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 5
