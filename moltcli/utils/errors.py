"""Error codes and error handler for MoltCLI."""
from typing import Optional


# Error codes
AUTH_INVALID = "AUTH_INVALID"
AUTH_MISSING = "AUTH_MISSING"
POST_NOT_FOUND = "POST_NOT_FOUND"
SUBMOLT_NOT_FOUND = "SUBMOLT_NOT_FOUND"
RATE_LIMIT = "RATE_LIMIT"
NETWORK_ERROR = "NETWORK_ERROR"


class MoltCLIError(Exception):
    """Base error for MoltCLI."""

    def __init__(self, message: str, code: str, suggestion: Optional[str] = None):
        self.message = message
        self.code = code
        self.suggestion = suggestion
        super().__init__(message)

    def to_dict(self) -> dict:
        """Convert to error response dict."""
        return {
            "status": "error",
            "error_code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class AuthError(MoltCLIError):
    """Authentication error."""

    def __init__(self, message: str):
        super().__init__(message, AUTH_INVALID, "Check your API key in credentials.json")


class NotFoundError(MoltCLIError):
    """Resource not found error."""

    def __init__(self, resource: str):
        super().__init__(
            f"{resource} not found",
            POST_NOT_FOUND if resource == "post" else SUBMOLT_NOT_FOUND,
            f"Verify the {resource} exists and you have permission",
        )


class RateLimitError(MoltCLIError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: Optional[str] = None,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        endpoint_type: str = "general",
    ):
        """Initialize rate limit error.

        Args:
            message: Raw error message from server
            retry_after: Seconds until retry is allowed
            limit: Rate limit maximum requests
            remaining: Remaining requests in window
            endpoint_type: Type of endpoint (post, vote, general)
        """
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining

        # Use server message if available, else generic
        if message:
            final_message = message
        else:
            default_wait = 60
            if endpoint_type == "post":
                default_wait = 1800
            elif endpoint_type == "vote":
                default_wait = 10
            final_message = f"Rate limit exceeded. Retry after {retry_after or default_wait} seconds."

        # Suggestion with retry_after
        if retry_after:
            suggestion = f"Retry after {retry_after} seconds."
        else:
            suggestion = "Wait before retrying."

        super().__init__(final_message, RATE_LIMIT, suggestion)


def handle_error(error: Exception) -> dict:
    """Convert exception to error response."""
    if isinstance(error, MoltCLIError):
        return error.to_dict()
    return {
        "status": "error",
        "error_code": "UNKNOWN",
        "message": str(error),
    }


def parse_rate_limit_from_response(response) -> tuple:
    """Parse rate limit info from API response.

    Args:
        response: requests.Response object

    Returns:
        Tuple of (retry_after, limit, remaining)
    """
    # Try common rate limit headers
    retry_after = None
    limit = None
    remaining = None

    # Retry-After header (seconds)
    if "Retry-After" in response.headers:
        try:
            retry_after = int(response.headers["Retry-After"])
        except ValueError:
            pass

    # X-RateLimit headers (common pattern)
    if "X-RateLimit-Limit" in response.headers:
        try:
            limit = int(response.headers["X-RateLimit-Limit"])
        except ValueError:
            pass

    if "X-RateLimit-Remaining" in response.headers:
        try:
            remaining = int(response.headers["X-RateLimit-Remaining"])
        except ValueError:
            pass

    # Also check response body for rate limit info
    try:
        body = response.json()
        if isinstance(body, dict):
            if "retry_after" in body:
                retry_after = body["retry_after"]
            if "rate_limit" in body:
                rl = body["rate_limit"]
                if isinstance(rl, dict):
                    limit = rl.get("limit", limit)
                    remaining = rl.get("remaining", remaining)
    except Exception:
        pass

    return retry_after, limit, remaining
