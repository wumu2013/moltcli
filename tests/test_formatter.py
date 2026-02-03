"""Tests for formatter module."""
import pytest
import json


class TestOutputFormatter:
    """Test OutputFormatter class."""

    def test_json_mode_output(self):
        """Test JSON output mode."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=True)
        result = formatter.format({"key": "value"})

        assert json.loads(result) == {"key": "value"}

    def test_human_mode_dict(self):
        """Test human-readable mode for dict."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=False)
        result = formatter.format({"name": "test", "count": 5})

        assert "name: test" in result
        assert "count: 5" in result

    def test_human_mode_list(self):
        """Test human-readable mode for list."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=False)
        result = formatter.format(["item1", "item2"])

        assert "1. item1" in result
        assert "2. item2" in result

    def test_human_mode_nested(self):
        """Test human-readable mode for nested data."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=False)
        data = {
            "user": {"name": "test", "age": 25},
            "posts": [{"id": 1}, {"id": 2}],
        }
        result = formatter.format(data)

        assert "user:" in result
        assert "name: test" in result
        assert "posts:" in result

    def test_print_output(self, capsys):
        """Test print method outputs to stdout."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=False)
        formatter.print({"test": "value"})

        captured = capsys.readouterr()
        assert "test: value" in captured.out

    def test_print_json_mode(self, capsys):
        """Test print method in JSON mode."""
        from moltcli.utils.formatter import OutputFormatter

        formatter = OutputFormatter(json_mode=True)
        formatter.print({"key": "value"})

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == {"key": "value"}
