"""pron serve (spec 11 §8): one process keeps the world open behind a Unix socket; the CLI,
the REPL and any client say through it, and sessions live in the server. The session counts
below follow the order of the tests in this file."""

from __future__ import annotations

import io

from pron.cli.main import main
from pron.cli.repl import run as repl
from pron.remote import RemoteSession, request
from pron.serve import Server

NOW = "2026-09-09"


def test_a_client_says_through_the_server_and_the_session_lives_there(server: Server):
    s = RemoteSession(server.path, projection="all", speaker="jp", now=NOW)
    r = s.turn("the large tables")
    assert (
        r.outcome == "unico" and "table 12" in r.text and r.move_id.startswith("move-")
    )
    r = s.turn("the large table")  # ambiguous: the server keeps the pending question
    assert r.outcome == "ambiguo"
    r = s.turn("1")
    assert r.outcome == "unico", r.text
    assert request(server.path, {"op": "ping"})["sessions"] == 1
    assert s.payload("Table", "table-12")["capacity"] >= 6


def _say(root: str, sentence: str, *extra: str) -> int:
    return main(["say", sentence, "--world", root, *extra])


def test_the_cli_uses_the_server_when_it_listens(server: Server, capsys):
    root = str(server.world.root)
    assert _say(root, "the large tables on the terrace", "--speaker", "cli") == 0
    assert "table 12" in capsys.readouterr().out
    assert (
        request(server.path, {"op": "ping"})["sessions"] == 2
    )  # a new speaker, a new session, in the server
    pythonpath = server.world.store.pythonpath
    local = ["--pythonpath", pythonpath, "--speaker", "cli", "--local"]
    assert _say(root, "the large tables", *local) == 0
    assert (
        request(server.path, {"op": "ping"})["sessions"] == 2
    )  # --local opened the world here


def test_the_repl_runs_over_the_server(server: Server):
    out = io.StringIO()
    s = RemoteSession(server.path, projection="all", speaker="repl", now=NOW)
    assert (
        repl(
            s,
            "restaurant",
            "all",
            stdin=io.StringIO("the large tables\n:state\n:lexicon Table\n:quit\n"),
            stdout=out,
        )
        == 0
    )
    text = out.getvalue()
    assert (
        "via server" in text
        and "table 12" in text
        and "state: libre" in text
        and "capacity" in text
    )


def test_the_session_key_is_the_five_parameters_and_close_starts_over(server: Server):
    a = RemoteSession(server.path, projection="all", speaker="pair", now=NOW)
    b = RemoteSession(
        server.path, projection="all", speaker="pair", now=NOW
    )  # same five: same dialogue
    c = RemoteSession(
        server.path, projection="all", speaker="pair", now="2026-09-10"
    )  # another now: another session
    before = request(server.path, {"op": "ping"})["sessions"]
    assert a.turn("the large table").outcome == "ambiguo"
    assert b.turn("1").outcome == "unico"  # b answered a's question
    assert (
        c.turn("1").outcome != "unico" or "table" not in c.turn("the clients").text
    )  # c has no pending question
    assert request(server.path, {"op": "ping"})["sessions"] == before + 2
    assert (
        a.turn("the large table").outcome == "ambiguo"
        and a.close()
        and a.turn("the clients").outcome == "unico"
    )
