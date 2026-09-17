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

QUIT = (":quit", ":q", ":exit")


def run(
    session: Any,
    world_name: str,
    projection: str = "all",
    stdin: IO[str] = sys.stdin,
    stdout: IO[str] = sys.stdout,
) -> int:
    """session: a pron.session.Session or a pron.serve.RemoteSession; both answer turn()."""
    remote = hasattr(session, "path")
    print(
        f"pron · world {world_name} · projection {projection}{' · via server' if remote else ''} · :help for commands",
        file=stdout,
    )
    trace = False
    for line in (raw.strip() for raw in stdin):
        if line in QUIT:
            break
        if line:
            trace = _line(session, line, trace, remote, stdout)
    return 0


def _line(session: Any, line: str, trace: bool, remote: bool, stdout: IO[str]) -> bool:
    """Answer one non-empty line; returns whether the trace is on afterwards."""
    if line == ":trace":
        print(f"trace {'off' if trace else 'on'}", file=stdout)
        return not trace
    if not _command(session, line, remote, stdout):
        _sentence(session, line, trace, stdout)
    return trace


def _command(session: Any, line: str, remote: bool, stdout: IO[str]) -> bool:
    """`:help`, `:lexicon [MODEL]` or `:state` answered; False when the line is none of them."""
    if line == ":help":
        print(HELP, file=stdout)
    elif line.startswith(":lexicon"):
        _lexicon(session, line, remote, stdout)
    elif line == ":state":
        print(_state(session, remote), file=stdout)
    else:
        return False
    return True


def _lexicon(session: Any, line: str, remote: bool, stdout: IO[str]) -> None:
    model = line.split(maxsplit=1)[1] if " " in line else None
    rows = session.lexicon(model) if remote else session.lex.table(model)
    for row in rows:
        print(f"  {row['form']:<24} {row['kind']:<16} {row['ref']}", file=stdout)


def _state(session: Any, remote: bool) -> str:
    if remote:
        st = session.state()
        return f"state: {st['state']} · singular: {st['singular']} · set: {st['set']} · pending: {st['pending'] or '-'}"
    d = session.dialogue
    return f"state: {d.state} · singular: {d.singular} · set: {d.last_set} · pending: {d.pending.kind if d.pending else '-'}"


def _sentence(session: Any, line: str, trace: bool, stdout: IO[str]) -> None:
    response = session.turn(line)
    print(response.text, file=stdout)
    if trace:
        for t in response.trace:
            print(f"  · {t}", file=stdout)
