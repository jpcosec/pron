"""The REPL: one session kept open, one sentence per line (spec 08 step 8)."""

from __future__ import annotations

import sys
from typing import IO

from typing import Any

HELP = """:help            this
:trace           toggle the trace after every answer
:lexicon [MODEL] what this projection can say (or the verbs and fields of one model)
:state           dialogue state, referents, last move
:quit            leave
Anything else is a sentence to the world."""


def run(
    session: Any,
    world_name: str,
    projection: str = "all",
    stdin: IO[str] = sys.stdin,
    stdout: IO[str] = sys.stdout,
) -> int:
    """session: a pron.session.Session or a pron.serve.RemoteSession; both answer turn()."""
    trace = False
    remote = hasattr(session, "path")
    print(
        f"pron · world {world_name} · projection {projection}{' · via server' if remote else ''} · :help for commands",
        file=stdout,
    )
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        if line in (":quit", ":q", ":exit"):
            break
        if line == ":help":
            print(HELP, file=stdout)
            continue
        if line == ":trace":
            trace = not trace
            print(f"trace {'on' if trace else 'off'}", file=stdout)
            continue
        if line.startswith(":lexicon"):
            model = line.split(maxsplit=1)[1] if " " in line else None
            rows = session.lexicon(model) if remote else session.lex.table(model)
            for row in rows:
                print(
                    f"  {row['form']:<24} {row['kind']:<16} {row['ref']}", file=stdout
                )
            continue
        if line == ":state":
            if remote:
                st = session.state()
                print(
                    f"state: {st['state']} · singular: {st['singular']} · set: {st['set']} · pending: {st['pending'] or '-'}",
                    file=stdout,
                )
            else:
                d = session.dialogue
                print(
                    f"state: {d.state} · singular: {d.singular} · set: {d.last_set} · pending: {d.pending.kind if d.pending else '-'}",
                    file=stdout,
                )
            continue
        response = session.turn(line)
        print(response.text, file=stdout)
        if trace:
            for t in response.trace:
                print(f"  · {t}", file=stdout)
    return 0
