# DISPATCH: deskops-executor
Eres el Executor. Tu rol (non-negotiables y boundaries) está abajo. Trabaja en /home/jp/proyectos/legos/knowledge.

## Zero-context bundle
### TaskDoc
---
id: task-auto-refresh-indexes-and-graph-after-writes
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-auto-refresh-indexes-and-graph-after-writes
current_node: checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
history: []
references: []
depends_on:
- task-implement-knowledge-anchor-add
pills: []
files: []
checklists:
- checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
- checklist-task-auto-refresh-indexes-and-graph-after-writes-testing-ready
- checklist-task-auto-refresh-indexes-and-graph-after-writes-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-a-zero-edge-graph-snapshot-should-be-treated-as-an-incomplete-provenance-build-rather-than-a-healthy-graph
---

# Auto-refresh indexes and graph after writes

## Rationale

_Explain why this task exists or the business driver behind it._

Tras cualquier escritura, el evaluator y kgdb leerian un grafo/indices viejos si no se reconstruyen; atom-a-zero-edge-graph-snapshot exige provenance de build, no grafos podridos.

## Goal

_Describe the concrete result this task must produce._

Centralizar el post-write hook: despues de anchor add, create, assert, ingest, regenerar los indices sldb (semantic/section) y el snapshot kgdb (.sldb/runtime/graphs/deskops.kg.json) en una sola llamada reutilizable (p.ej. infra.refresh(root)) usada por cli/main.py y ops/write.py; evitando duplicar la logica de rebuild.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/infra/ (nuevo refresh o extension de projector.py), src/knowledge/cli/main.py, src/knowledge/ops/

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Extraer la logica de rebuild que ya exista (project en infra/projector.py, snapshot en deskops graph build). 2. infra.refresh(root): reindex sldb + kgdb build, retornando estado. 3. Llamarla tras cada operacion de escritura. 4. Test: escribir y verificar que el snapshot cambia y los indices encuentran el doc nuevo.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q

## Done When

_Name the observable condition that makes the task complete._

Toda operacion de escritura deja indices y grafo consistentes sin comando manual; pytest verde
### Routine
---
# routine-xxx
id: routine-task-auto-refresh-indexes-and-graph-after-writes
# active | archived
status: active
# Initial node identifier
entrypoint: checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
# Ordered or grouped primitive identifiers
decomposition:
- checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-activate
- checklist-task-auto-refresh-indexes-and-graph-after-writes-testing-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-ready-for-testing
- checklist-task-auto-refresh-indexes-and-graph-after-writes-closeout-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-close
# Edge identifiers composing the graph
edges:
- edge-task-auto-refresh-indexes-and-graph-after-writes-execution-to-activate
- edge-task-auto-refresh-indexes-and-graph-after-writes-activate-to-testing
- edge-task-auto-refresh-indexes-and-graph-after-writes-testing-to-ready
- edge-task-auto-refresh-indexes-and-graph-after-writes-ready-to-closeout
- edge-task-auto-refresh-indexes-and-graph-after-writes-closeout-to-close
- edge-task-auto-refresh-indexes-and-graph-after-writes-close-to-complete
# Terminal node identifiers
terminal_nodes:
- complete
# e.g., system:deskops
tags:
- workspace:desk
- primitive:routine
---

# Routine for Auto-refresh indexes and graph after writes

## Summary

_Summarize what this routine does and how its nodes fit together._

Actionable routine for Auto-refresh indexes and graph after writes.
### Atom: atom-a-zero-edge-graph-snapshot-should-be-treated-as-an-incomplete-provenance-build-rather-than-a-healthy-graph
---
id: atom-a-zero-edge-graph-snapshot-should-be-treated-as-an-incomplete-provenance-build-rather-than-a-healthy-graph
title: A zero-edge graph snapshot should be treated as an incomplete provenance build
  rather than a healthy graph
five_wh_one_plus: what
tags:
- system:knowledge
- system:kgdb
- topic:knowledge_graph
- topic:provenance_retrieval
- graph:provenance
- graph:lineage
- domain:provenance
- kind:software
- impl:external
provenance: Derived from `.sldb/runtime/knowledge_graph.kg.json` and `source/spec/GRAPH_ARCHITECTURE.md`.
---

