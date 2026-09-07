"""Tests for the unified post-write refresh: infra.refresh(root).

Implements task-auto-refresh-indexes-and-graph-after-writes: after any write
(create/assert/ingest/anchor add) the sldb semantic/section indexes and the
kgdb graph snapshot must be consistent without a manual command.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from test_write_ops import ENV, ROOT, _bootstrap, _run


def test_refresh_reindexes_and_rebuilds_graph(tmp_path=None):
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        graph_path = tmp / ".sldb" / "runtime" / "knowledge.nx.json"
        before = graph_path.read_text() if graph_path.exists() else ""

        code, out = _run(tmp, "eval", '(assert "sldb es la puerta de los docs")')
        assert code == 0, out
        assert out["status"] == "ok"

        # graph snapshot regenerated after the write
        assert graph_path.exists(), "graph snapshot must exist after a write"
        after = graph_path.read_text()
        assert after != before or before == "", "graph snapshot must be rebuilt"

        # semantic index sees the new doc without manual rebuild
        r = subprocess.run(
            [
                sys.executable, "-m", "sldb", "find",
                "puerta de los docs", "--in", "semantic",
                "--store", str(tmp / ".sldb"), "--pythonpath", str(tmp),
                "--format", "json",
            ],
            capture_output=True, text=True, env=ENV,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        hits = json.loads(r.stdout) if r.stdout.strip().startswith(("[", "{")) else r.stdout
        text = json.dumps(hits, ensure_ascii=False) if not isinstance(hits, str) else hits
        assert "puerta de los docs" in text, f"semantic index must find the new doc: {text[:400]}"

        # sections index sees the new doc without manual rebuild
        r = subprocess.run(
            [
                sys.executable, "-m", "sldb", "find",
                "puerta de los docs", "--in", "physical",
                "--store", str(tmp / ".sldb"), "--pythonpath", str(tmp),
                "--format", "json",
            ],
            capture_output=True, text=True, env=ENV,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        body = r.stdout
        assert "puerta" in body or "fact" in body, f"sections/physical index must see the doc: {body[:400]}"


def test_cli_project_runs_refresh():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _bootstrap(tmp)
        r = subprocess.run(
            [sys.executable, "-m", "pron", "project"],
            capture_output=True, text=True, cwd=tmp, env=ENV,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert (tmp / ".sldb" / "runtime" / "knowledge.nx.json").exists()
