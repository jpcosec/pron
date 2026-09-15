#!/usr/bin/env python3
"""PLAN 15 (merkle) M5: the cost of one write, before/after, at different world sizes.

A repeatable stand-in for the manual measurement in PLAN-15-merkle.md's "Medición de
partida": prepare a world (a copy of an existing one, or a synthetic one with N documents
of one simple registered model), then time one `session.eval('(create ...)')` — the same
turn a `(create SelfDoc ...)` takes: interpretation is skipped (eval takes forms directly)
but resolve / pre-validate / execute / refresh / ledger.write all run for real.

Subcommands:
  prepare   --source DIR --root DIR         copy a world (like legos) and pron init+refresh it
  generate  --root DIR --n N                a fresh synthetic world with N BenchNote documents
  write     --world DIR [--pythonpath P] [--profile] [--model M] [--label L]
                                             time one create; prints one JSON line
  refresh   --world DIR [--pythonpath P] [--profile]
                                             time world.refresh() with nothing changed

PYTHONPATH must already carry the sldb/kgdb/pron clones (and, for `write`/`refresh`, the
world's own --pythonpath so its models import).
"""

from __future__ import annotations

import argparse
import cProfile
import json
import pstats
import shutil
import sys
import time
import uuid
from io import StringIO
from pathlib import Path

BENCH_MODEL_SOURCE = '''from pydantic import Field
from sldb import StructuredNLDoc


class BenchNote(StructuredNLDoc):
    """A minimal document for merkle cost measurements: two string fields, nothing else."""

    __template__ = "# \\u2e22rev\\u2022title\\u2e25\\n\\nBody: \\u2e22rev\\u2022body\\u2e25"
    title: str = Field(description="Title.")
    body: str = Field(description="Body text.")
'''

IGNORE = shutil.ignore_patterns(
    ".git", "ledger", "move-*", ".pron", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"
)


def cmd_prepare(args: argparse.Namespace) -> None:
    root = Path(args.root)
    if root.exists():
        shutil.rmtree(root)
    root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path(args.source), root, ignore=IGNORE)
    pythonpath = args.pythonpath or str(root)
    from pron.world import World, init_world

    init_world(root, pythonpath)
    report = World(root, pythonpath).refresh()
    print(json.dumps({"prepared": str(root), "pythonpath": pythonpath, **report}))


def cmd_generate(args: argparse.Namespace) -> None:
    root = Path(args.root)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "bench_models.py").write_text(BENCH_MODEL_SOURCE, encoding="utf-8")
    pythonpath = str(root)
    from sldb.cli import main as sldb_main
    from pron.store import Store
    from pron.world import World, init_world

    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, pythonpath)
    store = Store(root, pythonpath)
    if not store.register_model("bench_models:BenchNote"):
        raise SystemExit("could not register BenchNote")
    docs_dir = root / "knowledge" / "bench"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for i in range(args.n):
        name = f"note-{i:05d}"
        store.create(
            "BenchNote",
            name,
            {"title": f"Note {i}", "body": f"Generated body for bench note {i}."},
            docs_dir / f"{name}.md",
        )
    report = World(root, pythonpath).refresh()
    print(json.dumps({"generated": str(root), "pythonpath": pythonpath, "n": args.n, **report}))


def _time_call(fn, profile: bool) -> tuple[float, str]:
    if not profile:
        start = time.perf_counter()
        fn()
        return time.perf_counter() - start, ""
    pr = cProfile.Profile()
    start = time.perf_counter()
    pr.enable()
    fn()
    pr.disable()
    elapsed = time.perf_counter() - start
    buf = StringIO()
    stats = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    stats.print_stats(20)
    return elapsed, buf.getvalue()


def _model_fields(session, model: str) -> str:
    """One create form for `model`: BenchNote/SelfDoc/Note-shaped, the fields it actually has."""
    schema = {f["name"] for f in session.world.schema(model, session.lex.stores)}
    unique = uuid.uuid4().hex[:8]
    parts = [f'(create {model} (as "bench-{unique}")']
    values = {
        "title": f'"Bench {unique}"',
        "body": '"Generated for a merkle cost measurement."',
        "id": f'"bench-{unique}"',
        "name": f'"Bench {unique}"',
        "purpose": '"merkle cost measurement probe"',
        "responsibilities": '(list "measured")',
        "does_not": '(list "persist")',
    }
    for field, value in values.items():
        if field in schema:
            parts.append(f"({field} {value})")
    parts.append(")")
    return " ".join(parts)


def cmd_write(args: argparse.Namespace) -> None:
    """One (--repeat 1, default) or several creates in the same session: the first pays for
    opening a cold world (reading every index once — not what this plan is about); a second
    and later ones are the steady-state marginal cost of a write in an already-open session,
    which is what M2/M3/M4 change. Both numbers are printed; --repeat > 1 is how the 172 vs
    ~1500 docs comparison should be read."""
    from pron.session import Session
    from pron.world import World

    world = World(args.world, args.pythonpath)
    session = Session(world, projection="all", speaker="bench")
    docs_before = len(world.store.docs())
    runs = []

    def one(profile: bool) -> None:
        forms = args.forms or _model_fields(session, args.model)
        result: dict = {}

        def run() -> None:
            r = session.eval(forms)
            result["outcome"] = r.outcome

        elapsed, profile_text = _time_call(run, profile)
        runs.append({"elapsed_s": round(elapsed, 6), **result})
        if profile_text:
            print(profile_text, file=sys.stderr)

    for i in range(args.repeat):
        one(args.profile and i == args.repeat - 1)  # profile only the last: steady state
    out = {
        "label": args.label or "",
        "world": str(args.world),
        "docs_before": docs_before,
        "first_s": runs[0]["elapsed_s"],
        "steady_state_s": runs[-1]["elapsed_s"],
        "runs": runs,
    }
    print(json.dumps(out))


def cmd_refresh(args: argparse.Namespace) -> None:
    from pron.world import World

    world = World(args.world, args.pythonpath)
    world.refresh()  # warm: caches, on-disk indexes and .pron/graph.nx.json settle here

    def run() -> None:
        world.refresh()

    elapsed, profile_text = _time_call(run, args.profile)
    print(json.dumps({"label": args.label or "", "world": str(args.world), "elapsed_s": round(elapsed, 6)}))
    if profile_text:
        print(profile_text, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare")
    p.add_argument("--source", required=True)
    p.add_argument("--root", required=True)
    p.add_argument("--pythonpath")
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("generate")
    p.add_argument("--root", required=True)
    p.add_argument("--n", type=int, required=True)
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("write")
    p.add_argument("--world", required=True)
    p.add_argument("--pythonpath")
    p.add_argument("--model", default="BenchNote")
    p.add_argument("--forms", help="Override the create form entirely.")
    p.add_argument("--profile", action="store_true")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--label", default="")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("refresh")
    p.add_argument("--world", required=True)
    p.add_argument("--pythonpath")
    p.add_argument("--profile", action="store_true")
    p.add_argument("--label", default="")
    p.set_defaults(func=cmd_refresh)

    args = parser.parse_args()
    if getattr(args, "pythonpath", None) is None and args.cmd in ("write", "refresh"):
        args.pythonpath = str(args.world)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
