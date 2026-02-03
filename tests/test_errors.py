"""Tests for errors module."""
import pytest
from unittest.mock import Mock


class TestMoltCLIError:
    """Test error classes."""

    def test_auth_error(self):
        """Test AuthError has correct code and suggestion."""
        from moltcli.utils.errors import AuthError, AUTH_INVALID

        error = AuthError("Invalid API key")

        assert error.code == AUTH_INVALID
        assert "API key" in error.message
        assert error.suggestion is not None

    def test_not_found_error_post(self):
        """Test NotFoundError for post."""
        from moltcli.utils.errors import NotFoundError, POST_NOT_FOUND

        error = NotFoundError("post")

        assert error.code == POST_NOT_FOUND
        assert "not found" in error.message

    def test_not_found_error_submolt(self):
        """Test NotFoundError for submolt."""
        from moltcli.utils.errors import NotFoundError, SUBMOLT_NOT_FOUND

        error = NotFoundError("submolt")

        assert error.code == SUBMOLT_NOT_FOUND

    def test_rate_limit_error_basic(self):
        """Test RateLimitError basic usage."""
        from moltcli.utils.errors import RateLimitError, RATE_LIMIT

        error = RateLimitError()

        assert error.code == RATE_LIMIT
        assert error.suggestion is not None
        assert "wait" in error.message.lower() or "limit" in error.message.lower()

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after."""
        from moltcli.utils.errors import RateLimitError

        error = RateLimitError(retry_after=60)

        assert "60 seconds" in error.message
        assert "Retry after 60 seconds" in error.suggestion
        assert error.retry_after == 60

    def test_rate_limit_error_with_limit_info(self):
        """Test RateLimitError with limit info."""
        from moltcli.utils.errors import RateLimitError

        error = RateLimitError(limit=100, remaining=0)

        assert error.limit == 100
        assert error.remaining == 0

    def test_base_error_message(self):
        """Test MoltCLIError base class."""
        from moltcli.utils.errors import MoltCLIError

        error = MoltCLIError("test message", "TEST_CODE", "test suggestion")

        assert str(error) == "test message"
        assert error.code == "TEST_CODE"
        assert error.suggestion == "test suggestion"

    def test_to_dict_method(self):
        """Test MoltCLIError.to_dict() method."""
        from moltcli.utils.errors import AuthError

        error = AuthError("test message")
        result = error.to_dict()

        assert result["status"] == "error"
        assert result["error_code"] == "AUTH_INVALID"
        assert result["message"] == "test message"
        assert "suggestion" in result


class TestHandleError:
    """Test error handling function."""

    def test_handle_moltcli_error(self):
        """Test handling MoltCLIError."""
        from moltcli.utils.errors import AuthError, handle_error

        error = AuthError("Invalid key")
        result = handle_error(error)

        assert result["status"] == "error"
        assert result["error_code"] == "AUTH_INVALID"
        assert result["message"] == "Invalid key"

    def test_handle_unknown_error(self):
        """Test handling unknown exception."""
        from moltcli.utils.errors import handle_error

        error = ValueError("unknown error")
        result = handle_error(error)

        assert result["status"] == "error"
        assert result["error_code"] == "UNKNOWN"
        assert result["message"] == "unknown error"


class TestParseRateLimitFromResponse:
    """Test parse_rate_limit_from_response function."""

    def test_parse_retry_after_header(self):
        """Test parsing Retry-After header."""
        from moltcli.utils.errors import parse_rate_limit_from_response

        mock_response = Mock()
        mock_response.headers = {"Retry-After": "30"}
        mock_response.json.return_value = {}

        retry_after, limit, remaining = parse_rate_limit_from_response(mock_response)

        assert retry_after == 30
        assert limit is None
        assert remaining is None

    def test_parse_x_ratelimit_headers(self):
        """Test parsing X-RateLimit headers."""
        from moltcli.utils.errors import parse_rate_limit_from_response

        mock_response = Mock()
        mock_response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "50",
        }
        mock_response.json.return_value = {}

        retry_after, limit, remaining = parse_rate_limit_from_response(mock_response)

        assert retry_after is None
        assert limit == 100
        assert remaining == 50

    def test_parse_body_rate_limit(self):
        """Test parsing rate limit from body."""
        from moltcli.utils.errors import parse_rate_limit_from_response

        mock_response = Mock()
        mock_response.headers = {}
        mock_response.json.return_value = {
            "retry_after": 45,
            "rate_limit": {"limit": 200, "remaining": 100},
        }

        retry_after, limit, remaining = parse_rate_limit_from_response(mock_response)

        assert retry_after == 45
        assert limit == 200
        assert remaining == 100

    def test_parse_no_rate_limit(self):
        """Test when no rate limit info available."""
        from moltcli.utils.errors import parse_rate_limit_from_response

        mock_response = Mock()
        mock_response.headers = {}
        mock_response.json.return_value = {"data": "something"}

        retry_after, limit, remaining = parse_rate_limit_from_response(mock_response)

        assert retry_after is None
        assert limit is None
        assert remaining is None

