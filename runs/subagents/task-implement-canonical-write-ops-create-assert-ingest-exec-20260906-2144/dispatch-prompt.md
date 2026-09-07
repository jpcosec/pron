# DISPATCH: deskops-executor
Eres el Executor. Tu rol (non-negotiables y boundaries) está abajo. Trabaja en /home/jp/proyectos/legos/knowledge.

## Zero-context bundle
### TaskDoc
---
id: task-implement-canonical-write-ops-create-assert-ingest
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-implement-canonical-write-ops-create-assert-ingest
current_node: checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
history: []
references: []
depends_on:
- task-implement-knowledge-anchor-add
pills: []
files: []
checklists:
- checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
- checklist-task-implement-canonical-write-ops-create-assert-ingest-testing-ready
- checklist-task-implement-canonical-write-ops-create-assert-ingest-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-write-operations-record-provenance-of-the-command-that-produced-them
- atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator
---

# Implement canonical write ops (create, assert, ingest)

## Rationale

_Explain why this task exists or the business driver behind it._

El spec KNOWLEDGE_CORE_SEMANTIC_ANCHORING define assert/create/ingest/return; solo check/next/return existen. Sin escritura el CLI es un lector de solo-lectura.

## Goal

_Describe the concrete result this task must produce._

Implementar las operaciones de escritura canónicas como anchors kind=operation con implementación en ops/write.py: (create ...) define entidades (symbol/relation/modelo/doc), (assert ...) añade un hecho como verdadero, (ingest ...) registra una proposicion/documento. Toda escritura debe ir vía sldb document/field operations y registrar provenance: el s-expr evaluado completo que produjo el cambio (atom-write-operations-record-provenance-of-the-command-that-produced-them, hoy impl:pending -> voltear a impl:here). Declarar los AnchorDocs anchor-create.md, anchor-assert.md, anchor-ingest.md.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/ops/ (nuevo write.py), src/knowledge/core/evaluator.py (despacho de los verbos), knowledge/anchors/, knowledge/atoms/ (voltear impl del atom de provenance), tests/

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Leer ops/read.py como patrón de operación (firma check(evaluator, args, projection)). 2. ops/write.py con create/assert/ingest escribiendo vía sldb bridge (ver bridges/sldb_bridge.py). 3. provenance: guardar en el frontmatter del doc producido el s-expr serializado (serialize del sexpr parser) + timestamp. 4. Despachar los verbos en evaluator.py según anchor kind=operation ref op:<fn>. 5. Tras cada write disparar rebuild de índices + graph. 6. Test con store temporal (--kb) verificando roundtrip: assert -> return recupera el hecho; provenance contiene el comando.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q

## Done When

_Name the observable condition that makes the task complete._

assert/create/ingest evaluables via 'knowledge eval' crean docs en el store con provenance del comando; 'return' los recupera; atom-write-operations-record-provenance pasa a impl:here; pytest verde
### Routine
---
# routine-xxx
id: routine-task-implement-canonical-write-ops-create-assert-ingest
# active | archived
status: active
# Initial node identifier
entrypoint: checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
# Ordered or grouped primitive identifiers
decomposition:
- checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
- operator-task-implement-canonical-write-ops-create-assert-ingest-activate
- checklist-task-implement-canonical-write-ops-create-assert-ingest-testing-ready
- operator-task-implement-canonical-write-ops-create-assert-ingest-ready-for-testing
- checklist-task-implement-canonical-write-ops-create-assert-ingest-closeout-ready
- operator-task-implement-canonical-write-ops-create-assert-ingest-close
# Edge identifiers composing the graph
edges:
- edge-task-implement-canonical-write-ops-create-assert-ingest-execution-to-activate
- edge-task-implement-canonical-write-ops-create-assert-ingest-activate-to-testing
- edge-task-implement-canonical-write-ops-create-assert-ingest-testing-to-ready
- edge-task-implement-canonical-write-ops-create-assert-ingest-ready-to-closeout
- edge-task-implement-canonical-write-ops-create-assert-ingest-closeout-to-close
- edge-task-implement-canonical-write-ops-create-assert-ingest-close-to-complete
# Terminal node identifiers
terminal_nodes:
- complete
# e.g., system:deskops
tags:
- workspace:desk
- primitive:routine
---

# Routine for Implement canonical write ops (create, assert, ingest)

## Summary

_Summarize what this routine does and how its nodes fit together._

Actionable routine for Implement canonical write ops (create, assert, ingest).
### Atom: atom-write-operations-record-provenance-of-the-command-that-produced-them
---
id: atom-write-operations-record-provenance-of-the-command-that-produced-them
title: Write operations record provenance of the command that produced them
five_wh_one_plus: how
tags:
- system:knowledge
- domain:provenance
- kind:concept
- impl:pending
- topic:semantic_anchoring
- graph:lineage
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# Write operations record provenance of the command that produced them

## Answer

Every write operation (assert, create, ingest) goes through sldb document and field operations and records the evaluated command as provenance. This is SHRDLU's action memory made auditable: any stored fact can be traced back to the exact expression, anchors, and referents that produced it.
### Atom: atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator
---
id: atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator
title: The knowledge core is a semantically anchored s-expression evaluator
five_wh_one_plus: what
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The knowledge core is a semantically anchored s-expression evaluator

## Answer

The core of knowledge is an evaluator of s-expressions in which every symbol is anchored to a semantic motive resolvable against the infrastructure (sldb + kgdb + runtime state). A command is not a string parsed into flags: it is an expression whose meaning is resolved against the world before it executes. Everything else in the knowledge system is ordered after this core.
### Atom: atom-an-anchor-binds-a-symbol-to-a-semantic-motive-and-a-resolvable-referent
---
id: atom-an-anchor-binds-a-symbol-to-a-semantic-motive-and-a-resolvable-referent
title: An anchor binds a symbol to a semantic motive and a resolvable referent
five_wh_one_plus: what
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# An anchor binds a symbol to a semantic motive and a resolvable referent

## Answer

An anchor links a grammar symbol to three things: a kind (model, doc, relation, operation, or projection), a ref (the concrete referent in the infrastructure), and a motive (the natural-language meaning of the symbol for a human). The motive is what keeps the grammar legible and auditable; the kind and ref are what make the symbol executable.
### Atom: atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind
---
id: atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind
title: "Anchor ref is a typed string with a scheme per kind"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`, section 'Decisiones cerradas'.
---

# Anchor ref is a typed string with a scheme per kind

## Answer

AnchorDoc.ref is a single string with a kind-specific scheme validated by regex: model:<Name>, doc:<name>, edge:<relation_type>[:direction], op:<function>, and fields:<f1,f2> or view:<name> for projections. A typed string instead of a dict keeps frontmatter legible and validation simple; complex resolution lives in the evaluator, not in the anchor.
### Pills
---
id: contexts-pills
tags:
- workspace:desk
---

# Pills

Pills are reusable context documents for the Upla desk routine.

## Notes

- Keep active task-to-pill binding in task docs.
- Add temporary context here only when it affects execution safety or scope.
### Estado previo relevante
anchor add ya existe: src/knowledge/ops/anchor_add.py (patrón de escritura vía sldb + validación). Léelo como referencia. ops/read.py tiene el patrón de firma de operaciones (check/next_/return_). El evaluator despacha verbos kind=operation ref op:<fn>.
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
