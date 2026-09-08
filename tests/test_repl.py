"""Tests for `pron repl`: same evaluator as eval/surface, in-memory dialogue.

Implements atom-repl-shares-the-evaluator-and-answers-ambiguity-in-memory:
an ambiguous result opens a pending question, and the next line answers it
in place of the ambiguous selector, entirely within the process — no
.pron/session.json involved.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT  # this repo's own knowledge base
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _repl(script: str) -> str:
    r = subprocess.run(
        [sys.executable, "-m", "pron", "repl", "--kb", str(KB)],
        input=script,
        capture_output=True,
        text=True,
        env=ENV,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_surface_command_with_quoted_selector():
    """A quoted selector resolves the real document, not a literal-quotes string."""
    out = _repl('show atom "atom-searchvector"\n:quit\n')
    assert '"id": "atom-searchvector"' in out
    assert '"title": "SearchVector"' in out


def test_ambiguous_result_opens_a_pending_question_and_answering_resolves_it():
    """The exact SHRDLU-style flow: ask, then the next line answers in place."""
    out = _repl('list atom "runtime"\natom-knar-runtime\n:quit\n')
    assert "? Ambiguo" in out
    assert "atom-knar-runtime" in out.split("? Ambiguo")[1].split("pron>")[0]
    resolved = out.split("pron>")[2]  # banner, question, then the resolved answer
    assert '"id": "atom-knar-runtime"' in resolved


def test_internals_traces_the_grounding_of_each_symbol():
    out = _repl(":internals\nshow atom \"atom-searchvector\"\n:quit\n")
    assert "grounding:" in out
    assert "show -> operation op:check" in out
    assert "atom -> model model:AtomDoc" in out


def test_help_lists_the_live_grammar():
    out = _repl(":help\n:quit\n")
    assert "gramática viva (anchors):" in out
    assert "executable" not in out  # sanity: not echoing unrelated content
    assert "check" in out and "operation" in out


def test_direct_meaning_expression_is_evaluated_like_eval():
    out = _repl('(check (doc atom "atom-searchvector") :project title)\n:quit\n')
    assert '"title": "SearchVector"' in out
