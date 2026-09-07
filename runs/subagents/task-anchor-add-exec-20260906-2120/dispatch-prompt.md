# DISPATCH: deskops-executor
Eres el Executor. Tu rol (non-negotiables y boundaries) está abajo. Trabaja en /home/jp/proyectos/legos/knowledge.

## Zero-context bundle
### TaskDoc
---
id: task-implement-knowledge-anchor-add
status: ready_for_testing
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-implement-knowledge-anchor-add
current_node: checklist-task-implement-knowledge-anchor-add-closeout-ready
history:
- operator-task-implement-knowledge-anchor-add-activate
- operator-task-implement-knowledge-anchor-add-ready-for-testing
references: []
depends_on: []
pills: []
files: []
checklists:
- checklist-task-implement-knowledge-anchor-add-execution-ready
- checklist-task-implement-knowledge-anchor-add-testing-ready
- checklist-task-implement-knowledge-anchor-add-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-an-anchor-binds-a-symbol-to-a-semantic-motive-and-a-resolvable-referent
- atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind
- atom-anchor-kinds-partition-what-a-symbol-can-refer-to
- atom-the-anchor-table-is-declared-as-sldb-documents-not-code
- atom-anchors-py-loads-the-grammar-from-tracked-anchordocs
closeout_evidence_verified: false
pill_graduation_verified: true
---

# Implement knowledge anchor add

## Rationale

_Explain why this task exists or the business driver behind it._

El CLI sugiere 'knowledge anchor add' en cada error semántico pero el comando no existe; sin escritura el conocimiento no crece desde el evaluator.

## Goal

_Describe the concrete result this task must produce._

Implementar 'knowledge anchor add <symbol> --kind <model|doc|relation|operation|projection> --ref <typed-ref> --motive <text>' que crea un AnchorDoc sldb en knowledge/anchors/ con frontmatter id/symbol/kind/ref/tags/provenance y seccion ## Motive; validar ref por regex segun kind (model:<Name>, doc:<name>, edge:<rel>[:dir], op:<fn>, fields:<f1,f2>, view:<name>); rechazar kinds fuera de la particion; disparar reindex sldb + graph rebuild (project) tras escribir; anadir anchor para el nuevo verbo (anchor-add.md) para que el surface grammar lo reconozca.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/cli/main.py, src/knowledge/core/anchors.py, src/knowledge/anchors/, tests/; NO modificar el evaluador ni los bridges

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Leer knowledge/anchors/anchor-check.md como formato canónico y knowledge/core/anchors.py (AnchorRegistry, _load) para el contrato de lectura. 2. Añadir subcomando 'anchor add' en cli/main.py (junto a 'anchors'). 3. Validación regex del ref por kind (atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind). 4. Escribir el AnchorDoc vía escritura de doc sldb respetando frontmatter (id: anchor-<symbol>, symbol, kind, ref, tags: [system:knowledge, entity:anchor, domain:knowledge_representation, kind:software, impl:here], provenance). 5. Tras escribir, regenerar índices y snapshot kgdb. 6. Declarar anchor-add.md para el verbo add.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q
- python -m knowledge anchors | grep -c symbol

## Done When

_Name the observable condition that makes the task complete._

knowledge anchor add <sym> --kind op --ref 'op:f' --motive 'x' crea el AnchorDoc, 'knowledge anchors <sym>' lo lista con motive correcto, y 'knowledge eval' resuelve el símbolo nuevo sin semantic error; kinds/refs inválidos fallan con error explícito; pytest 44+ verde
### Routine
---
# routine-xxx
id: routine-task-implement-knowledge-anchor-add
# active | archived
status: active
# Initial node identifier
entrypoint: checklist-task-implement-knowledge-anchor-add-execution-ready
# Ordered or grouped primitive identifiers
decomposition:
- checklist-task-implement-knowledge-anchor-add-execution-ready
- operator-task-implement-knowledge-anchor-add-activate
- checklist-task-implement-knowledge-anchor-add-testing-ready
- operator-task-implement-knowledge-anchor-add-ready-for-testing
- checklist-task-implement-knowledge-anchor-add-closeout-ready
- operator-task-implement-knowledge-anchor-add-close
# Edge identifiers composing the graph
edges:
- edge-task-implement-knowledge-anchor-add-execution-to-activate
- edge-task-implement-knowledge-anchor-add-activate-to-testing
- edge-task-implement-knowledge-anchor-add-testing-to-ready
- edge-task-implement-knowledge-anchor-add-ready-to-closeout
- edge-task-implement-knowledge-anchor-add-closeout-to-close
- edge-task-implement-knowledge-anchor-add-close-to-complete
# Terminal node identifiers
terminal_nodes:
- complete
# e.g., system:deskops
tags:
- workspace:desk
- primitive:routine
---

# Routine for Implement knowledge anchor add

## Summary

_Summarize what this routine does and how its nodes fit together._

Actionable routine for Implement knowledge anchor add.
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
### Atom: atom-anchor-kinds-partition-what-a-symbol-can-refer-to
---
id: atom-anchor-kinds-partition-what-a-symbol-can-refer-to
title: Anchor kinds partition what a symbol can refer to
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

# Anchor kinds partition what a symbol can refer to

## Answer

Anchor kinds are: model (a registered StructuredNLDoc such as UserDoc or TaskDoc), doc (a concrete tracked document), relation (a kgdb edge type such as declares_preference), operation (a runtime verb such as check, next, assert, ingest, create, return), and projection (a payload view such as summary). The evaluator dispatches on kind, so the set of kinds is the closed contract of the core.
### Atom: atom-the-anchor-table-is-declared-as-sldb-documents-not-code
---
id: atom-the-anchor-table-is-declared-as-sldb-documents-not-code
title: The anchor table is declared as SLDB documents, not code
five_wh_one_plus: why
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- entity:anchor
- cross:knowledge_sldb
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The anchor table is declared as SLDB documents, not code

## Answer

Anchors live as tracked SLDB documents (AnchorDoc), not as code, so each app declares its own grammar by registering anchors. knowledge adapts to each use case without code changes, the grammar is queryable and versioned with provenance, and the app becomes self-aware of its own command language: --help and the living grammar derive from the same documents.
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
