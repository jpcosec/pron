FILE:desk/tasks/task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co.md
---
sldb:
  by: agent
  at: '2026-11-14T05:43:25Z'
  authority: generated
  via: create_document
id: task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references: []
depends_on: []
pills: []
files: []
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# pron vuelve a verde contra sldb main: la caché de aristas se lee de .sldb_cache y los goldens de la conversación se actualizan con su diff revisado

## Rationale

_Explain why this task exists or the business driver behind it._

El CI de pron está rojo desde el 06-11 (runs 42301383706 y 42305648222). pron sigue a sldb main y sldb movió la caché derivada de .sldb/runtime/ a .sldb_cache/ (migrate-layout); tests/plnr/test_goal_stale_graph.py todavía arma la ruta .sldb/runtime/edges/TheoremDoc/<doc>.yaml y da FileNotFoundError, y cuatro goldens de tests/golden (test_16_golden_conversation, test_16_golden_eval, test_16_golden_undo_why x2) ya no coinciden con su snapshot. Reproducido el 14-11 contra sldb b51e9667.

## Goal

_Describe the concrete result this task must produce._

Con sldb origin/main instalado, la suite de pron pasa entera de a un archivo (0 failed, 0 errors) y el job check del CI vuelve a verde; ningún test ni código de pron nombra .sldb/runtime/ como ruta de caché.

## Scope

_State what is in scope and what is out of scope._

En alcance: tests/plnr/test_goal_stale_graph.py y cualquier otro test o módulo de src/ que arme rutas de la caché de sldb a mano (pasar por la API de sldb que da la ruta de la caché o por .sldb_cache/), tests/mcp_surface/test_14_mount.py (su lista CACHE), los snapshots de tests/golden/__snapshots__ que cambien por el sldb nuevo, CHANGELOG. Fuera: cambiar sldb, cambiar el comportamiento de pron más allá de lo que exige el sldb nuevo, y la política de .gitignore de .sldb/ (decisión del dueño).

## Implementation Path

_Outline the expected implementation route or affected surface._

p1: instalar sldb origin/main y correr de a un archivo toda la suite de pron, guardar la lista de fallos como línea base en runs/subagents/. p2: reemplazar las rutas .sldb/runtime/ por la ruta que expone sldb (buscar con grep -rn 'runtime' src tests); si sldb no expone la ruta, usar .sldb_cache/ con un helper único en tests. p3: correr los goldens, mostrar el diff de cada snapshot en el informe y actualizar con --snapshot-update solo si el diff se explica por el sldb nuevo (orden, textos de sldb, rutas); si un diff muestra una respuesta de pron distinta en significado, parar y reportarlo sin actualizar. p4: suite completa de a un archivo en verde y CHANGELOG.

## Validation

_List the checks required before this task can close._

- TMPDIR=/tmp python -m pytest -q tests/plnr/test_goal_stale_graph.py
- TMPDIR=/tmp python -m pytest -q tests/golden
- grep -rn '.sldb/runtime' src tests (vacío)
- suite completa de pron de a un archivo

## Done When

_Name the observable condition that makes the task complete._

Suite de pron de a un archivo con 0 failed y 0 errors contra sldb origin/main; grep -rn '.sldb/runtime' src tests vacío; diffs de snapshots explicados en el informe.

FILE:desk/rituals/phase.md
---
id: ritual-phase
steps: []
tags:
- workspace:desk
---

# Phase ritual for dependency-layer execution

Run one horizontal layer of pron-repair tasks whose prerequisites are satisfied and whose
planned changes do not overlap, then close the layer with integration validation,
pill reconciliation, and next-phase preparation.

Each task in the phase still closes with its own validation and its own commit;
the phase adds the pass that only makes sense once those tasks are integrated.

FILE:desk/rituals/execution.md
---
id: ritual-execution
steps: []
tags:
- workspace:desk
---

# Execution ritual

Review the board, bind the relevant pills, keep scope tight, and implement only the active task for pron-repair.

FILE:desk/rituals/testing.md
---
id: ritual-testing
steps: []
tags:
- workspace:desk
---

# Testing ritual

Run the smallest relevant validation first, then broaden coverage when pron-repair changes shared behavior.

FILE:desk/rituals/closeout.md
---
id: ritual-closeout
steps: []
tags:
- workspace:desk
---

# Closeout ritual

Close a pron-repair task only after validation passes, any durable knowledge from bound pills is linked to an atom when needed, the board is updated, and the final change is ready to commit.

FILE:instruccion
Cold-bundle de la tarea task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- TMPDIR=/tmp python -m pytest -q tests/plnr/test_goal_stale_graph.py
- TMPDIR=/tmp python -m pytest -q tests/golden
- grep -rn '.sldb/runtime' src tests (vacío)
- suite completa de pron de a un archivo