# A zero-edge graph snapshot should be treated as an incomplete provenance build rather than a healthy graph

## Answer

A graph snapshot with nodes but no edges should be treated as an incomplete provenance build, because the KB architecture expects recoverable support, derivation, and composition relations, not just labeled entities. Node-only materialization is still useful for inventory, but it does not yet satisfy the graph’s intended knowledge-layer role.
### Atom: atom-anchors-py-loads-the-grammar-from-tracked-anchordocs
---
id: atom-anchors-py-loads-the-grammar-from-tracked-anchordocs
title: "anchors.py loads the grammar from tracked AnchorDocs"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
provenance: src/knowledge/core/anchors.py
---

# anchors.py loads the grammar from tracked AnchorDocs

## Answer

src/knowledge/core/anchors.py implements AnchorRegistry: it loads every tracked AnchorDoc from the store via the sldb bridge, exposes lookup (symbol -> Anchor or SemanticError with declaration hint), all() for the living grammar, and by_kind(). It never invents anchors.
### Estado previo relevante
anchor add (src/knowledge/ops/anchor_add.py) y write ops (src/knowledge/ops/write.py) YA disparan rebuild inline tras cada write. Esta tarea extrae esa lógica a infra.refresh(root) única y reutilizable, eliminando la duplicación. Lee ambos módulos primero. bridges/write_models.py y bridges/sldb_bridge.py son las únicas puertas a sldb.
### ROLE DEFINITION (deskops-executor)
# Workflow Executor

Use this skill when your role is **executor**.

## Non-negotiables

- Implement one bounded task only.
- Recover state from `Board` before changing files.
- Keep evidence on disk under `runs/subagents/` when doing non-trivial work.
- Run the smallest relevant validation first.
- Do not self-retire the task.

## Model binding

- Primary: `openai-codex/gpt-5.4` (plan).
- Fallback: `google-gemini-cli/gemini-3.1-pro-preview` (plan). The supervisor may also override per dispatch with an explicit `model=`.

## Hard boundaries

- This is the only role allowed to write implementation code for the task, including tests.
- Writes are limited to task scope. Do not touch board routing or other tasks.
- Annotations for supervisor review go on the evidence surface: `runs/subagents/<run-dir>/result-summary.md` plus snapshot files. Do not hand off in chat only.

## Recovery

```bash
deskops show board Board --root .
deskops show task <task-id> --root .
deskops next <task-id> --root .
deskops graph missing --root .
git status --short --branch
```

## Executor duties

- read the assigned task
- read bound references, pills, and files
- confirm exact touched surfaces
- snapshot desk and git state into run evidence
- implement only task scope
- run focused validation first
- write a result summary for handoff

## Evidence snapshot pattern

```bash
TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/subagents/$TS-<task-id>"
mkdir -p "$RUN_DIR"

deskops show board Board --root . > "$RUN_DIR/board.txt"
deskops show task <task-id> --root . > "$RUN_DIR/task.txt"
deskops next <task-id> --root . > "$RUN_DIR/next.txt"
deskops graph missing --root . > "$RUN_DIR/graph.txt"
git status --short --branch > "$RUN_DIR/git-status.txt"
```

## Validation discipline

Prefer the smallest meaningful proof first.

Examples:

```bash
pytest tests/<targeted-scope> -q
pytest
sldb stores check --store .sldb
```

If the change touches tracked structured docs or models, also use `.opencode/skills/use-sldb/SKILL.md`.

## Required outputs

- `board.txt`
- `task.txt`
- `next.txt`
- `graph.txt`
- `git-status.txt`
- `result-summary.md` with `run_id`, child `session` path, and `session_sha256`
- `validation.log` when applicable

Closeout commits are made only via `deskops closeout commit --task <id> --run-dir <dir>`; never handcraft them with plain `git commit`.

## Anti-patterns

Do not:

- expand into other tasks
- change board routing casually
- claim closeout is done
- skip validation evidence
- rewrite unrelated files because they are already dirty
