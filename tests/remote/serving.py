"""A pron server running on a thread for as long as a test needs it."""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from pron.remote import alive, request
from pron.serve import Server


def _wait_alive(path: Path) -> None:
    for _ in range(100):
        if alive(path):
            break
        time.sleep(0.05)
    assert alive(path)


def _stop(path: Path, t: threading.Thread) -> None:
    if alive(path):
        request(path, {"op": "stop"})
        t.join(timeout=10)


@contextmanager
def running(srv: Server, sock: Path | None = None) -> Iterator[Server]:
    """Serve on a daemon thread until the socket answers; stop the server on the way out."""
    path = sock or srv.path
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        _wait_alive(path)
        yield srv
    finally:
        _stop(path, t)
