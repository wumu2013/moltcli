"""Tests for config module."""
import pytest
import tempfile
import json
import os
from pathlib import Path


class TestConfig:
    """Test Config class."""

    def test_load_config_success(self, tmp_path):
        """Test loading config from file."""
        config_file = tmp_path / "credentials.json"
        config_file.write_text(json.dumps({"api_key": "test_key", "agent_name": "test_agent"}))

        from moltcli.utils.config import Config
        config = Config(str(config_file))

        assert config.api_key == "test_key"
        assert config.agent_name == "test_agent"

    def test_load_config_missing_file(self, tmp_path):
        """Test config raises error when file missing."""
        from moltcli.utils.config import Config

        config = Config(str(tmp_path / "missing.json"))
        with pytest.raises(FileNotFoundError):
            _ = config.config

    def test_load_config_missing_api_key(self, tmp_path):
        """Test config raises error when api_key missing."""
        config_file = tmp_path / "credentials.json"
        config_file.write_text(json.dumps({"agent_name": "test"}))

        from moltcli.utils.config import Config
        config = Config(str(config_file))

        with pytest.raises(ValueError, match="api_key not found"):
            _ = config.api_key

    def test_config_get_with_default(self, tmp_path):
        """Test config.get with default value."""
        config_file = tmp_path / "credentials.json"
        config_file.write_text(json.dumps({"api_key": "test"}))

        from moltcli.utils.config import Config
        config = Config(str(config_file))

        assert config.get("missing_key", "default") == "default"
        assert config.get("api_key") == "test"

    def test_config_env_override(self, tmp_path, monkeypatch):
        """Test environment variable overrides config path."""
        config_file = tmp_path / "custom.json"
        config_file.write_text(json.dumps({"api_key": "env_key"}))

        monkeypatch.setenv("MOLTCLI_CONFIG_PATH", str(config_file))

        from moltcli.utils.config import Config
        # Reset global config
        import moltcli.utils.config as config_module
        config_module._config = None

        config = Config()
        assert config.api_key == "env_key"

    def test_save_credentials(self, tmp_path):
        """Test saving credentials to file."""
        from moltcli.utils.config import Config

        config = Config(str(tmp_path / "credentials.json"))
        config.save("test_api_key", "TestAgent")

        assert config.config_path.exists()
        with open(config.config_path) as f:
            saved = json.load(f)
        assert saved["api_key"] == "test_api_key"
        assert saved["agent_name"] == "TestAgent"

    def test_save_credentials_overwrite_fails(self, tmp_path):
        """Test that saving to existing file raises error."""
        from moltcli.utils.config import Config

        config_file = tmp_path / "credentials.json"
        config_file.write_text('{"api_key": "existing"}')

        config = Config(str(config_file))

        with pytest.raises(FileExistsError):
            config.save("new_key", "NewAgent")

    def test_save_credentials_no_agent_name(self, tmp_path):
        """Test saving credentials without agent name."""
        from moltcli.utils.config import Config

        config = Config(str(tmp_path / "credentials.json"))
        config.save("test_api_key")

        with open(config.config_path) as f:
            saved = json.load(f)
        assert saved["api_key"] == "test_api_key"
        assert "agent_name" not in saved

    def test_remove_credentials(self, tmp_path):
        """Test removing credentials file."""
        from moltcli.utils.config import Config

        config_file = tmp_path / "credentials.json"
        config_file.write_text(json.dumps({"api_key": "test"}))
        config = Config(str(config_file))

        assert config.exists()
        result = config.remove()
        assert result is True
        assert not config.exists()

    def test_remove_nonexistent(self, tmp_path):
        """Test removing non-existent credentials."""
        from moltcli.utils.config import Config

        config = Config(str(tmp_path / "nonexistent.json"))
        assert not config.exists()
        result = config.remove()
        assert result is False

    def test_exists(self, tmp_path):
        """Test exists() method."""
        from moltcli.utils.config import Config

        config_file = tmp_path / "credentials.json"
        config_file.write_text('{"api_key": "test"}')
        config = Config(str(config_file))

        assert config.exists() is True

        config2 = Config(str(tmp_path / "missing.json"))
        assert config2.exists() is False
