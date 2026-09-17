"""pron serve (spec 11 §8): where the socket lives, a stale socket does not fool a client, and
what a client reads over it stays inside its projection."""

from __future__ import annotations

import pytest

from pron.remote import RemoteSession, alive, request, socket_path
from pron.serve import Server
from pron.world.graph import doc_id
from pron.world.world import World

NOW = "2026-09-09"


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
