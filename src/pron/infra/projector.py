"""Projector: gives the evaluator a world. Implements atom-the-projector-gives-the-evaluator-a-world.

`model add` registers a StructuredNLDoc; `project` materializes the kgdb graph
via the verified pipeline (sldb semantic-export + kgdb ingest-sldb).
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from knowledge.bridges.kgdb_bridge import GRAPH_RELPATH


def model_add(
    root: Path, model_ref: str, pythonpath: str | None = None
) -> tuple[bool, str]:
    """Register a model in the local store through the sldb CLI surface."""
    cmd = [
        "python",
        "-m",
        "sldb",
        "models",
        "add",
        model_ref,
        "--store",
        str(root / ".sldb"),
        "--pythonpath",
        pythonpath or str(root),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or r.stderr).strip().splitlines()
    return r.returncode == 0, out[-1] if out else ""


def refresh(root: Path, pythonpath: str | None = None) -> tuple[bool, str]:
    """Single post-write hook: reindex sldb (semantic + sections) and rebuild graph.

    Every write operation (create, assert, ingest, anchor add) must call this
    so evaluators and kgdb never read stale indexes or a stale snapshot.
    """
    root = Path(root)
    r = subprocess.run(
        [
            "python",
            "-m",
            "sldb",
            "stores",
            "update",
            "--store",
            str(root / ".sldb"),
            "--pythonpath",
            pythonpath or str(root),
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        out = (r.stderr or r.stdout).strip().splitlines()
        return False, out[-1] if out else "sldb stores update falló"
    return project(root, pythonpath)


def project(root: Path, pythonpath: str | None = None) -> tuple[bool, str]:
    """Materialize the graph: semantic-export then ingest-sldb."""
    root = Path(root)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        export_path = tmp.name
    r1 = subprocess.run(
        [
            "python",
            "-m",
            "sldb",
            "stores",
            "semantic-export",
            "--store",
            str(root / ".sldb"),
            "--pythonpath",
            pythonpath or str(root),
            "--output",
            export_path,
        ],
        capture_output=True,
        text=True,
    )
    if r1.returncode != 0:
        return False, (r1.stderr or r1.stdout).strip().splitlines()[-1]
    graph_path = root / GRAPH_RELPATH
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    r2 = subprocess.run(
        ["kgdb", "ingest-sldb", "--input", export_path, "--output", str(graph_path)],
        capture_output=True,
        text=True,
    )
    out = (r2.stdout or r2.stderr).strip().splitlines()
    return r2.returncode == 0, out[-1] if out else ""
