FILE:desk/tasks/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c.md
---
sldb:
  by: agent
  at: '2026-11-16T03:37:05Z'
  authority: generated
  via: save_document_payload
id: task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references:
- desk/inbox/20261104-233659-unclear-sldb-pron-ignora-sldb-entero-stores-check-falla-con-stores-core-ignored.md
- .gitignore
- Makefile
depends_on: []
pills: []
files:
- docs/decision-store-sldb.md
- .gitignore
- Makefile
task_type: task.decision
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# Decisión de JP: pron versiona .sldb/ (store.yaml + core/) o queda como excepción al layout de sldb c420809c

## Rationale

_Explain why this task exists or the business driver behind it._

sldb c420809c (2026-11-04) aplica la decisión del dueño del 2026-10-29: el store .sldb/ (store.yaml + core/) se versiona y .sldb_cache/ es la caché ignorada. pron ignora .sldb/ entero (.gitignore línea 10, bajo el comentario "pron's own world: make world rebuilds the store"), porque ahí `make world` (Makefile líneas 29-32) regenera el mundo de pron: hoy unos 740 documentos derivados en .sldb/core/documents (RelationDoc 359, SurfaceDoc 278, RelationTypeDoc, SpecDoc, ExplanationDoc, CliCommandDoc, MoveDoc, AnchorDoc, ReadmeDoc). Consecuencias medidas el 2026-11-16 en robocop2: `sldb stores check` sale con error stores/core_ignored; `deskops doctor --root .` declara el desk roto; los documentos del desk (TaskCodeDoc, InboxNoteDoc y los ReviewDoc de los recibos preflight/bundle/owner) se escriben en .sldb/core y git los ignora, así que no viajan en un clon y una tarea de pron no puede activarse en otra máquina. Origen: nota del inbox desk/inbox/20261104-233659-unclear-sldb-pron-ignora-sldb-entero-stores-check-falla-con-stores-core-ignored.md.

## Goal

_Describe the concrete result this task must produce._

JP elige una de tres opciones y la elección queda escrita y commiteada en pron: (A) versionar .sldb/ como el resto de los repos: quitar la línea `.sldb/` de .gitignore y commitear store.yaml y core/, mundo derivado incluido; (B) separar stores: el mundo derivado de pron sale de .sldb/ a otro store ignorado y .sldb/ queda versionado solo con el desk (exige cambiar `pron init --world` y el Makefile); (C) pron queda como excepción declarada: .sldb/ sigue ignorado, stores check sigue en error y los recibos del desk no se versionan. Recomendación del coordinador: A, porque cumple la decisión del 2026-10-29 sin tocar código de pron y hace versionables los recibos; su costo es versionar unos 740 documentos regenerables y sus diffs al correr make world.

## Scope

_State what is in scope and what is out of scope._

Entra: registrar la elección de JP (recibo owner), escribir docs/decision-store-sldb.md con la opción elegida, su razón y sus consecuencias, y commitearlo. Si la elección exige cambios (A o B), esta tarea solo crea la tarea task.code que los implementa (con .gitignore, Makefile y los archivos de src/pron que correspondan) y la referencia aquí; no los implementa. No entra: cambiar sldb ni su política, editar .gitignore o el código de pron, ni correr `sldb stores migrate-layout`.

## Implementation Path

_Outline the expected implementation route or affected surface._

p1: JP lee las opciones A/B/C del goal y dispone el recibo owner ya registrado con deskops review dispose 'review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-owner-1' --verdict accepted --reason 'Opción <A|B|C>: <razón>' --root . (desde /mnt/ssd/proyectos/SLDB_1/pron). p2: escribir docs/decision-store-sldb.md con la línea 'Opción elegida: A|B|C', fecha, razón y consecuencias para stores check y para los recibos del desk. p3: si es A o B, deskops add task --root . --task-type task.code con la implementación, que referencie docs/decision-store-sldb.md. p4: commit de docs/decision-store-sldb.md y del desk con [skip ci] y push a origin master.

## Validation

_List the checks required before this task can close._

- test -f docs/decision-store-sldb.md && grep -nE 'Opción elegida: (A|B|C)' docs/decision-store-sldb.md
- deskops review status task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c --root .   # recibo owner accepted e intact
- git log -1 --format=%H -- docs/decision-store-sldb.md   # commit alcanzable desde HEAD

## Done When

_Name the observable condition that makes the task complete._

Recibo owner aceptado por JP; docs/decision-store-sldb.md commiteado y pusheado en master de pron con la opción elegida; si la opción es A o B, existe en desk/tasks una task.code que la implementa y referencia el documento.

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

FILE:.gitignore
# derived: rebuilt by tools, never versioned
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.pron/
# pron's own world: `make world` rebuilds the store and everything generated into it
.sldb/
sldb/
knowledge/commands/
knowledge/relations/
knowledge/surfaces/
docs/spec2viz/out/
docs/spec2viz/index.html
docs/spec2viz/offline.html
docs/spec2viz/diagrams.md
# local Claude Code agent worktrees
.claude/worktrees/
# from the plnr engine's own .gitignore
*.py[cod]
build/
dist/
.venv/
.sldb_cache/

FILE:Makefile
PYTHON ?= python

.PHONY: check lint format-check format typecheck test world docs-check

check:
	$(MAKE) lint format-check typecheck
	$(MAKE) test
	$(MAKE) docs-check

# includes standards.md Layer 1 for src/ and tests/: ≤10 statements per function, ≤100 code lines per file
lint:
	$(PYTHON) -m ruff check src tests examples tools/check_plnr_file_length.py
	$(PYTHON) tools/check_file_length.py src/pron tests
	$(PYTHON) tools/check_plnr_file_length.py

format-check:
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -q -p syrupy

# pron's own world is derived: rebuild the store and the generated docs from the repo
world:
	test -f .sldb/core/store_index.yaml || sldb stores init
	$(PYTHON) -m pron.cli.main init --world . --pythonpath . --knowledge > /dev/null
	$(PYTHON) -m pron.cli.main docs --world . --pythonpath .

docs-check: world
	git diff --exit-code -- README.md
	$(PYTHON) -m pron.cli.main docs --world . --pythonpath . --check
	$(PYTHON) -m pron.cli.main check --world . --pythonpath .

FILE:instruccion
Cold-bundle de la tarea task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- test -f docs/decision-store-sldb.md && grep -nE 'Opción elegida: (A|B|C)' docs/decision-store-sldb.md
- deskops review status task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c --root .   # recibo owner accepted e intact
- git log -1 --format=%H -- docs/decision-store-sldb.md   # commit alcanzable desde HEAD

