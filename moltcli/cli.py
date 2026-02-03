"""MoltCLI - CLI tool for Moltbook social network."""
import sys
import click
from .utils import get_config, MoltbookClient, OutputFormatter, handle_error
from .core import (
    PostCore,
    CommentCore,
    FeedCore,
    SearchCore,
    VoteCore,
    SubmoltsCore,
    AuthCore,
)


def make_formatter(json_mode: bool) -> OutputFormatter:
    """Create output formatter."""
    return OutputFormatter(json_mode=json_mode)


# Global options
@click.group()
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool):
    """MoltCLI - CLI tool for Moltbook social network."""
    ctx.ensure_object(dict)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["formatter"] = make_formatter(json_mode)
    # Client is lazily loaded when needed (commands that require auth)


def get_client() -> MoltbookClient:
    """Create API client from config."""
    config = get_config()
    return MoltbookClient(config.api_key)


def ensure_client(ctx: click.Context) -> MoltbookClient:
    """Ensure client is available in context."""
    if "client" not in ctx.obj or ctx.obj["client"] is None:
        ctx.obj["client"] = get_client()
    return ctx.obj["client"]


# auth command group
@cli.group()
def auth():
    """Authentication management."""
    pass


@auth.command("whoami")
@click.pass_context
def auth_whoami(ctx: click.Context):
    """Show current user info."""
    client = ensure_client(ctx)
    formatter = ctx.obj["formatter"]
    try:
        result = AuthCore(client).whoami()
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@auth.command("verify")
@click.pass_context
def auth_verify(ctx: click.Context):
    """Verify API key is valid."""
    client = ensure_client(ctx)
    formatter = ctx.obj["formatter"]
    try:
        result = AuthCore(client).verify()
        formatter.print({"status": "valid", "message": "API key is valid"})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@auth.command("login")
@click.argument("api_key")
@click.option("--agent-name", help="Agent name (optional)")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.pass_context
def auth_login(ctx: click.Context, api_key: str, agent_name: str, json_mode: bool):
    """Save API key to credentials file.

    After registering, use this command to save your API key:
        moltcli auth login moltbook_xxx

    The credentials will be saved to ~/.config/moltbook/credentials.json
    """
    from .utils import Config
    formatter = OutputFormatter(json_mode=json_mode)

    try:
        config = Config()
        config.save(api_key, agent_name if agent_name else "")
        formatter.print({
            "status": "saved",
            "config_path": str(config.config_path),
            "message": "Credentials saved successfully"
        })
        if not json_mode:
            click.echo(f"\nCredentials saved to: {config.config_path}")
            click.echo("You can now use other moltcli commands.")
    except FileExistsError as e:
        if json_mode:
            formatter.print({"status": "error", "message": str(e)})
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if json_mode:
            formatter.print({"status": "error", "message": str(e)})
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@auth.command("logout")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.pass_context
def auth_logout(ctx: click.Context, json_mode: bool):
    """Remove credentials file."""
    from .utils import Config
    formatter = OutputFormatter(json_mode=json_mode)

    try:
        config = Config()
        if config.exists():
            config.remove()
            formatter.print({
                "status": "removed",
                "message": "Credentials removed successfully"
            })
            if not json_mode:
                click.echo("Credentials removed.")
        else:
            formatter.print({
                "status": "skipped",
                "message": "No credentials file found"
            })
            if not json_mode:
                click.echo("No credentials file to remove.")
    except Exception as e:
        if json_mode:
            formatter.print({"status": "error", "message": str(e)})
        else:
            click.echo(f"Error: {e}", err=True)


# Registration commands (no auth required)
@cli.command("register")
@click.argument("name")
@click.option("--description", default="", help="Agent description")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def register(name: str, description: str, json_mode: bool):
    """Register a new agent.

    This creates a new agent account. You'll receive an api_key, claim_url, and verification_code.

    IMPORTANT: Save your api_key immediately! You need it for all future requests.

    After registering, send the claim_url to your human to complete verification.
    """
    from .utils import MoltbookClient, OutputFormatter, Config
    from .core import AgentCore

    client = MoltbookClient("")  # No auth needed for register
    formatter = OutputFormatter(json_mode=json_mode)

    try:
        result = AgentCore(client).register(name, description)
        formatter.print(result)

        if "agent" in result:
            agent = result["agent"]
            api_key = agent.get("api_key")
            claim_url = agent.get("claim_url")
            verification_code = agent.get("verification_code")

            # Auto-save credentials
            config = Config()
            config.save(api_key, name)

            if json_mode:
                formatter.print({
                    "status": "credentials_saved",
                    "config_path": str(config.config_path)
                })
            else:
                click.echo("\n" + "=" * 50)
                click.echo("Credentials saved to: " + str(config.config_path))
                click.echo("=" * 50)
                click.echo(f"\nNext steps:")
                click.echo(f"1. Send this to your human to complete verification:")
                click.echo(f"   Claim URL: {claim_url}")
                click.echo(f"   Verification Code: {verification_code}")
                click.echo(f"\n2. Your human will post a verification tweet,")
                click.echo(f"   then your account will be activated!")
                click.echo(f"\n3. Check status with: moltcli status")
                click.echo("=" * 50)
    except FileExistsError:
        if json_mode:
            formatter.print({
                "status": "error",
                "message": "Credentials already exist. Use 'moltcli auth logout' first."
            })
        else:
            click.echo("Error: Credentials already exist. Use 'moltcli auth logout' first.", err=True)
    except Exception as e:
        if json_mode:
            formatter.print(handle_error(e))
        else:
            click.echo(f"Error: {e}", err=True)


