"""pron command line. Every command is a thin door to a library function; the docs of
each command are generated from these handlers' docstrings (spec 08 step 9).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _cmd_init(args: argparse.Namespace) -> int:
    """Make a store a pron world.

    Runs kgdb init (typed relations) and registers pron's models: AnchorDoc, ProjectionDoc,
    MoveDoc; with --knowledge also SpecDoc, the command and module docs, and the relation
    type implements, for pron's own knowledge base. Idempotent.

    With --template DIR, the world is born with the words, projections and relation
    types the template holds (anchors/, projections/, relations/types/, relations/).

    Usage:
      pron init --world . [--pythonpath .] [--knowledge] [--template DIR]
    """
    from pron.world import init_world

    report = init_world(
        args.world,
        args.pythonpath,
        with_knowledge=args.knowledge,
        template=args.template,
    )
    print(json.dumps(report, indent=2))
    return 0


def _cmd_refresh(args: argparse.Namespace) -> int:
    """Rebuild the world's indexes and its typed graph.

    sldb stores update, then kgdb's typed ingest into .pron/graph.nx.json, in-process.

    Usage:
      pron refresh --world .
    """
    from pron.world import World

    report = World(args.world, args.pythonpath).refresh()
    print(
        f"graph: {report['nodes']} nodes, {report['edges']} edges, {len(report['relation_types'])} relation types"
    )
    return 0


def _cmd_lexicon(args: argparse.Namespace) -> int:
    """List what this projection can say.

    Every word with its kind, what it names and its motive; with a model, the verbs that
    class takes and its fields. Answers "what can I say?".

    Usage:
      pron lexicon --world . [--projection all] [MODEL] [--json]
    """
    from pron.lexicon import Lexicon
    from pron.world import World

    world = World(args.world, args.pythonpath)
    lex = Lexicon(world, world.projection(args.projection))
    rows = lex.table(args.model)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    width = max((len(r["form"]) for r in rows), default=10)
    for r in rows:
        print(f"{r['form']:<{width}}  {r['kind']:<16} {r['ref']:<48} {r['motive']}")
    return 0


def _session_for(args: argparse.Namespace):
    """A live session: through the running server when one listens at the world's socket
    (and --local was not asked), else opened here."""
    from pron.client import RemoteSession, alive, socket_path

    sock = (
        Path(args.socket) if getattr(args, "socket", None) else socket_path(args.world)
    )
    if not getattr(args, "local", False) and alive(sock):
        return RemoteSession(
            sock,
            projection=args.projection,
            speaker=args.speaker,
            now=args.now,
            world=str(Path(args.world).resolve()),
            home=getattr(args, "home", None),
        )
    from pron.session import Session
    from pron.world import World

    return Session(
        World(args.world, args.pythonpath),
        projection=args.projection,
        speaker=args.speaker,
        now=args.now,
    )


def _cmd_say(args: argparse.Namespace) -> int:
    """Say one sentence to a world and print the answer, with the trace on request.

    Opens a session with the projection and speaker given, runs one turn, prints the
    answer in natural language; --trace adds the addresses, edges and writes. When a
    `pron serve` listens at the world's socket the sentence goes there and nothing is
    opened here; --local forces opening the world in this process.

    Usage:
      pron say "what tables are on the terrace?" --world . [--projection all] [--speaker me] [--trace] [--local]
    """
    response = _session_for(args).turn(args.sentence)
    print(response.text)
    if args.trace:
        print("\n".join(f"  · {line}" for line in response.trace))
    return 0


def _cmd_repl(args: argparse.Namespace) -> int:
    """Talk to a world, one sentence per line.

    The same session as `say`, kept open: pending questions and referents survive between
    lines. `:trace` toggles the trace, `:lexicon [MODEL]` lists words, `:quit` leaves.
    Through the running server when one listens; --local opens the world here.

    Usage:
      pron repl --world . [--projection all] [--speaker me] [--local]
    """
    from pron.cli.repl import run

    return run(_session_for(args), Path(args.world).resolve().name, args.projection)


def _cmd_serve(args: argparse.Namespace) -> int:
    """Keep one or more worlds open and answer sentences over a Unix socket (spec 11 §8, 12 §7).

    Imports, caches and sessions are paid once; `say`, `repl` and runtimes use the socket
    while it listens. --world is repeatable, as PATH or NAME=PATH; the first is the default
    and its .pron/serve.sock is the daemon's socket unless --socket says otherwise; every
    other world gets a .pron/serve.sock pointing at it. A caller from another world may
    open only the projections a world exposes. Runs in the foreground until --stop is
    sent from another shell or the process is interrupted; --mount NAME=PATH adds a world
    to a running daemon.

    Usage:
      pron serve --world . [--world other=../other] [--pythonpath .] [--socket PATH]
      pron serve --world . --mount other=../other
      pron serve --world . --stop
    """
    from pron.client import alive, request, socket_path

    entries = []
    for spec in args.world if isinstance(args.world, list) else [args.world]:
        name, _, path = (
            spec.partition("=")
            if "=" in spec and not Path(spec).exists()
            else ("", "", spec)
        )
        entries.append((name or Path(path).resolve().name, path, args.pythonpath))
    sock = Path(args.socket) if args.socket else socket_path(entries[0][1])
    if args.stop:
        if not alive(sock):
            print(f"no server at {sock}")
            return 1
        request(sock, {"op": "stop"})
        print("stopped")
        return 0
    if args.mount:
        name, _, path = (
            args.mount.partition("=")
            if "=" in args.mount
            else (Path(args.mount).resolve().name, "", args.mount)
        )
        print(
            request(
                sock,
                {
                    "op": "mount",
                    "name": name,
                    "root": str(Path(path).resolve()),
                    "pythonpath": args.pythonpath,
                },
            )["world"]
        )
        return 0
    from pron.serve import Server

    server = Server(sock=sock, worlds=entries)
    print(
        f"pron serve · worlds {', '.join(f'{n}={root}' for n, root in server.worlds().items())} · socket {sock} · pid {os.getpid()}",
        flush=True,
    )
    server.serve_forever()
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    """Run pron's lints over a world and fail on any violation.

    Usage:
      pron check --world .
    """
    from pron.lints import run_lints
    from pron.world import World

    problems = run_lints(World(args.world, args.pythonpath))
    for p in problems:
        print(f"FAIL {p}")
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 0 if not problems else 1


def _cmd_docs(args: argparse.Namespace) -> int:
    """Regenerate pron's own knowledge base from this repo: a CliCommandDoc per command, a
    SurfaceDoc per module, a SpecDoc per chapter of source/spec, and the implements edges
    from each module to the chapters its docstring cites.

    Usage:
      pron docs --world . [--check]
    """
    from pron.docs import synchronize_docs
    from pron.world import World

    world = World(args.world, args.pythonpath)
    changed = synchronize_docs(world, check=args.check)
    print("\n".join(changed) if changed else "up to date")
    if changed and not args.check:
        world.refresh()  # the indexes and the graph follow the documents just written
    return 1 if (args.check and changed) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pron", description="pron: a SHRDLU over an sldb world."
    )
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--world", default=".", help="World root (contains .sldb)")
        sp.add_argument(
            "--pythonpath",
            default=None,
            help="Project path where the world's models import from",
        )

    s = sub.add_parser("init", help="Make a store a pron world")
    common(s)
    s.add_argument(
        "--knowledge",
        action="store_true",
        help="Also what pron's own knowledge base needs",
    )
    s.add_argument(
        "--template",
        default=None,
        help="World template directory: anchors/, projections/, relations/types/, relations/",
    )
    s.set_defaults(fn=_cmd_init)
    s = sub.add_parser("refresh", help="Rebuild indexes and the typed graph")
    common(s)
    s.set_defaults(fn=_cmd_refresh)
    s = sub.add_parser("lexicon", help="List what this projection can say")
    common(s)
    s.add_argument("model", nargs="?", default=None)
    s.add_argument("--projection", default="all")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=_cmd_lexicon)
    s = sub.add_parser("say", help="Say one sentence")
    common(s)

    def remote(sp):
        sp.add_argument(
            "--local",
            action="store_true",
            help="Open the world here even if a server listens",
        )
        sp.add_argument(
            "--socket",
            default=None,
            help="The daemon's socket, when the world's .pron/serve.sock is not it",
        )
        sp.add_argument(
            "--home",
            default=None,
            help="The caller's own world (name or path); another world opens only its exposed projections",
        )

    s.add_argument("sentence")
    s.add_argument("--projection", default="all")
    s.add_argument("--speaker", default="")
    s.add_argument("--now", default=None)
    s.add_argument("--trace", action="store_true")
    remote(s)
    s.set_defaults(fn=_cmd_say)
    s = sub.add_parser("repl", help="Talk to a world")
    common(s)
    s.add_argument("--projection", default="all")
    s.add_argument("--speaker", default="")
    s.add_argument("--now", default=None)
    remote(s)
    s.set_defaults(fn=_cmd_repl)
    s = sub.add_parser("serve", help="Keep worlds open behind a Unix socket")
    s.add_argument(
        "--world",
        action="append",
        required=True,
        help="World root, or NAME=PATH; repeatable, the first is the default",
    )
    s.add_argument(
        "--pythonpath",
        default=None,
        help="Project path where the worlds' models import from",
    )
    s.add_argument(
        "--socket",
        default=None,
        help="Socket path (default: the first world's .pron/serve.sock)",
    )
    s.add_argument(
        "--stop", action="store_true", help="Stop the server listening at the socket"
    )
    s.add_argument(
        "--mount", default=None, help="NAME=PATH to add a world to the running daemon"
    )
    s.set_defaults(fn=_cmd_serve)
    s = sub.add_parser("check", help="Run pron's lints")
    common(s)
    s.set_defaults(fn=_cmd_check)
    s = sub.add_parser("docs", help="Regenerate pron's command docs")
    common(s)
    s.add_argument("--check", action="store_true")
    s.set_defaults(fn=_cmd_docs)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
