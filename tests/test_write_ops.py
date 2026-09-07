"""Tests for canonical write ops: create, assert, ingest, with provenance.

Implements atom-write-operations-record-provenance-of-the-command-that-produced-them:
roundtrip assert -> return recovers the fact, and the produced doc records the
full evaluated command as provenance.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The knowledge base (atoms, anchors, .sldb) lives in its own repo, `pron`:
# $KNOWLEDGE_KB or the sibling directory ../pron.
KB = Path(os.environ.get("KNOWLEDGE_KB", str(ROOT.parent / "pron")))
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _run(cwd: Path, *args: str) -> tuple[int, dict | str]:
    r = subprocess.run(
        [sys.executable, "-m", "knowledge", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=ENV,
    )
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, r.stdout


def _bootstrap(tmp: Path):
    """Fresh knowledge workspace: store init + models + grammar anchors."""
    for cmd in (
        [sys.executable, "-m", "sldb", "stores", "init", "--path", str(tmp)],
        [
            sys.executable, "-m", "sldb", "models", "add",
            "sldb.models.knowledge_surface:AnchorDoc",
            "--store", str(tmp / ".sldb"), "--pythonpath", str(ROOT / "src"),
        ],
        [
            sys.executable, "-m", "sldb", "models", "add",
            "knowledge.bridges.write_models:FactDoc",
            "--store", str(tmp / ".sldb"), "--pythonpath", str(ROOT / "src"),
        ],
        [
            sys.executable, "-m", "sldb", "models", "add",
            "knowledge.bridges.write_models:PropositionDoc",
            "--store", str(tmp / ".sldb"), "--pythonpath", str(ROOT / "src"),
        ],
    ):
        r = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
        assert r.returncode == 0, r.stdout + r.stderr
    anchors_src = KB / "knowledge" / "anchors"
    anchors_dst = tmp / "knowledge" / "anchors"
    anchors_dst.mkdir(parents=True)
    for f in anchors_src.glob("*.md"):
        shutil.copy(f, anchors_dst / f.name)
    for f in sorted(anchors_dst.glob("*.md")):
        subprocess.run(
            [sys.executable, "-m", "sldb", "docs", "track", str(f),
             "--model", "AnchorDoc", "--store", str(tmp / ".sldb"),
             "--pythonpath", str(ROOT / "src"), "--force"],
            capture_output=True, text=True, check=True, env=ENV,
        )


def test_assert_roundtrip_records_provenance():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(tmp, "eval", '(assert "sldb es la puerta de los docs")')
        assert code == 0, out
        assert out["status"] == "ok"
        assert out["payload"]["model"] == "FactDoc"
        assert "(assert" in out["payload"]["provenance"]

        # return recovers the fact
        code, out = _run(tmp, "eval", '(return (docs fact))')
        assert code == 0, out
        facts = out["payload"]
        assert len(facts) == 1
        assert facts[0]["fact"] == "sldb es la puerta de los docs"
        assert facts[0]["provenance"] == '(assert "sldb es la puerta de los docs")'
        assert out["refs"], "refs must always be present"

        # the produced doc records the command in its frontmatter
        doc = Path(out["refs"][0])
        if not doc.is_absolute():
            doc = tmp / doc
        assert doc.exists()
        front = doc.read_text().split("---")[1]
        assert 'provenance: (assert "sldb es la puerta de los docs")' in front
        assert "provenance_at:" in front


def test_ingest_registers_proposition():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(tmp, "eval", '(ingest "Tesis" "el núcleo es un evaluador anclado")')
        assert code == 0, out
        assert out["payload"]["model"] == "PropositionDoc"

        code, out = _run(tmp, "eval", '(return (docs proposition))')
        assert code == 0, out
        props = out["payload"]
        assert len(props) == 1
        assert props[0]["title"] == "Tesis"
        assert props[0]["proposition"] == "el núcleo es un evaluador anclado"
        assert '(ingest "Tesis"' in props[0]["provenance"]
        ref = Path(out["refs"][0])
        assert "provenance_at:" in (ref if ref.is_absolute() else tmp / ref).read_text()


def test_create_defines_doc_entity():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(
            tmp, "eval",
            '(create anchor "anchor-zzz" id anchor-zzz symbol zzz kind operation ref op:zzz motive "motivo de prueba")',
        )
        assert code == 0, out
        assert out["payload"]["model"] == "AnchorDoc"
        doc = tmp / "knowledge" / "anchors" / "anchor-zzz.md"
        assert doc.exists()

        code, out = _run(tmp, "eval", "(return (docs anchor))")
        assert code == 0, out
        symbols = [d["symbol"] for d in out["payload"]]
        assert "zzz" in symbols


def test_write_errors_are_explicit():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(tmp, "eval", "(assert)")
        assert code == 1
        assert out["status"] == "error"

        code, out = _run(tmp, "eval", '(create "no-symbol" "name")')
        assert code == 1
        assert out["status"] == "error"

        code, out = _run(tmp, "eval", '(ingest "solo título")')
        assert code == 1
        assert out["status"] == "error"