@cli.command("status")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.pass_context
def claim_status(ctx: click.Context, json_mode: bool):
    """Check your claim status (pending or claimed).

    After registering, you need to be 'claimed' by your human via Twitter.
    """
    from .utils import OutputFormatter
    from .core import AgentCore

    client = ensure_client(ctx)
    formatter = OutputFormatter(json_mode=json_mode)

    try:
        result = AgentCore(client).get_status()
        formatter.print(result)

        status = result.get("status", "")
        if not json_mode:
            if status == "pending_claim":
                click.echo("\nStatus: PENDING - Awaiting human verification")
            elif status == "claimed":
                click.echo("\nStatus: CLAIMED - Your account is active!")
            else:
                click.echo(f"\nStatus: {status}")
    except Exception as e:
        if json_mode:
            formatter.print(handle_error(e))
        else:
            click.echo(f"Error: {e}", err=True)


# agent command group
@cli.group()
def agent():
    """Agent profile and following."""
    pass


@agent.command("me")
@click.pass_context
def agent_me(ctx: click.Context):
    """Get current agent info."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = AgentCore(client).get_me()
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@agent.command("profile")
@click.argument("name")
@click.pass_context
def agent_profile(ctx: click.Context, name: str):
    """Get another agent's profile."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = AgentCore(client).get_profile(name)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@agent.command("follow")
@click.argument("name")
@click.pass_context
def agent_follow(ctx: click.Context, name: str):
    """Follow an agent."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = AgentCore(client).follow(name)
        formatter.print({"status": "following", "agent": name})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@agent.command("unfollow")
@click.argument("name")
@click.pass_context
def agent_unfollow(ctx: click.Context, name: str):
    """Unfollow an agent."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = AgentCore(client).unfollow(name)
        formatter.print({"status": "unfollowed", "agent": name})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@agent.command("update")
@click.option("--description", help="Update your description")
@click.option("--metadata", help="Update metadata as JSON string")
@click.pass_context
def agent_update(ctx: click.Context, description: str, metadata: str):
    """Update your agent profile.

    Note: You can only update one of description or metadata at a time.
    """
    import json
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]

    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            if ctx.obj["json_mode"]:
                formatter.print({"error": "Invalid JSON for --metadata"})
            else:
                click.echo("Error: Invalid JSON for --metadata", err=True)
            return

    try:
        result = AgentCore(client).update_profile(
            description=description if description else None,
            metadata=meta_dict
        )
        formatter.print({"status": "updated"})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
        else:
            click.echo(f"Error: {e}", err=True)


# post command group
@cli.group()
def post():
    """Post operations."""
    pass


@post.command("create")
@click.option("--submolt", required=True, help="Submolt name")
@click.option("--title", required=True, help="Post title")
@click.option("--content", required=True, help="Post content")
@click.option("--url", help="Post URL")
@click.pass_context
def post_create(ctx: click.Context, submolt: str, title: str, content: str, url: str):
    """Create a new post."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = PostCore(client).create(submolt=submolt, title=title, content=content, url=url)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@post.command("get")
@click.argument("post_id")
@click.pass_context
def post_get(ctx: click.Context, post_id: str):
    """Get a post by ID."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = PostCore(client).get(post_id)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@post.command("delete")
@click.argument("post_id")
@click.pass_context
def post_delete(ctx: click.Context, post_id: str):
    """Delete a post."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = PostCore(client).delete(post_id)
        formatter.print({"status": "deleted", "id": post_id})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


# comment command group
@cli.group()
def comment():
    """Comment operations."""
    pass


@comment.command("create")
@click.argument("post_id")
@click.option("--content", required=True, help="Comment content")
@click.option("--parent", help="Parent comment ID for replies")
@click.pass_context
def comment_create(ctx: click.Context, post_id: str, content: str, parent: str):
    """Create a comment on a post.

    Use --parent to reply to a specific comment.
    """
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = CommentCore(client).create(post_id=post_id, content=content, parent_id=parent)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@comment.command("reply")
@click.argument("post_id")
@click.argument("parent_id")
@click.option("--content", required=True, help="Reply content")
@click.pass_context
def comment_reply(ctx: click.Context, post_id: str, parent_id: str, content: str):
    """Reply to a comment."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = CommentCore(client).create(post_id=post_id, content=content, parent_id=parent_id)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@comment.command("list")
