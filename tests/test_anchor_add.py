"""Tests for `knowledge anchor add`: declare grammar symbols as AnchorDocs."""

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


def _run(cwd: Path, *args: str) -> tuple[int, dict | str]:
    r = subprocess.run(
        [sys.executable, "-m", "knowledge", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, r.stdout


def _bootstrap(tmp: Path):
    """Fresh knowledge workspace: store init + AnchorDoc model + base anchors."""
    for cmd in (
        [sys.executable, "-m", "sldb", "stores", "init", "--path", str(tmp)],
        [
            sys.executable, "-m", "sldb", "models", "add",
            "sldb.models.knowledge_surface:AnchorDoc",
            "--store", str(tmp / ".sldb"), "--pythonpath", str(ROOT / "src"),
        ],
    ):
        r = subprocess.run(cmd, capture_output=True, text=True)
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
            capture_output=True, text=True, check=True,
        )


def test_anchor_add_creates_tracked_anchordoc():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(
            tmp, "anchor", "add", "rotate",
            "--kind", "operation", "--ref", "op:rotate", "--motive", "girar el estado",
        )
        assert code == 0, out
        doc = tmp / "knowledge" / "anchors" / "anchor-rotate.md"
        assert doc.exists()
        text = doc.read_text()
        assert "id: anchor-rotate" in text and "## Motive" in text
        assert "girar el estado" in text
        # listed in the living grammar with the right motive
        code, out = _run(tmp, "anchors", "rotate")
        assert code == 0 and out["payload"]["motive"] == "girar el estado"
        assert out["payload"]["ref"] == "op:rotate"


def test_anchor_add_rejects_bad_kind_and_ref():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(tmp, "anchor", "add", "x", "--kind", "nope",
                         "--ref", "op:x", "--motive", "y")
        assert code == 1
        assert "kind inválido" in str(out)
        code, out = _run(tmp, "anchor", "add", "x", "--kind", "operation",
                         "--ref", "doc:zzz", "--motive", "y")
        assert code == 1
        assert "ref inválido" in str(out)
        assert not (tmp / "knowledge" / "anchors" / "anchor-x.md").exists()


def test_anchor_add_rejects_duplicate_symbol():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        code, out = _run(tmp, "anchor", "add", "check", "--kind", "operation",
                         "--ref", "op:other", "--motive", "dup")
        assert code == 1
        assert "ya existe" in str(out)
