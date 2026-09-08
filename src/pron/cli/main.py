"""knowledge CLI entry point: the semantically anchored evaluator surface.

Implements the usability spec: surface grammar, direct eval, clarification
dialogue, anchors listing, and the infra layer (model add / project).
"""

from __future__ import annotations

import sys
from pathlib import Path

from pron.bridges.kgdb_bridge import KgdbBridge
from pron.bridges.sldb_bridge import SldbBridge
from pron.core.anchors import AnchorRegistry
from pron.core.evaluator import Evaluator
from pron.core.results import Ambiguous, SemanticError
from pron.core.sexpr import SexprError, parse, serialize
from pron.core.session import Session
from pron.cli.render import render
from pron.cli.surface import desugar


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    fmt = "json"
    if "--format" in args:
        i = args.index("--format")
        fmt = args[i + 1]
        del args[i : i + 2]
    root = Path.cwd()
    if "--kb" in args:
        i = args.index("--kb")
        root = Path(args[i + 1]).resolve()
        del args[i : i + 2]

    if not args:
        print(_help())
        return 0

    sldb = SldbBridge(root)
    registry = AnchorRegistry(sldb)

    # infra / meta commands first
    if args[0] == "anchor" and len(args) >= 2 and args[1] == "add":
        return _cmd_anchor_add(root, args[2:])
    if args[0] == "anchors":
        return _cmd_anchors(registry, args[1:], fmt)
    if args[0] == "model" and len(args) >= 3 and args[1] == "add":
        from pron.infra.projector import model_add

        ok, msg = model_add(root, args[2])
        print(msg)
        return 0 if ok else 1
    if args[0] == "project":
        from pron.infra.projector import refresh

        ok, msg = refresh(root)
        print(msg)
        return 0 if ok else 1
    if args[0] == "docs":
        from pron.bridges.documentation_bridge import synchronize_documentation

        ok, msg = synchronize_documentation(root, check="--check" in args[1:])
        print(msg)
        return 0 if ok else 1
    if args[0] == "eval" and len(args) >= 2:
        return _run_expr_text(args[1], root, sldb, registry, fmt)

    # surface command (possibly a clarification answer)
    return _run_surface(args, root, sldb, registry, fmt)


def _cmd_anchor_add(root: Path, rest: list[str]) -> int:
    """knowledge anchor add <symbol> --kind <k> --ref <r> --motive <text>."""
    from pron.ops.anchor_add import anchor_add

    flags: dict[str, str | None] = {"--kind": None, "--ref": None, "--motive": None}
    positional: list[str] = []
    i = 0
    while i < len(rest):
        t = rest[i]
        if t in flags and i + 1 < len(rest):
            flags[t] = rest[i + 1]
            i += 2
        else:
            positional.append(t)
            i += 1
    if not positional:
        print("uso: knowledge anchor add <symbol> --kind <model|doc|relation|operation|projection> --ref <typed-ref> --motive <text>")
        return 1
    if flags["--kind"] is None or flags["--ref"] is None or flags["--motive"] is None:
        print("error: se requieren --kind, --ref y --motive")
        return 1
    ok, msg = anchor_add(root, positional[0], flags["--kind"], flags["--ref"], flags["--motive"])
    print(msg)
    return 0 if ok else 1


def _cmd_anchors(registry: AnchorRegistry, rest: list[str], fmt: str) -> int:
    """The living grammar: all anchors, or one symbol's motive."""
    if rest:
        anchor = registry.lookup(rest[0])
        text, code = render(
            anchor if isinstance(anchor, SemanticError) else _anchor_result(anchor), fmt
        )
        print(text)
        return code
    rows = [
        {"symbol": a.symbol, "kind": a.kind, "ref": a.ref, "motive": a.motive}
        for a in registry.all()
    ]
    from pron.core.results import OperationResult

    text, code = render(OperationResult(status="ok", payload=rows), fmt)
    print(text)
    return code


def _anchor_result(anchor):
    from pron.core.results import OperationResult

    return OperationResult(
        status="ok",
        payload={
            "symbol": anchor.symbol,
            "kind": anchor.kind,
            "ref": anchor.ref,
            "motive": anchor.motive,
        },
    )


def _run_surface(tokens: list[str], root, sldb, registry, fmt: str) -> int:
    session = Session(root, sldb.store_hash())
    pending = session.load()
    if pending and len(tokens) == 1 and tokens[0] in pending["candidates"]:
        expr_text = pending["pending_sexpr"].replace("\u0000PENDING\u0000", tokens[0])
        session.clear()
        return _run_expr_text(expr_text, root, sldb, registry, fmt)
    if pending:
        session.clear()

    expr = desugar(tokens, registry)
    if isinstance(expr, SemanticError):
        text, code = render(expr, fmt)
        print(text)
        return code
    return _run_expr(expr, root, sldb, registry, fmt)


def _run_expr_text(text: str, root, sldb, registry, fmt: str) -> int:
    try:
        expr = parse(text)
    except SexprError as e:
        err = SemanticError(symbol=text[:40], message=f"s-expression inválida: {e}")
        out, code = render(err, fmt)
        print(out)
        return code
    return _run_expr(expr, root, sldb, registry, fmt)


def _run_expr(expr, root, sldb, registry, fmt: str) -> int:
    evaluator = Evaluator(sldb, KgdbBridge(root), registry)
    result = evaluator.eval(expr)
    if isinstance(result, Ambiguous):
        _save_pending(expr, result, root, sldb)
    text, code = render(result, fmt)
    print(text)
    return code


def _save_pending(expr, ambiguous: Ambiguous, root, sldb) -> None:
    """Persist the expression with the ambiguous selector marked for replacement."""
    template = serialize(_mark_pending(expr))
    Session(root, sldb.store_hash()).save(template, ambiguous.candidates)


def _mark_pending(item):
    if isinstance(item, list):
        return [_mark_pending(x) for x in item]
    if isinstance(item, str):
        return "\u0000PENDING\u0000"
    return item


def _help() -> str:
    return (
        "pron — evaluador semánticamente anclado sobre sldb+kgdb\n\n"
        "  pron <tokens...> [--<projection>]   comando surface\n"
        "  pron eval '<s-expr>'                capa Meaning directa\n"
        "  pron anchors [symbol]               gramática viva\n"
        "  pron anchor add <symbol> --kind <k> --ref <r> --motive <text>\n"
        "  pron model add <module:Class>       declara un modelo\n"
        "  pron project                        refresca índices sldb + grafo kgdb\n"
        "  pron docs [--check]                 deriva/verifica docs de CLI y módulos\n\n"
        "Opciones: --kb <root>  --format json|text\n"
    )


if __name__ == "__main__":
    sys.exit(main())
