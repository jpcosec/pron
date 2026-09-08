"""Interactive loop over the same Meaning layer as `eval` and the surface command.

Implements atom-repl-shares-the-evaluator-and-answers-ambiguity-in-memory: no
side grammar, no parallel evaluator; disambiguation is SHRDLU-style dialogue
held in a local variable for the life of the process, not a file-persisted
session like the non-interactive CLI.
"""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from pron.bridges.kgdb_bridge import KgdbBridge
from pron.bridges.sldb_bridge import SldbBridge
from pron.cli.render import render
from pron.cli.surface import desugar
from pron.core.anchors import AnchorRegistry
from pron.core.evaluator import Evaluator
from pron.core.results import Ambiguous, SemanticError
from pron.core.sexpr import SExpr, SexprError, Symbol, parse, serialize

PENDING_MARK = "\u0000PENDING\u0000"
QUIT = (":q", ":quit", ":exit")


def run(root: Path, fmt: str = "text") -> int:
    """Read-eval-print loop: surface tokens or direct `(...)` Meaning, evaluated
    against the same Evaluator as `pron eval`. An ambiguous result opens a
    pending question; typing one of its candidates on the next line answers
    it in place of the ambiguous selector, entirely in memory."""
    sldb = SldbBridge(root)
    registry = AnchorRegistry(sldb)
    evaluator = Evaluator(sldb, KgdbBridge(root), registry)
    pending: dict[str, Any] | None = None
    trace = False
    print(_banner(root))
    while True:
        try:
            line = input("pron> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line in QUIT:
            return 0
        if line == ":help":
            print(_help(registry))
            continue
        if line in (":internals", ":trace"):
            trace = not trace
            print(f"internals: {'on' if trace else 'off'}")
            continue
        if pending is not None:
            if line in pending["candidates"]:
                pending = _step(_answer(pending["template"], line), evaluator, registry, fmt, trace)
                continue
            print("(la pregunta pendiente sigue abierta; respondé con una de las opciones)")
            continue
        expr = _read(line, registry)
        if isinstance(expr, SemanticError):
            print(render(expr, fmt)[0])
            continue
        pending = _step(expr, evaluator, registry, fmt, trace)


def _read(line: str, registry: AnchorRegistry):
    """A line starting with '(' is direct Meaning; anything else is surface tokens."""
    if line.startswith("("):
        try:
            return parse(line)
        except SexprError as e:
            return SemanticError(symbol=line[:40], message=f"s-expression inválida: {e}")
    try:
        tokens = shlex.split(line)
    except ValueError as e:
        return SemanticError(symbol=line[:40], message=f"comillas sin cerrar: {e}")
    return desugar(tokens, registry)


def _step(
    expr: SExpr, evaluator: Evaluator, registry: AnchorRegistry, fmt: str, trace: bool
) -> dict[str, Any] | None:
    """Trace grounding if asked, evaluate, print, and open a pending question if ambiguous."""
    if trace:
        print(_trace(expr, registry))
    result = evaluator.eval(expr)
    text, _ = render(result, fmt)
    print(text)
    if isinstance(result, Ambiguous):
        return {"template": _mark(expr), "candidates": result.candidates}
    return None


def _trace(expr: SExpr, registry: AnchorRegistry) -> str:
    """Show which anchor grounds each symbol before evaluating: the SHRDLU-style
    grounding step the default renderer never surfaces."""
    lines = ["· grounding:"]
    for name in _symbols(expr):
        anchor = registry.lookup(name)
        if not isinstance(anchor, SemanticError):
            lines.append(f"  {name} -> {anchor.kind} {anchor.ref}  ({anchor.motive})")
    return "\n".join(lines)


def _symbols(item: object) -> list[str]:
    if isinstance(item, list):
        return [name for x in item for name in _symbols(x)]
    if isinstance(item, Symbol):
        return [item.name]
    return []


def _mark(item: object) -> object:
    """Replace every string leaf with a marker, mirroring the CLI's own pending
    template (main.py:_mark_pending) so the same single-slot assumption holds."""
    if isinstance(item, list):
        return [_mark(x) for x in item]
    if isinstance(item, str):
        return PENDING_MARK
    return item


def _answer(template: object, choice: str) -> SExpr:
    return parse(serialize(template).replace(PENDING_MARK, choice))


def _banner(root: Path) -> str:
    return (
        f"pron — evaluador semánticamente anclado ({root})\n"
        '  comando surface: list atom · show atom "id"\n'
        "  Meaning directo:  (check (doc atom \"id\") :project title)\n"
        "  una pregunta con opciones espera tu respuesta en la línea siguiente (estilo SHRDLU)\n"
        "  :help gramática viva · :internals traza el grounding · :quit salir\n"
    )


def _help(registry: AnchorRegistry) -> str:
    rows = [f"  {a.symbol:<14} {a.kind:<10} {a.motive}" for a in registry.all()]
    return "gramática viva (anchors):\n" + "\n".join(rows)
