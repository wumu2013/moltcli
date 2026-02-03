"""Test fixtures."""
import pytest
import sys
from pathlib import Path

# Add moltcli to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def mock_client(mock_api_key):
    """Create mock API client."""
    from moltcli.utils.api_client import MoltbookClient
    return MoltbookClient(mock_api_key)


@pytest.fixture
def sample_post():
    """Sample post data."""
    return {
        "id": "post_123",
        "title": "Test Post",
        "content": "Test content",
        "author": {"name": "test_user"},
        "submolt": {"name": "test_submolt"},
        "upvotes": 10,
        "comment_count": 5,
        "created_at": "2026-02-03T10:30:00+08:00",
    }


@pytest.fixture
def sample_feed():
    """Sample feed response."""
    return {
        "posts": [
            {
                "id": "post_1",
                "title": "Post 1",
                "upvotes": 100,
            },
            {
                "id": "post_2",
                "title": "Post 2",
                "upvotes": 50,
            },
        ],
        "total": 2,
    }