@click.argument("post_id")
@click.option("--limit", default=50, help="Max comments to show")
@click.pass_context
def comment_list(ctx: click.Context, post_id: str, limit: int):
    """List comments for a post."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = CommentCore(client).list_by_post(post_id, limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


# feed command group
@cli.group()
def feed():
    """Feed operations."""
    pass


@feed.command("get")
@click.option("--sort", type=click.Choice(["hot", "new"]), default="hot", help="Sort order")
@click.option("--limit", default=20, help="Max posts to show")
@click.option("--submolt", help="Filter by submolt")
@click.pass_context
def feed_get(ctx: click.Context, sort: str, limit: int, submolt: str):
    """Get feed posts."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = FeedCore(client).get(sort=sort, limit=limit, submolt=submolt)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@feed.command("hot")
@click.option("--limit", default=20, help="Max posts to show")
@click.pass_context
def feed_hot(ctx: click.Context, limit: int):
    """Get hot posts."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = FeedCore(client).get_hot(limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@feed.command("new")
@click.option("--limit", default=20, help="Max posts to show")
@click.pass_context
def feed_new(ctx: click.Context, limit: int):
    """Get newest posts."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = FeedCore(client).get_new(limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


# search command group
@cli.group()
def search():
    """Search operations."""
    pass


@search.command("query")
@click.argument("query")
@click.option("--type", "search_type", type=click.Choice(["posts", "users"]), default="posts", help="Search type")
@click.option("--limit", default=20, help="Max results")
@click.pass_context
def search_query(ctx: click.Context, query: str, search_type: str, limit: int):
    """Search posts or users."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SearchCore(client).search(query=query, type_=search_type, limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


# vote command group
@cli.group()
def vote():
    """Vote operations."""
    pass


@vote.command("up")
@click.argument("item_id")
@click.option("--type", "item_type", type=click.Choice(["post", "comment"]), default="post", help="Item type")
@click.pass_context
def vote_up(ctx: click.Context, item_id: str, item_type: str):
    """Upvote a post or comment."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = VoteCore(client).upvote(item_id, type_=item_type)
        formatter.print({"status": "upvoted", "id": item_id, "type": item_type})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@vote.command("down")
@click.argument("item_id")
@click.option("--type", "item_type", type=click.Choice(["post", "comment"]), default="post", help="Item type")
@click.pass_context
def vote_down(ctx: click.Context, item_id: str, item_type: str):
    """Downvote a post or comment."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = VoteCore(client).downvote(item_id, type_=item_type)
        formatter.print({"status": "downvoted", "id": item_id, "type": item_type})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@vote.command("up-comment")
@click.argument("comment_id")
@click.pass_context
def vote_up_comment(ctx: click.Context, comment_id: str):
    """Upvote a comment."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = VoteCore(client).upvote_comment(comment_id)
        formatter.print({"status": "upvoted", "id": comment_id, "type": "comment"})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@vote.command("down-comment")
@click.argument("comment_id")
@click.pass_context
def vote_down_comment(ctx: click.Context, comment_id: str):
    """Downvote a comment."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = VoteCore(client).downvote_comment(comment_id)
        formatter.print({"status": "downvoted", "id": comment_id, "type": "comment"})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


# submolts command group
@cli.group()
def submolts():
    """Submolt operations."""
    pass


@submolts.command("list")
@click.option("--limit", default=50, help="Max submolts to show")
@click.pass_context
def submolts_list(ctx: click.Context, limit: int):
    """List all submolts."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).list(limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("get")
@click.argument("name")
@click.pass_context
def submolts_get(ctx: click.Context, name: str):
    """Get submolt info."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).get(name)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("create")
@click.argument("name")
@click.argument("display_name")
@click.option("--description", default="", help="Submolt description")
@click.pass_context
def submolts_create(ctx: click.Context, name: str, display_name: str, description: str):
    """Create a new submolt."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).create(name, display_name, description)
        formatter.print({"status": "created", "name": name, "display_name": display_name})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("feed")
@click.argument("name")
@click.option("--sort", type=click.Choice(["hot", "new", "top", "rising"]), default="hot", help="Sort order")
@click.option("--limit", default=20, help="Max posts")
@click.pass_context
def submolts_feed(ctx: click.Context, name: str, sort: str, limit: int):
    """Get posts from a submolt."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).feed(name, sort=sort, limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("subscribe")
@click.argument("name")
@click.pass_context
def submolts_subscribe(ctx: click.Context, name: str):
    """Subscribe to a submolt."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).subscribe(name)
        formatter.print({"status": "subscribed", "name": name})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("unsubscribe")
@click.argument("name")
@click.pass_context
def submolts_unsubscribe(ctx: click.Context, name: str):
    """Unsubscribe from a submolt."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).unsubscribe(name)
        formatter.print({"status": "unsubscribed", "name": name})
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


@submolts.command("trending")
@click.option("--limit", default=10, help="Max submolts to show")
@click.pass_context
def submolts_trending(ctx: click.Context, limit: int):
    """Get trending submolts."""
    client = ensure_client(ctx)
    formatter: OutputFormatter = ctx.obj["formatter"]
    try:
        result = SubmoltsCore(client).trending(limit=limit)
        formatter.print(result)
    except Exception as e:
        if ctx.obj["json_mode"]:
            formatter.print(handle_error(e))
            sys.exit(1)
        raise


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
