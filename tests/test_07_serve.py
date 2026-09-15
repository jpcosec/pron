"""pron serve (spec 11 §8): one process keeps the world open behind a Unix socket; the CLI,
the REPL and any client say through it, sessions live in the server, and a stale socket
does not fool a client."""

from __future__ import annotations

import argparse
import importlib.util
import io
import threading
import time
from pathlib import Path

import pytest

from pron.cli.main import main
from pron.cli.repl import run as repl
from pron.client import RemoteSession, alive, request, socket_path
from pron.serve import Server
from pron.session import Session
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
    assert (
        r.outcome == "unico" and "table 12" in r.text and r.move_id.startswith("move-")
    )
    r = s.turn("the large table")  # ambiguous: the server keeps the pending question
    assert r.outcome == "ambiguo"
    r = s.turn("1")
    assert r.outcome == "unico", r.text
    assert request(server.path, {"op": "ping"})["sessions"] == 1
    assert s.payload("Table", "table-12")["capacity"] >= 6


def test_the_cli_uses_the_server_when_it_listens(server: Server, capsys):
    root = str(server.world.root)
    assert (
        main(
            [
                "say",
                "the large tables on the terrace",
                "--world",
                root,
                "--speaker",
                "cli",
            ]
        )
        == 0
    )
    assert "table 12" in capsys.readouterr().out
    assert (
        request(server.path, {"op": "ping"})["sessions"] == 2
    )  # a new speaker, a new session, in the server
    assert (
        main(
            [
                "say",
                "the large tables",
                "--world",
                root,
                "--pythonpath",
                server.world.store.pythonpath,
                "--speaker",
                "cli",
                "--local",
            ]
        )
        == 0
    )
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


def test_a_write_through_the_server_is_a_real_move(server: Server):
    s = RemoteSession(server.path, projection="all", speaker="jp", now=NOW)
    r = s.turn("create a client named Zed Lee, phone 9 5555 0000")
    assert r.outcome == "unico" and r.record["writes"], r.text
    assert server.world.store.doc("Client", "client-zed-lee") is not None
    assert s.turn("the clients").outcome == "unico"


def test_a_deferred_session_records_the_refresh_and_a_graph_read_settles_it(world: World):
    """A session with defer_refresh (spec 11 §8) answers without the graph refresh: the
    world keeps it pending, and the first graph read — the server's settle, or any caller
    of world.graph — runs it and sees the node the write made."""
    from pron.graph import doc_id

    s = Session(world, projection="all", speaker="defer", now=NOW, defer_refresh=True)
    r = s.eval(
        '(create Client (as "client-settled-dee") (name "Settled Dee") (phone "9 5555 1111"))'
    )
    assert r.outcome == "unico", r.text
    assert "graph refresh deferred until after the response" in r.trace, r.trace
    assert world.has_pending_refresh
    assert world.graph.has_node(doc_id("Client:client-settled-dee"))  # the read settles it
    assert not world.has_pending_refresh


def test_a_write_through_the_server_is_seen_by_the_next_read(server: Server):
    """The answer leaves before the refresh (11 §8); the next request — a graph read here —
    waits for it and sees the write."""
    from pron.graph import doc_id

    s = RemoteSession(server.path, projection="all", speaker="settle", now=NOW)
    r = s.turn("create a client named Settled Sue, phone 9 5555 4321")
    assert r.outcome == "unico" and r.record["writes"], r.text
    assert any("deferred" in line for line in r.trace), r.trace
    assert s.graph.has_node(node_id=doc_id("Client:client-settled-sue"))
    assert not server.world.has_pending_refresh
    assert s.turn("the clients").outcome == "unico"


def _bench_module():
    """bench/merkle.py, loaded from its file: it is a script, not a package."""
    path = Path(__file__).resolve().parent.parent / "bench" / "merkle.py"
    spec = importlib.util.spec_from_file_location("bench_merkle", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_write_through_the_server_answers_before_the_graph_settles(tmp_path):
    """What the client waits for is the write, not write + refresh (spec 11 §8): on a
    synthetic world of 800 notes, a write's response through the server takes clearly less
    than a sync session's write measured in this same test. Best of three on each side; a
    machine too noisy to tell skips instead of flaking."""
    merkle = _bench_module()
    root = tmp_path / "bench-world"
    merkle.cmd_generate(argparse.Namespace(root=str(root), n=800))

    srv = Server(root, str(root))
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        for _ in range(100):
            if alive(srv.path):
                break
            time.sleep(0.05)
        assert alive(srv.path)

        def timed(fn):
            start = time.perf_counter()
            fn()
            return time.perf_counter() - start

        def creates(tag: str) -> list[str]:
            return [
                f'(create BenchNote (as "bench-{tag}-{i}") '
                f'(title "Bench {tag} {i}") (body "A timed create."))'
                for i in range(3)
            ]

        remote = RemoteSession(srv.path, speaker="bench-defer")
        deferred = min(timed(lambda: remote.eval(f)) for f in creates("d"))
        sync = Session(World(root, str(root)), projection="all", speaker="bench-sync")
        # no defer_refresh: the eval pays the refresh; min drops the cold first one
        synchronous = min(timed(lambda: sync.eval(f)) for f in creates("s"))
        assert deferred < synchronous, (
            f"a deferred write cost {deferred:.3f}s, as much as a sync one ({synchronous:.3f}s)"
        )
        if deferred >= 0.7 * synchronous:
            pytest.skip(
                f"machine too noisy: deferred {deferred:.3f}s vs sync {synchronous:.3f}s"
            )
    finally:
        if alive(srv.path):
            request(srv.path, {"op": "stop"})
            t.join(timeout=10)


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
    assert len(str(socket_path(deep))) < 60 and socket_path(deep).name.startswith(
        "pron-"
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


def test_payload_respects_the_session_projection(server: Server):
    proj = dict(server.world.projection("all"), name="tables-only", models=["Table"])
    server.world.store.create(
        "ProjectionDoc",
        "projection-tables-only",
        proj,
        server.world.root / "knowledge" / "projections" / "tables-only.md",
    )
    s = RemoteSession(server.path, projection="tables-only", speaker="narrow", now=NOW)
    assert s.payload("Table", "table-12")["number"] == 12
    with pytest.raises(RuntimeError, match="not in projection"):
        s.payload("Client", "client-luis-soto")


def test_graph_and_world_navigation_over_the_socket(server: Server):
    from pron.graph import doc_id

    s = RemoteSession(server.path, projection="all", speaker="nav", now=NOW)
    assert "Reservation" in s.world.model_names()
    assert "booked_by" in s.world.relation_types()
    res = doc_id("Reservation:reservation-2026-09-11-luis-soto")
    assert s.graph.targets(node_id=res, relation="booked_by") == [
        doc_id("Client:client-luis-soto")
    ]
    edges = s.graph.edges_from(node_id=res, relation="assigned_to")
    assert edges and set(edges[0]) == {"source", "target", "relation", "metadata"}
    assert res in s.graph.nodes_of_type(node_type="Reservation")
    with pytest.raises(RuntimeError, match="unknown method"):
        s.graph.call("load")
