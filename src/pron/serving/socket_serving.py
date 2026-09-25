"""The daemon's Unix socket (spec 11 §8): listening at one path, refusing to start over a
live server, and pointing every mounted world's `<root>/.pron/serve.sock` at it so a client
that only knows its world finds the daemon; the links and the socket go when it stops. With
`listen`, the same requests are also answered at a TCP address, for a client that does not
share this machine's filesystem (spec 12 §7).
"""

from __future__ import annotations

import socketserver
import threading
from pathlib import Path
from typing import Any, Callable

from pron.remote import alive, socket_path
from pron.remote.client import tcp_address
from pron.serving.request_handler import RequestHandler


class SocketServing:
    """The listening socket of one daemon and the links that point at it."""

    def __init__(self, path: Path, listen: str | None = None) -> None:
        self.path = path
        self.listen = self._listen_address(listen)
        self.links: list[Path] = []
        self._srv: socketserver.UnixStreamServer | None = None
        self._tcp: socketserver.TCPServer | None = None

    @staticmethod
    def _listen_address(listen: str | None) -> tuple[str, int] | None:
        if listen is None:
            return None
        address = tcp_address(listen)
        if address is None:
            raise ValueError(f"--listen takes HOST:PORT, not {listen!r}")
        return address

    @property
    def is_serving(self) -> bool:
        return self._srv is not None

    def link(self, root: Path) -> None:
        """<root>/.pron/serve.sock -> the daemon's socket, so `pron say --world <root>` finds it."""
        link = socket_path(root)
        if link == self.path or link.parent != root / ".pron":
            return
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(self.path)
        self.links.append(link)

    def serve(self, app: Any, roots: Callable[[], list[Path]]) -> None:
        """Listen until stopped, answering through `app`; `roots` are linked once listening."""
        self._take_path()
        self._srv = socketserver.UnixStreamServer(
            str(self.path), RequestHandler.bound_to(app)
        )
        for root in roots():
            self.link(root)
        self._listen(app)
        try:
            self._srv.serve_forever()
        finally:
            self._close()

    def _listen(self, app: Any) -> None:
        """The TCP side, on its own thread: the app answers one request at a time under its
        lock, whichever door the request came through."""
        if self.listen is None:
            return
        socketserver.TCPServer.allow_reuse_address = True
        self._tcp = socketserver.TCPServer(self.listen, RequestHandler.bound_to(app))
        threading.Thread(target=self._tcp.serve_forever, daemon=True).start()

    def _take_path(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() or self.path.is_symlink():
            if alive(self.path):
                raise RuntimeError(f"a server already listens at {self.path}")
            self.path.unlink()

    def _close(self) -> None:
        assert self._srv is not None
        self._srv.server_close()
        if self._tcp is not None:
            self._tcp.shutdown()
            self._tcp.server_close()
        for link in self.links:
            if link.is_symlink():
                link.unlink()
        if self.path.exists():
            self.path.unlink()

    def stop(self) -> None:
        if self._srv is not None:
            self._srv.shutdown()
