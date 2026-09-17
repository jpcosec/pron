"""Invoke pron's CLI in-process and capture its behavior: exit code, stdout, stderr, or the
exception that escaped. Usage errors keep only that the command failed and its exit code: their
wording belongs to the argument parser, not to pron."""

from __future__ import annotations

import re
from typing import Any

from pron.cli.main import main
from golden.normalize import Normalizer

PID = re.compile(r"\bpid \d+")  # the process id of the test run
ROW = re.compile(r"^(\s*)(\S.*?)(\s{2,}\S.*)$")


def relation_forms(text: str) -> str:
    """A relation's two forms, `booked_by` and `booked by`, are listed in the order a Python set
    yields them (pron.world.lexicon, _relation_words), and that follows PYTHONHASHSEED. Only such
    an adjacent pair of rows, equal but for the form, is put in one order (the identifier first);
    every other row keeps its place, so any other reordering still shows."""
    lines = text.split("\n")
    for i in range(len(lines) - 1):
        a, b = ROW.match(lines[i]), ROW.match(lines[i + 1])
        if a and b and _same_relation_row(a, b) and "_" in b.group(2):
            lines[i], lines[i + 1] = lines[i + 1], lines[i]
    return "\n".join(lines)


def _same_relation_row(a: re.Match, b: re.Match) -> bool:
    first, second = a.group(2), b.group(2)
    if first == second or first.replace("_", " ") != second.replace("_", " "):
        return False
    return a.group(3).lstrip() == b.group(3).lstrip()


def invoke(argv: list[str], capsys, norm: Normalizer) -> dict[str, Any]:
    capsys.readouterr()  # whatever building the world printed is not the command's
    try:
        outcome: dict[str, Any] = {"exit": main(argv)}
    except SystemExit as exc:
        capsys.readouterr()
        return {"argv": norm(argv), "exit": exc.code, "failed": exc.code != 0}
    except Exception as exc:  # noqa: BLE001 - what escapes the CLI is its behavior too
        outcome = {"raised": type(exc).__name__, "message": str(exc)}
    out = capsys.readouterr()
    outcome.update(stdout=relation_forms(PID.sub("pid <pid>", out.out)), stderr=out.err)
    return norm({"argv": argv, **outcome})
