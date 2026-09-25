"""pron serve --listen (spec 12 §7): the same requests answered at HOST:PORT, for a client that
does not share the daemon's filesystem."""

from __future__ import annotations

import socket

import pytest
from pron.remote import RemoteSession, alive, request, tcp_address
from pron.serve import Server
from pron.world.world import World
from remote.serving import running


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def tcp(world: World, tmp_path_factory):
    address = f"127.0.0.1:{_free_port()}"
    sock = tmp_path_factory.mktemp("tcp") / "pron.sock"
    with running(
        Server(world.root, world.store.pythonpath, sock=sock, listen=address), sock
    ):
        yield address


def test_an_address_is_a_path_unless_it_is_host_and_port(tmp_path):
    assert tcp_address("kb-grifo:8200") == ("kb-grifo", 8200)
    assert tcp_address(tmp_path / "serve.sock") is None
    assert tcp_address("./a:1/serve.sock") is None


def test_nobody_listening_at_an_address():
    address = f"127.0.0.1:{_free_port()}"
    assert not alive(address)
    with pytest.raises(ConnectionError):
        request(address, {"op": "ping"})


def test_the_daemon_answers_over_tcp_what_it_answers_over_its_socket(
    tcp: str, world: World
):
    assert alive(tcp)
    assert request(tcp, {"op": "worlds"})["worlds"]
    answer = RemoteSession(tcp, now="2026-09-09").turn("the table 3")
    assert answer.outcome == "unico" and answer.text
    assert RemoteSession(tcp).world.model_names() == world.model_names()


def test_listen_takes_host_and_port(world: World):
    with pytest.raises(ValueError, match="HOST:PORT"):
        Server(world.root, world.store.pythonpath, listen="8200")
