"""Invoke pron's CLI in-process and capture its behavior: exit code, stdout, stderr, or the
exception that escaped. Usage errors keep only that the command failed and its exit code: their
wording belongs to the argument parser, not to pron."""

from __future__ import annotations

import re
from typing import Any

from pron.cli.main import main
from golden.normalize import Normalizer

PID = re.compile(r"\bpid \d+")  # the process id of the test run


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
    outcome.update(stdout=PID.sub("pid <pid>", out.out), stderr=out.err)
    return norm({"argv": argv, **outcome})
