"""pron command line. Every command is a thin door to a library function; the docs of
each command are generated from these handlers' docstrings (spec 08 step 9).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pron.world import World, init_world


def _cmd_init(args: argparse.Namespace) -> int:
    """Make a store a pron world.

    Runs kgdb init (typed relations) and registers pron's models: AnchorDoc, ProjectionDoc,
    MoveDoc, and Atom with --atoms. Idempotent.

    Usage:
      pron init --world . [--pythonpath .] [--atoms]
    """
    report = init_world(args.world, args.pythonpath, with_atoms=args.atoms)
    print(json.dumps(report, indent=2))
    return 0


def _cmd_refresh(args: argparse.Namespace) -> int:
    """Rebuild the world's indexes and its typed graph.

    sldb stores update, then kgdb's typed ingest into .pron/graph.nx.json, in-process.

    Usage:
      pron refresh --world .
    """
    report = World(args.world, args.pythonpath).refresh()
    print(f"graph: {report['nodes']} nodes, {report['edges']} edges, {len(report['relation_types'])} relation types")
    return 0


def _cmd_lexicon(args: argparse.Namespace) -> int:
    """List what this projection can say.

    Every word with its kind, what it names and its motive; with a model, the verbs that
    class takes and its fields. Answers "what can I say?".

    Usage:
      pron lexicon --world . [--projection all] [MODEL] [--json]
    """
    from pron.lexicon import Lexicon

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


def _cmd_say(args: argparse.Namespace) -> int:
    """Say one sentence to a world and print the answer, with the trace on request.

    Opens a session with the projection and speaker given, runs one turn, prints the
    answer in natural language; --trace adds the addresses, edges and writes.

    Usage:
      pron say "what tables are on the terrace?" --world . [--projection all] [--speaker me] [--trace]
    """
    from pron.session import Session

    session = Session(World(args.world, args.pythonpath), projection=args.projection, speaker=args.speaker, now=args.now)
    response = session.turn(args.sentence)
    print(response.text)
    if args.trace:
        print("\n".join(f"  · {line}" for line in response.trace))
    return 0


def _cmd_repl(args: argparse.Namespace) -> int:
    """Talk to a world, one sentence per line.

    The same session as `say`, kept open: pending questions and referents survive between
    lines. `:trace` toggles the trace, `:lexicon [MODEL]` lists words, `:quit` leaves.

    Usage:
      pron repl --world . [--projection all] [--speaker me]
    """
    from pron.cli.repl import run

    return run(World(args.world, args.pythonpath), args.projection, args.speaker, args.now)


def _cmd_check(args: argparse.Namespace) -> int:
    """Run pron's lints over a world and fail on any violation.

    Usage:
      pron check --world .
    """
    from pron.lints import run_lints

    problems = run_lints(World(args.world, args.pythonpath))
    for p in problems:
        print(f"FAIL {p}")
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 0 if not problems else 1


def _cmd_docs(args: argparse.Namespace) -> int:
    """Regenerate pron's own CliCommandDoc and SurfaceDoc documents from this code.

    Usage:
      pron docs --world . [--check]
    """
    from pron.docs import synchronize_docs

    changed = synchronize_docs(World(args.world, args.pythonpath), check=args.check)
    print("\n".join(changed) if changed else "up to date")
    return 1 if (args.check and changed) else 0


def _cmd_migrate_atoms(args: argparse.Namespace) -> int:
    """Migrate v1 atoms (deskops AtomDoc markdown files) into this world's Atom model.

    Usage:
      pron migrate-atoms SRC_DIR --world .
    """
    from pron.migrate import migrate_atoms

    report = migrate_atoms(World(args.world, args.pythonpath), Path(args.src))
    print(json.dumps(report, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pron", description="pron: a SHRDLU over an sldb world.")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--world", default=".", help="World root (contains .sldb)")
        sp.add_argument("--pythonpath", default=None, help="Project path where the world's models import from")

    s = sub.add_parser("init", help="Make a store a pron world"); common(s); s.add_argument("--atoms", action="store_true"); s.set_defaults(fn=_cmd_init)
    s = sub.add_parser("refresh", help="Rebuild indexes and the typed graph"); common(s); s.set_defaults(fn=_cmd_refresh)
    s = sub.add_parser("lexicon", help="List what this projection can say"); common(s)
    s.add_argument("model", nargs="?", default=None); s.add_argument("--projection", default="all"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=_cmd_lexicon)
    s = sub.add_parser("say", help="Say one sentence"); common(s)
    s.add_argument("sentence"); s.add_argument("--projection", default="all"); s.add_argument("--speaker", default=""); s.add_argument("--now", default=None); s.add_argument("--trace", action="store_true"); s.set_defaults(fn=_cmd_say)
    s = sub.add_parser("repl", help="Talk to a world"); common(s)
    s.add_argument("--projection", default="all"); s.add_argument("--speaker", default=""); s.add_argument("--now", default=None); s.set_defaults(fn=_cmd_repl)
    s = sub.add_parser("check", help="Run pron's lints"); common(s); s.set_defaults(fn=_cmd_check)
    s = sub.add_parser("docs", help="Regenerate pron's command docs"); common(s); s.add_argument("--check", action="store_true"); s.set_defaults(fn=_cmd_docs)
    s = sub.add_parser("migrate-atoms", help="Migrate v1 atoms into Atom"); common(s); s.add_argument("src"); s.set_defaults(fn=_cmd_migrate_atoms)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
