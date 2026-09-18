"""`pron mcp`: the MCP surface over stdio, several worlds, one per --world (spec 14 §1)."""

from __future__ import annotations

import click


@click.command("mcp", short_help="Serve worlds to agents over MCP (stdio)")
@click.option(
    "--world",
    "worlds",
    multiple=True,
    required=True,
    help="World root, or NAME=PATH; repeatable, each world is a tool argument",
)
@click.option(
    "--pythonpath",
    default=None,
    help="Project path where the worlds' models import from",
)
@click.option("--projection", default="all", help="The sessions' projection (spec 01)")
@click.option("--speaker", default="mcp", help="Default speaker of the MoveDocs")
@click.option("--audit", default=None, help="MODULE:FUNC a world's audit also runs")
def command(
    worlds: tuple[str, ...],
    pythonpath: str | None,
    projection: str,
    speaker: str,
    audit: str | None,
) -> int:
    """Serve one or more worlds to agents as an MCP server over stdio (spec 14).

    Each --world is mounted as its own World, never linked into another and never written
    to for mounting; the world is an argument of every tool. Reads are kb:// addresses
    (kb_get and the resources) and the read tools; no tool takes a sentence. Writes are
    forms compiled from JSON: content (level 1), relation types (level 2), and models
    generated under --pythonpath (level 3, only with confirm); the projection's
    `mutability` is the highest level its sessions may use. kb_audit runs pron check,
    check_edges and --audit. Needs the optional dependency: pip install pron[mcp].

    Usage:
      pron mcp --world restaurant=../restaurant --world ./other --pythonpath .
      pron mcp --world . --projection all --speaker agent-7
    """
    from pron.mcp.app import McpApp
    from pron.mcp.server import run

    run(McpApp.open(list(worlds), pythonpath, projection, speaker, audit))
    return 0
