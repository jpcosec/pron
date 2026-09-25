"""`pron serve`: worlds kept open behind a Unix socket (spec 11 §8, spec 12 §7)."""

from __future__ import annotations

import os
from pathlib import Path

import click


@click.command("serve", short_help="Keep worlds open behind a Unix socket")
@click.option(
    "--world",
    multiple=True,
    required=True,
    help="World root, or NAME=PATH; repeatable, the first is the default",
)
@click.option(
    "--pythonpath",
    default=None,
    help="Project path where the worlds' models import from",
)
@click.option(
    "--socket",
    default=None,
    help="Socket path (default: the first world's .pron/serve.sock)",
)
@click.option(
    "--listen",
    default=None,
    help="HOST:PORT to answer over TCP too, for clients outside this filesystem",
)
@click.option("--stop", is_flag=True, help="Stop the server listening at the socket")
@click.option(
    "--mount", default=None, help="NAME=PATH to add a world to the running daemon"
)
def command(
    world: tuple[str, ...],
    pythonpath: str | None,
    socket: str | None,
    listen: str | None,
    stop: bool,
    mount: str | None,
) -> int:
    """Keep one or more worlds open and answer sentences over a Unix socket (spec 11 §8, 12 §7).

    Imports, caches and sessions are paid once; `say`, `repl` and runtimes use the socket
    while it listens. --world is repeatable, as PATH or NAME=PATH; the first is the default
    and its .pron/serve.sock is the daemon's socket unless --socket says otherwise; every
    other world gets a .pron/serve.sock pointing at it. A caller from another world may
    open only the projections a world exposes. Runs in the foreground until --stop is
    sent from another shell or the process is interrupted; --mount NAME=PATH adds a world
    to a running daemon; --listen HOST:PORT answers the same requests over TCP too, for a
    client in another container or machine (nothing authenticates: keep it on a private
    network).

    Usage:
      pron serve --world . [--world other=../other] [--pythonpath .] [--socket PATH] [--listen HOST:PORT]
      pron serve --world . --mount other=../other
      pron serve --world . --stop
    """
    from pron.remote import socket_path

    entries: list[tuple[str, str | Path, str | None]] = [
        _entry(spec, pythonpath) for spec in world
    ]
    sock = Path(socket) if socket else socket_path(entries[0][1])
    if stop:
        return _stop(sock)
    if mount:
        return _mount(sock, mount, pythonpath)
    return _serve(sock, entries, listen)


def _entry(spec: str, pythonpath: str | None) -> tuple[str, str, str | None]:
    """A --world value as (name, path, pythonpath): NAME=PATH, or a PATH named after itself."""
    if "=" in spec and not Path(spec).exists():
        name, _, path = spec.partition("=")
    else:
        name, path = "", spec
    return (name or Path(path).resolve().name, path, pythonpath)


def _stop(sock: Path) -> int:
    from pron.remote import alive, request

    if not alive(sock):
        print(f"no server at {sock}")
        return 1
    request(sock, {"op": "stop"})
    print("stopped")
    return 0


def _mount(sock: Path, mount: str, pythonpath: str | None) -> int:
    from pron.remote import request

    if "=" in mount:
        name, _, path = mount.partition("=")
    else:
        name, path = Path(mount).resolve().name, mount
    root = str(Path(path).resolve())
    message = {"op": "mount", "name": name, "root": root, "pythonpath": pythonpath}
    print(request(sock, message)["world"])
    return 0


def _serve(
    sock: Path, entries: list[tuple[str, str | Path, str | None]], listen: str | None
) -> int:
    from pron.serve import Server

    server = Server(sock=sock, worlds=entries, listen=listen)
    worlds = ", ".join(f"{n}={root}" for n, root in server.worlds().items())
    print(
        f"pron serve · worlds {worlds} · socket {sock}"
        f"{f' · tcp {listen}' if listen else ''} · pid {os.getpid()}",
        flush=True,
    )
    server.serve_forever()
    return 0
