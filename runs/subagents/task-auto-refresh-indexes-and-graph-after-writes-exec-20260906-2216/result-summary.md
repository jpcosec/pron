# Result summary — task-auto-refresh-indexes-and-graph-after-writes

- run_id: task-auto-refresh-indexes-and-graph-after-writes-exec-20260906-2216
- session: no child subagent spawned; evidence in this run dir
- session_sha256 (validation.log): 31e00bd4258bfecc2e6bc9f505aa45cb0f360b18addbba16219e1b944a251e3f

## What was implemented

Centralized the post-write hook as `infra.refresh(root)` (src/knowledge/infra/projector.py):
1. `sldb stores update` — rebuilds semantic + sections indexes (and store hashes).
2. `project(root)` — semantic-export + kgdb ingest-sldb to regenerate `.sldb/runtime/knowledge.nx.json`.

Callers routed through refresh (no duplicated rebuild logic):
- src/knowledge/ops/write.py `_write_doc` (create / assert / ingest)
- src/knowledge/ops/anchor_add.py (anchor add)
- src/knowledge/cli/main.py (`knowledge project` now runs the full refresh)

## Test added

- tests/test_refresh.py: after `(assert ...)`, the graph snapshot is rebuilt, the semantic
  index finds the new doc without `--rebuild`, the physical/section index sees it, and
  `knowledge project` performs the full refresh.

## Validation

- `PYTHONPATH=src python -m pytest tests -q` → **53 passed** (was 51 before; +2 new).
- `sldb stores check --store .sldb` → FAIL, but **pre-existing**: verified identical FAIL
  on a clean `git stash` checkout, unrelated to this change.

## Notes for supervisor

- Atom a (zero-edge snapshot = incomplete provenance) is honored by keeping graph
  materialization via the verified sldb-export + kgdb pipeline; refresh does not
  fabricate edges. Deeper provenance enforcement of the atom is out of task scope.
- `knowledge project` semantics widened from graph-only to full refresh; its help text
  still says "materializa el grafo kgdb" (minor copy drift, flagged here).
- No closeout commit performed, per dispatch instruction.
