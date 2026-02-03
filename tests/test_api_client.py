"""Tests for API client module."""
import pytest
from unittest.mock import Mock, patch


class TestMoltbookClient:
    """Test MoltbookClient class."""

    def test_init_sets_headers(self, mock_api_key):
        """Test client initializes with correct headers."""
        from moltcli.utils.api_client import MoltbookClient

        client = MoltbookClient(mock_api_key)

        assert client.api_key == mock_api_key
        assert client.headers["Authorization"] == f"Bearer {mock_api_key}"
        assert client.headers["Content-Type"] == "application/json"

    @patch("moltcli.utils.api_client.requests.request")
    def test_get_request(self, mock_request, mock_api_key):
        """Test GET request."""
        from moltcli.utils.api_client import MoltbookClient

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)
        result = client.get("/test", params={"key": "value"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "GET"
        assert call_args.kwargs["params"] == {"key": "value"}

    @patch("moltcli.utils.api_client.requests.request")
    def test_post_request(self, mock_request, mock_api_key):
        """Test POST request."""
        from moltcli.utils.api_client import MoltbookClient

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "created", "id": "123"}
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)
        result = client.post("/posts", json_data={"title": "Test"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["json"] == {"title": "Test"}

    @patch("moltcli.utils.api_client.requests.request")
    def test_delete_request(self, mock_request, mock_api_key):
        """Test DELETE request."""
        from moltcli.utils.api_client import MoltbookClient

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "deleted"}
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)
        result = client.delete("/posts/123")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"

    @patch("moltcli.utils.api_client.requests.request")
    def test_patch_request(self, mock_request, mock_api_key):
        """Test PATCH request."""
        from moltcli.utils.api_client import MoltbookClient

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "updated"}
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)
        result = client.patch("/agents/me", json_data={"description": "New desc"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["json"] == {"description": "New desc"}

    @patch("moltcli.utils.api_client.requests.request")
    def test_error_response_raises(self, mock_request, mock_api_key):
        """Test non-OK response raises exception."""
        from moltcli.utils.api_client import MoltbookClient
        from moltcli.utils.errors import AuthError

        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)

        with pytest.raises(AuthError):
            client.get("/auth/whoami")

    @patch("moltcli.utils.api_client.requests.request")
    def test_rate_limit_error(self, mock_request, mock_api_key):
        """Test 429 rate limit error handling."""
        from moltcli.utils.api_client import MoltbookClient
        from moltcli.utils.errors import RateLimitError

        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60", "X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "0"}
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)

        with pytest.raises(RateLimitError) as exc_info:
            client.get("/feed")

        assert exc_info.value.retry_after == 60
        assert exc_info.value.limit == 100
        assert exc_info.value.remaining == 0

    @patch("moltcli.utils.api_client.requests.request")
    def test_not_found_error(self, mock_request, mock_api_key):
        """Test 404 not found error handling."""
        from moltcli.utils.api_client import MoltbookClient
        from moltcli.utils.errors import NotFoundError

        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.request.url = "https://www.moltbook.com/api/v1/posts/123"
        mock_request.return_value = mock_response

        client = MoltbookClient(mock_api_key)

        with pytest.raises(NotFoundError):
            client.get("/posts/123")
