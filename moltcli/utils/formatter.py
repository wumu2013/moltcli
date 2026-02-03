"""Output formatter for MoltCLI."""
import json
from typing import Any


class OutputFormatter:
    """Handle JSON vs human-readable output."""

    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode

    def format(self, data: Any) -> str:
        """Format data for output."""
        if self.json_mode:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return self._humanize(data)

    def _humanize(self, data: Any, indent: int = 0) -> str:
        """Convert to human-readable format."""
        if isinstance(data, dict):
            lines = []
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{k}:")
                    lines.append(self._humanize(v, indent + 2))
                else:
                    lines.append(f"{k}: {v}")
            return "\n".join(lines)
        elif isinstance(data, list):
            if not data:
                return "(empty)"
            lines = []
            for i, item in enumerate(data, 1):
                lines.append(f"  {i}. {self._humanize(item, indent + 1)}")
            return "\n".join(lines)
        return str(data)

    def print(self, data: Any) -> None:
        """Print formatted output."""
        print(self.format(data))
