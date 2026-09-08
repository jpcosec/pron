"""pron serve (spec 11 §8): one process keeps the world open behind a Unix socket; the CLI,
the REPL and any client say through it, sessions live in the server, and a stale socket
does not fool a client."""

from __future__ import annotations

import io
import threading
import time

import pytest

from pron.cli.main import main
from pron.cli.repl import run as repl
from pron.client import RemoteSession, alive, request, socket_path
from pron.serve import Server
from pron.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def server(world: World):
    srv = Server(world.root, world.store.pythonpath)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    for _ in range(100):
        if alive(srv.path):
            break
        time.sleep(0.05)
    assert alive(srv.path)
    yield srv
    request(srv.path, {"op": "stop"})
    t.join(timeout=10)


def test_a_client_says_through_the_server_and_the_session_lives_there(server: Server):
    s = RemoteSession(server.path, projection="all", speaker="jp", now=NOW)
    r = s.turn("the large tables")
    assert r.outcome == "unico" and "table 12" in r.text and r.move_id.startswith("move-")
    r = s.turn("the large table")                        # ambiguous: the server keeps the pending question
    assert r.outcome == "ambiguo"
    r = s.turn("1")
    assert r.outcome == "unico", r.text
    assert request(server.path, {"op": "ping"})["sessions"] == 1
    assert s.payload("Table", "table-12")["capacity"] >= 6


def test_the_cli_uses_the_server_when_it_listens(server: Server, capsys):
    root = str(server.world.root)
    assert main(["say", "the large tables on the terrace", "--world", root, "--speaker", "cli"]) == 0
    assert "table 12" in capsys.readouterr().out
    assert request(server.path, {"op": "ping"})["sessions"] == 2   # a new speaker, a new session, in the server
    assert main(["say", "the large tables", "--world", root, "--pythonpath", server.world.store.pythonpath, "--speaker", "cli", "--local"]) == 0
    assert request(server.path, {"op": "ping"})["sessions"] == 2   # --local opened the world here


def test_the_repl_runs_over_the_server(server: Server):
    out = io.StringIO()
    s = RemoteSession(server.path, projection="all", speaker="repl", now=NOW)
    assert repl(s, "restaurant", "all", stdin=io.StringIO("the large tables\n:state\n:lexicon Table\n:quit\n"), stdout=out) == 0
    text = out.getvalue()
    assert "via server" in text and "table 12" in text and "state: libre" in text and "capacity" in text


def test_a_write_through_the_server_is_a_real_move(server: Server):
    s = RemoteSession(server.path, projection="all", speaker="jp", now=NOW)
    r = s.turn("create a client named Zed Lee, phone 9 5555 0000")
    assert r.outcome == "unico" and r.record["writes"], r.text
    assert server.world.store.doc("Client", "client-zed-lee") is not None
    assert s.turn("the clients").outcome == "unico"


def test_a_stale_socket_file_is_not_a_server(tmp_path):
    sock = tmp_path / "serve.sock"
    sock.write_text("")
    assert not alive(sock)
    with pytest.raises(ConnectionError):
        request(sock, {"op": "ping"})


def test_socket_path_is_under_the_world_unless_too_long(world: World, tmp_path):
    short = tmp_path / "w"
    assert socket_path(short) == short.resolve() / ".pron" / "serve.sock"
    deep = tmp_path / ("x" * 120) / "world"
    assert len(str(socket_path(deep))) < 60 and socket_path(deep).name.startswith("pron-")
