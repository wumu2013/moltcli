"""Config loader for MoltCLI."""
import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Config loader for credentials and settings."""

    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "moltbook"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "credentials.json"

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.environ.get(
                "MOLTCLI_CONFIG_PATH",
                str(self.DEFAULT_CONFIG_FILE)
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

    def save(self, api_key: str, agent_name: str = "") -> None:
        """Save credentials to config file.

        Does NOT overwrite existing files.

        Args:
            api_key: Moltbook API key
            agent_name: Agent name (optional)

        Raises:
            FileExistsError: If config file already exists
        """
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        if self.config_path.exists():
            raise FileExistsError(
                f"Credentials file already exists: {self.config_path}\n"
                f"Use 'moltcli auth logout' first to remove existing credentials."
            )

        config = {"api_key": api_key}
        if agent_name:
            config["agent_name"] = agent_name

        with open(self.config_path, "x") as f:
            json.dump(config, f, indent=2)

        # Clear cached config
        self._config = None

    def remove(self) -> bool:
        """Remove config file.

        Returns:
            True if file was removed, False if it didn't exist.
        """
        if self.config_path.exists():
            self.config_path.unlink()
            self._config = None
            return True
        return False

    def exists(self) -> bool:
        """Check if config file exists."""
        return self.config_path.exists()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
