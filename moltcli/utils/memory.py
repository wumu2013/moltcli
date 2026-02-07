"""Local memory system for CLI-first agents."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
import hashlib


MEMORY_DIR = "~/.config/moltcli/memory"


@dataclass
class MemoryEntry:
    """A single memory entry."""

    id: str
    category: str
    content: str
    tags: List[str]
    source: str
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert to human-readable markdown format."""
        tags_str = ", ".join(f"`{t}`" for t in self.tags)
        return f"""## {self.category} - {self.created_at[:10]}
{self.content}

**Tags:** {tags_str} | **Source:** {self.source} | **ID:** {self.id[-8:]}"""


class MemoryStore:
    """Local memory storage for CLI-first agents."""

    def __init__(self, memory_path: Optional[str] = None):
        self.memory_path = Path(memory_path or MEMORY_DIR).expanduser()
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self._init_memory_files()

    def _init_memory_files(self):
        """Initialize memory files if they don't exist."""
        files = {
            "identity.md": "# Agent Identity\n\nCore identity, values, and purpose.",
            "learnings.md": "# Learnings\n\nThings the agent has learned from interactions.",
            "context.md": "# Context\n\nCurrent context, preferences, and ongoing topics.",
            "interactions.md": "# Interactions\n\nHistory of posts, comments, and key interactions.",
            "platforms.md": "# Platforms\n\nNotes about different platforms and their quirks.",
        }
        for filename, default_content in files.items():
            filepath = self.memory_path / filename
            if not filepath.exists():
                filepath.write_text(default_content)

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for a memory entry."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{content}{timestamp}".encode()).hexdigest()[:16]

    def add(
        self,
        content: str,
        category: str = "learnings",
        tags: Optional[List[str]] = None,
        source: str = "cli",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""
        entry = MemoryEntry(
            id=self._generate_id(content),
            category=category,
            content=content,
            tags=tags or [],
            source=source,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        self._save_entry(entry)
        return entry

    def _save_entry(self, entry: MemoryEntry):
        """Save entry to appropriate category file."""
        filename = f"{entry.category}.jsonl"
        filepath = self.memory_path / filename
        with open(filepath, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def search(self, query: str, category: Optional[str] = None) -> List[MemoryEntry]:
        """Search memories by content."""
        results = []
        categories = (
            [category] if category else ["learnings", "context", "interactions"]
        )
        for cat in categories:
            filepath = self.memory_path / f"{cat}.jsonl"
            if filepath.exists():
                with open(filepath) as f:
                    for line in f:
                        if query.lower() in line.lower():
                            results.append(MemoryEntry(**json.loads(line)))
        return results

    def view(self, category: Optional[str] = None) -> str:
        """View memories as human-readable markdown."""
        categories = (
            [category]
            if category
            else ["identity", "learnings", "context", "interactions", "platforms"]
        )
        output = []
        for cat in categories:
            jsonl_file = self.memory_path / f"{cat}.jsonl"
            md_file = self.memory_path / f"{cat}.md"

            if jsonl_file.exists():
                output.append(f"\n# {cat.title()}\n")
                with open(jsonl_file) as f:
                    for line in f:
                        entry = MemoryEntry(**json.loads(line))
                        output.append(entry.to_markdown())
                        output.append("\n---\n")
            elif md_file.exists():
                output.append(f"\n# {cat.title()}\n")
                output.append(md_file.read_text())
        return "\n".join(output)

    def export(self, format: str = "json") -> str:
        """Export all memories for portability."""
        if format == "json":
            all_memories = {}
            for jsonl_file in self.memory_path.glob("*.jsonl"):
                memories = []
                with open(jsonl_file) as f:
                    for line in f:
                        memories.append(json.loads(line))
                all_memories[jsonl_file.stem] = memories
            return json.dumps(all_memories, indent=2)
        elif format == "markdown":
            return self.view()
        return self.view()

    def import_from(self, data: str, format: str = "json"):
        """Import memories from exported data."""
        if format == "json":
            all_memories = json.loads(data)
            for category, memories in all_memories.items():
                filename = f"{category}.jsonl"
                filepath = self.memory_path / filename
                with open(filepath, "a") as f:
                    for mem in memories:
                        f.write(json.dumps(mem) + "\n")
        elif format == "markdown":
            pass  # Markdown import would require parsing

    def record_interaction(
        self,
        platform: str,
        action: str,
        target: str,
        result: str = "success",
    ):
        """Record a platform interaction."""
        self.add(
            content=f"{action} on {platform}: {target} -> {result}",
            category="interactions",
            tags=[platform, action, result],
            source=platform,
        )

    def record_learning(
        self,
        content: str,
        topic: str,
        source: str = "cli",
    ):
        """Record something the agent learned."""
        self.add(
            content=content,
            category="learnings",
            tags=["learning", topic],
            source=source,
        )

    def update_context(
        self,
        topic: str,
        details: str,
    ):
        """Update current context/preferences."""
        self.add(
            content=f"{topic}: {details}",
            category="context",
            tags=["context", topic],
            source="cli",
        )


def get_memory() -> MemoryStore:
    """Get the memory store instance."""
    return MemoryStore()


__all__ = ["MemoryStore", "MemoryEntry", "get_memory", "MEMORY_DIR"]
