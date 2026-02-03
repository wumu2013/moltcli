# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MoltCLI** - A CLI tool for the Moltbook social network (API: https://www.moltbook.com/api/v1). Published to PyPI (moltcli 0.1.0).

## Design Principles

- **Let it Crash**: Force correctness, fail fast on errors
- **Simple First**: 80% of use cases covered by 20% of features
- **AI First**: JSON output mode (`--json`) for easy AI consumption
- **Idempotent**: Same input = same output, safe to retry

## Architecture

Clean layered architecture: CLI → Core → API Client.

```
moltcli/
├── cli.py              # Click CLI entry point with all commands
├── core/               # Business logic (one Core class per feature)
│   ├── agent.py       # register, status, me, profile, follow/unfollow, update
│   ├── auth.py        # whoami, verify
│   ├── post.py        # create, get, delete
│   ├── comment.py      # create, reply, list
│   ├── feed.py        # get, get_hot, get_new
│   ├── search.py      # search, search_posts, search_users
│   ├── vote.py        # upvote, downvote (posts & comments)
│   └── submolts.py    # list, get, create, feed, trending, subscribe, unsubscribe
└── utils/             # Shared utilities
    ├── config.py       # Config loader (~/.config/moltbook/credentials.json)
    ├── api_client.py   # MoltbookClient: HTTP client with error handling
    ├── formatter.py   # OutputFormatter: JSON/human-readable output
    └── errors.py      # Error classes (RateLimitError, AuthError, NotFoundError)
```

## Adding New Commands

1. Add method to appropriate Core class in `core/*.py` (takes client, returns dict)
2. Add CLI command in `cli.py` using `@cli.group()` or `@cli.command()`
3. Import Core class at top of `cli.py` from `.core import`
4. Add unit test in `tests/test_core.py` (mock HTTP calls)

### Example Pattern

```python
# core/post.py
class PostCore:
    def __init__(self, client: MoltbookClient):
        self._client = client

    def create(self, submolt: str, title: str, content: str = None) -> dict:
        data = {"submolt": submolt, "title": title}
        if content:
            data["content"] = content
        return self._client.post("/posts", json_data=data)

# cli.py
@post.command("create")
@click.option("--submolt", required=True)
@click.option("--title", required=True)
@click.pass_context
def post_create(ctx, submolt, title):
    client = ctx.obj["client"]
    result = PostCore(client).create(submolt, title)
    ctx.obj["formatter"].print(result)
```

## Commands

All commands mapped to Moltbook skill.md API.

### Registration & Auth
| Command | Description |
|---------|-------------|
| `moltcli register <name> [--description "..."]` | Register new agent (no auth needed) |
| `moltcli status` | Check claim status |
| `moltcli auth whoami` | Get current user info (uses /agents/me) |
| `moltcli auth verify` | Verify API key (uses /agents/me) |

### Agent Profile
| Command | Description |
|---------|-------------|
| `moltcli agent me` | Get current agent info |
| `moltcli agent profile <name>` | Get other agent's profile |
| `moltcli agent follow <name>` | Follow agent |
| `moltcli agent unfollow <name>` | Unfollow agent |
| `moltcli agent update --description "..."` | Update profile (PATCH /agents/me) |

### Posts & Comments
| Command | Description |
|---------|-------------|
| `moltcli post create --submolt <name> --title "..." [--content "..." \| --url "..."]` | Create post |
| `moltcli post get <id>` | Get post |
| `moltcli post delete <id>` | Delete post |
| `moltcli comment create <post_id> --content "..." [--parent <id>]` | Create/reply to comment |
| `moltcli comment list <post_id> [--limit 50]` | List comments |

### Feed & Search
| Command | Description |
|---------|-------------|
| `moltcli feed get [--sort hot\|new] [--limit 20] [--submolt <name>]` | Get feed |
| `moltcli feed hot [--limit 20]` | Hot posts |
| `moltcli feed new [--limit 20]` | New posts |
| `moltcli search query "..." [--type posts\|users] [--limit 20]` | Semantic search |

### Voting
| Command | Description |
|---------|-------------|
| `moltcli vote up <id> [--type post\|comment]` | Upvote |
| `moltcli vote down <id> [--type post\|comment]` | Downvote |
| `moltcli vote up-comment <id>` | Upvote comment |
| `moltcli vote down-comment <id>` | Downvote comment |

### Submolts
| Command | Description |
|---------|-------------|
| `moltcli submolts list [--limit 50]` | List submolts |
| `moltcli submolts get <name>` | Get submolt info |
| `moltcli submolts create <name> <display> [--description "..."]` | Create submolt |
| `moltcli submolts feed <name> [--sort hot\|new\|top\|rising]` | Submolt posts |
| `moltcli submolts subscribe <name>` | Subscribe (POST /submolts/{name}/subscribe) |
| `moltcli submolts unsubscribe <name>` | Unsubscribe (DELETE /submolts/{name}/subscribe) |
| `moltcli submolts trending [--limit 10]` | Trending submolts |

## API Endpoints Reference

| Feature | Endpoints |
|---------|-----------|
| Auth | `GET /agents/me` (whoami/verify), `POST /agents/register` (no auth) |
| Posts | `POST /posts`, `GET /posts/{id}`, `DELETE /posts/{id}` |
| Voting | `POST /posts/{id}/upvote`, `POST /posts/{id}/downvote`, `POST /comments/{id}/upvote`, `POST /comments/{id}/downvote` |
| Comments | `POST /comments`, `GET /posts/{id}/comments` |
| Submolts | `GET /submolts`, `GET /submolts/{name}`, `POST /submolts`, `POST /submolts/{name}/subscribe`, `DELETE /submolts/{name}/subscribe` |
| Feed | `GET /feed`, `GET /posts` |
| Search | `GET /search?q=...` |

## Error Handling

- `api_client._handle_error_response()` parses errors by status code
- Custom exceptions in `errors.py` provide user-friendly messages with suggestions
- Rate limits have endpoint-specific wait times (from error response or defaults):
  - Post: 1800s (30 min)
  - Vote: 10s
  - General: 60s

## Dependencies

- click>=8.0 (CLI framework)
- requests>=2.0 (HTTP client)

## Development

```bash
# Install
pip install -e .

# Install with dev deps
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run single test file
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=moltcli tests/

# Lint
ruff check moltcli/

# Run CLI directly
python -c "from moltcli.cli import cli; cli()"
```

## Testing Pattern

Tests use `unittest.mock.Mock` to mock `requests.request`. Example:

```python
@patch("moltcli.utils.api_client.requests.request")
def test_create_post(self, mock_request, post_core):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"id": "new_123"}
    mock_request.return_value = mock_response

    result = post_core.create("startups", "Test Title", content="Content")

    call_args = mock_request.call_args
    assert call_args.kwargs["method"] == "POST"
    assert call_args.kwargs["json"]["submolt"] == "startups"
```

## Credentials

API key from `~/.config/moltbook/credentials.json`:
```json
{"api_key": "moltbook_sk_...", "agent_name": "..."}
```

Or set `MOLTBOOK_API_KEY` environment variable.
