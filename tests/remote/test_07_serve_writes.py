"""pron serve (spec 11 §8): a write through the server is a real move, and the answer leaves
before the graph refresh that the next read waits for."""

from __future__ import annotations

from pron.remote import RemoteSession
from pron.serve import Server
from pron.session import Session
from pron.world.graph import doc_id
from pron.world.world import World

NOW = "2026-09-09"


def test_a_write_through_the_server_is_a_real_move(server: Server):
    s = RemoteSession(server.path, projection="all", speaker="jp", now=NOW)
    r = s.turn("create a client named Zed Lee, phone 9 5555 0000")
    assert r.outcome == "unico" and r.record["writes"], r.text
    assert server.world.store.doc("Client", "client-zed-lee") is not None
    assert s.turn("the clients").outcome == "unico"


def test_a_deferred_session_records_the_refresh_and_a_graph_read_settles_it(
    world: World,
):
    """A session with defer_refresh (spec 11 §8) answers without the graph refresh: the
    world keeps it pending, and the first graph read — the server's settle, or any caller
    of world.graph — runs it and sees the node the write made."""
    s = Session(world, projection="all", speaker="defer", now=NOW, defer_refresh=True)
    r = s.eval(
        '(create Client (as "client-settled-dee") (name "Settled Dee") (phone "9 5555 1111"))'
    )
    assert r.outcome == "unico", r.text
    assert "graph refresh deferred until after the response" in r.trace, r.trace
    assert world.has_pending_refresh
    assert world.graph.has_node(
        doc_id("Client:client-settled-dee")
    )  # the read settles it
    assert not world.has_pending_refresh


def test_a_write_through_the_server_is_seen_by_the_next_read(server: Server):
    """The answer leaves before the refresh (11 §8); the next request — a graph read here —
    waits for it and sees the write."""
    s = RemoteSession(server.path, projection="all", speaker="settle", now=NOW)
    r = s.turn("create a client named Settled Sue, phone 9 5555 4321")
    assert r.outcome == "unico" and r.record["writes"], r.text
    assert any("deferred" in line for line in r.trace), r.trace
    assert s.graph.has_node(node_id=doc_id("Client:client-settled-sue"))
    assert not server.world.has_pending_refresh
    assert s.turn("the clients").outcome == "unico"
