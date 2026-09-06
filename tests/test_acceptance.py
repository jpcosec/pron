"""Acceptance tests: the canonical commands, surface to JSON.

Implements atom-canonical-commands-are-acceptance-tests-from-day-one.
Run from the repo root: PYTHONPATH=src pytest tests/ -x -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = {"PYTHONPATH": str(ROOT / "src")}


def run(*args: str) -> tuple[int, dict | str]:
    import os
    r = subprocess.run(
        [sys.executable, "-m", "knowledge", *args],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, **ENV},
    )
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, r.stdout


def test_sexpr_roundtrip():
    sys.path.insert(0, str(ROOT / "src"))
    from knowledge.core.sexpr import parse, serialize
    text = '(check (rel preferences (doc user "juanito")) :project summary)'
    assert serialize(parse(text)) == text


def test_next_atom_summary():
    code, out = run("next", "atom", "--summary")
    assert code == 0
    assert out["status"] == "ok"
    assert "id" in out["payload"]
    assert out["refs"], "refs must always be present"


def test_show_resolves_unique():
    code, out = run("show", "atom", "atom-searchvector", "--title")
    assert code == 0
    assert out["payload"] == {"title": "SearchVector"}


def test_ambiguity_is_dialogue():
    code, out = run("show", "atom", "atom-anchor")
    assert code == 2
    assert out["status"] == "ambiguous"
    assert len(out["candidates"]) > 1


def test_unanchored_symbol_fails_semantically():
    code, out = run("frobnicate", "atom")
    assert code == 1
    assert out["status"] == "semantic_error"
    assert "frobnicate" in out["symbol"]


def test_missing_offers_nearest():
    code, out = run("show", "atom", "atom-serchvector")
    assert code == 1
    assert out["status"] == "missing"
    assert any("searchvector" in n for n in out["nearest"])


def test_relation_traversal():
    code, out = run("atom", "atom-searchvector", "check", "tagged")
    assert code == 0
    tags = [p["tag"] for p in out["payload"]]
    assert "domain:knowledge_representation" in tags


def test_eval_equals_surface():
    code_s, out_s = run("show", "atom", "atom-searchvector", "--title")
    code_e, out_e = run("eval", '(check (doc atom "atom-searchvector") :project title)')
    assert out_s["payload"] == out_e["payload"]


def test_anchors_lists_living_grammar():
    code, out = run("anchors")
    assert code == 0
    symbols = {a["symbol"] for a in out["payload"]}
    assert {"check", "next", "atom", "summary"} <= symbols


def test_where_uses_sldb_filter_engine():
    code, out = run("list", "atom", "--where", 'title ~ "SearchVector"', "--title")
    assert code == 0
    assert out["payload"] == [{"title": "SearchVector"}]


def test_selector_by_semantic_tag():
    code, out = run("show", "atom", "practice:styling", "--title")
    assert code == 0
    assert "styling" in out["payload"]["title"].lower()


def test_selector_by_title_substring():
    code, out = run("show", "atom", "SearchVector", "--title")
    assert code == 0
    assert out["payload"] == {"title": "SearchVector"}


def test_where_contains_on_tags():
    code, out = run("list", "atom", "--where", '"impl:here" in tags')
    assert code == 0
    assert len(out["payload"]) > 10
