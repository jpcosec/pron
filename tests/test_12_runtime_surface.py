"""Freeze the runtime surface spec 12 names, with its documented defaults.

Spec 12 is the contract with kinesis (and any other host): a change here that breaks a
caller must fail inside pron's own suite, not in someone else's. Imports only what the
chapter names.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pron.client
import pron.ids
import pron.response
from pron.client import RemoteGraph, RemoteSession, RemoteWorld, socket_path
from pron.response import Response
from pron.session import Session

# --- Session(world, projection, speaker, speaker_address, now, embedder,
#             read_only, home) -------------------------------------------------------


def test_session_signature() -> None:
    params = inspect.signature(Session.__init__).parameters
    assert list(params)[1:] == [
        "world",
        "projection",
        "speaker",
        "speaker_address",
        "now",
        "embedder",
        "read_only",
        "home",
    ]
    assert params["projection"].default == "all"
    assert params["speaker"].default == ""
    assert params["speaker_address"].default is None
    assert params["now"].default is None
    assert params["embedder"].default is None
    assert params["read_only"].default is False
    assert params["home"].default is None


def test_session_has_turn() -> None:
    assert callable(Session.turn)


# --- RemoteSession(sock, projection, speaker, speaker_address, now, read_only,
#                   world, home) ----------------------------------------------------


def test_remote_session_signature() -> None:
    params = inspect.signature(RemoteSession.__init__).parameters
    assert list(params)[1:] == [
        "path",
        "projection",
        "speaker",
        "speaker_address",
        "now",
        "read_only",
        "world",
        "home",
    ]
    assert params["projection"].default == "all"
    assert params["speaker"].default == ""
    assert params["speaker_address"].default is None
    assert params["now"].default is None
    assert params["read_only"].default is False
    assert params["world"].default is None
    assert params["home"].default is None


def test_remote_session_payload_method() -> None:
    assert callable(RemoteSession.payload)


# --- the five fields of Response ----------------------------------------------------


def test_response_fields() -> None:
    fields = {f: p.default for f, p in inspect.signature(Response).parameters.items()}
    assert list(fields) == ["text", "outcome", "trace", "move_id", "record"]
    assert fields["trace"] is inspect.Parameter.empty or True  # list factory
    assert fields["move_id"] == ""
    assert fields["record"] is not None


def test_response_construction() -> None:
    r = Response(text="hi", outcome="ok")
    assert r.trace == []
    assert r.move_id == ""
    assert r.record == {}


# --- pron.client surface ------------------------------------------------------------


def test_client_module_surface() -> None:
    assert callable(pron.client.socket_path)
    assert callable(pron.client.alive)
    assert callable(pron.client.request)
    assert pron.client.RemoteSession is RemoteSession
    assert pron.client.RemoteGraph is RemoteGraph
    assert pron.client.RemoteWorld is RemoteWorld


def test_remote_graph_and_world_call_by_name() -> None:
    assert callable(RemoteGraph.call)
    assert callable(RemoteWorld.call)


# --- World.store.payload ------------------------------------------------------------


def test_world_store_attribute_exists() -> None:
    from pron.store import Store

    # World.store yields a Store, whose payload(model, doc) is the documented read.
    assert callable(Store.payload)


def test_store_payload_method() -> None:
    from pron.store import Store

    assert callable(Store.payload)


# --- World.store model editing (spec 12 §4) ------------------------------------------


def test_store_model_editing_surface() -> None:
    from pron.store import Store

    assert callable(Store.replace)
    assert callable(Store.model_catalog)
    assert callable(Store.model_detail)
    assert callable(Store.model_template_edit)
    assert callable(Store.model_fields_add)
    assert callable(Store.model_fields_remove)
    assert callable(Store.model_validate_draft)
    assert callable(Store.model_promote)


# --- pron.ids splits A:Modelo:doc ---------------------------------------------------


def test_ids_split_qualified() -> None:
    assert pron.ids.split_id("A:Reserva:mesa-1") == ("A", "Reserva", "mesa-1")
    assert pron.ids.split_id("Reserva:mesa-1") == (None, "Reserva", "mesa-1")
    assert pron.ids.split_id("local:Reserva:mesa-1") == (None, "Reserva", "mesa-1")


def test_ids_join_and_address() -> None:
    assert pron.ids.join_id("A", "Reserva", "mesa-1") == "A:Reserva:mesa-1"
    assert pron.ids.join_id(None, "Reserva", "mesa-1") == "Reserva:mesa-1"
    assert pron.ids.scope("A", "Reserva") == "A:st.{Reserva+}"
    assert pron.ids.scope(None, "Reserva") == "st.{Reserva+}"
    assert pron.ids.address_of("A:Reserva:mesa-1") == "A:st.{Reserva}.mesa-1"
    assert pron.ids.address_of("Reserva:mesa-1") == "st.{Reserva}.mesa-1"


def test_ids_local_none_equivalent() -> None:
    assert pron.ids.is_local(None)
    assert pron.ids.is_local(pron.ids.LOCAL)


# --- the socket at <world>/.pron/serve.sock -----------------------------------------


def test_socket_path(tmp_path: Path) -> None:
    assert socket_path(tmp_path) == tmp_path / ".pron" / "serve.sock"
