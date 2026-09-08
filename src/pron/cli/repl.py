"""The REPL: one session kept open, one sentence per line (spec 08 step 8)."""

from __future__ import annotations

import sys
from typing import IO

from pron.session import Session
from pron.world import World

HELP = """:help            this
:trace           toggle the trace after every answer
:lexicon [MODEL] what this projection can say (or the verbs and fields of one model)
:state           dialogue state, referents, last move
:quit            leave
Anything else is a sentence to the world."""


def run(world: World, projection: str = "all", speaker: str = "", now: str | None = None,
        stdin: IO[str] = sys.stdin, stdout: IO[str] = sys.stdout) -> int:
    session = Session(world, projection=projection, speaker=speaker, now=now)
    trace = False
    print(f"pron · world {world.root.name} · projection {projection} · :help for commands", file=stdout)
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        if line in (":quit", ":q", ":exit"):
            break
        if line == ":help":
            print(HELP, file=stdout); continue
        if line == ":trace":
            trace = not trace; print(f"trace {'on' if trace else 'off'}", file=stdout); continue
        if line.startswith(":lexicon"):
            model = line.split(maxsplit=1)[1] if " " in line else None
            for row in session.lex.table(model):
                print(f"  {row['form']:<24} {row['kind']:<16} {row['ref']}", file=stdout)
            continue
        if line == ":state":
            d = session.dialogue
            print(f"state: {d.state} · singular: {d.singular} · set: {d.last_set} · pending: {d.pending.kind if d.pending else '-'}", file=stdout)
            continue
        response = session.turn(line)
        print(response.text, file=stdout)
        if trace:
            for t in response.trace:
                print(f"  · {t}", file=stdout)
    return 0
