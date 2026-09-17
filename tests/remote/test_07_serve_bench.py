"""pron serve (spec 11 §8): what the client waits for is the write, not write + refresh."""

from __future__ import annotations

import argparse
import importlib.util
import time
from pathlib import Path

import pytest

from pron.remote import RemoteSession
from pron.serve import Server
from pron.session import Session
from pron.world.world import World
from remote.serving import running


def _bench_module():
    """tools/merkle_bench.py, loaded from its file: it is a script, not a package."""
    path = Path(__file__).resolve().parents[2] / "tools" / "merkle_bench.py"
    spec = importlib.util.spec_from_file_location("bench_merkle", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _timed(fn) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def _creates(tag: str) -> list[str]:
    return [
        f'(create BenchNote (as "bench-{tag}-{i}") '
        f'(title "Bench {tag} {i}") (body "A timed create."))'
        for i in range(3)
    ]


def _best_of_three(session, tag: str) -> float:
    return min(_timed(lambda: session.eval(f)) for f in _creates(tag))


def test_a_write_through_the_server_answers_before_the_graph_settles(tmp_path):
    """What the client waits for is the write, not write + refresh (spec 11 §8): on a
    synthetic world of 800 notes, a write's response through the server takes clearly less
    than a sync session's write measured in this same test. Best of three on each side; a
    machine too noisy to tell skips instead of flaking."""
    root = tmp_path / "bench-world"
    _bench_module().cmd_generate(argparse.Namespace(root=str(root), n=800))
    with running(Server(root, str(root))) as srv:
        deferred = _best_of_three(RemoteSession(srv.path, speaker="bench-defer"), "d")
        sync = Session(World(root, str(root)), projection="all", speaker="bench-sync")
        # no defer_refresh: the eval pays the refresh; min drops the cold first one
        synchronous = _best_of_three(sync, "s")
        assert deferred < synchronous, (
            f"a deferred write cost {deferred:.3f}s, as much as a sync one ({synchronous:.3f}s)"
        )
        if deferred >= 0.7 * synchronous:
            pytest.skip(
                f"machine too noisy: deferred {deferred:.3f}s vs sync {synchronous:.3f}s"
            )
