"""Config loader for MoltCLI."""
import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Config loader for credentials and settings."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.environ.get(
                "MOLTCLI_CONFIG_PATH",
                str(Path(__file__).parent.parent.parent / "credentials.json")
            )
        self.config_path = Path(config_path)
        self._config: Optional[dict] = None

    @property
    def config(self) -> dict:
        """Load and cache config."""
        if self._config is None:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config not found: {self.config_path}")
            with open(self.config_path) as f:
                self._config = json.load(f)
        return self._config

    @property
    def api_key(self) -> str:
        """Get API key from config."""
        key = self.config.get("api_key")
        if not key:
            raise ValueError("api_key not found in config")
        return key

    @property
    def agent_name(self) -> str:
        """Get agent name from config."""
        return self.config.get("agent_name", "unknown")

    def get(self, key: str, default=None):
        """Get config value by key."""
        return self.config.get(key, default)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
