"""MoltCLI utils package."""

from .config import Config, get_config
from .api_client import MoltbookClient
from .formatter import OutputFormatter
from .memory import MemoryStore, MemoryEntry, get_memory, MEMORY_DIR
from .errors import (
    MoltCLIError,
    AuthError,
    NotFoundError,
    RateLimitError,
    handle_error,
    parse_rate_limit_from_response,
)


def normalize_submolt_name(name: str) -> str:
    """Strip 'm/' prefix if present.

    Some API responses use 'm/' prefix for submolt names,
    but API calls should use the name without prefix.
    """
    if name.startswith("m/"):
        return name[2:]
    return name


__all__ = [
    "Config",
    "get_config",
    "MoltbookClient",
    "OutputFormatter",
    "MemoryStore",
    "MemoryEntry",
    "get_memory",
    "MEMORY_DIR",
    "MoltCLIError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "handle_error",
    "parse_rate_limit_from_response",
    "normalize_submolt_name",
]
