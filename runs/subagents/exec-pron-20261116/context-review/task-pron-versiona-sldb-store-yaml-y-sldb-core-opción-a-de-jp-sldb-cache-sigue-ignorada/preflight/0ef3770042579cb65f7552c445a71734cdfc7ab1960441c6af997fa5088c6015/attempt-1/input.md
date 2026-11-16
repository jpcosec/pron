FILE:desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md
---
sldb:
  by: agent
  at: '2026-11-16T05:15:12Z'
  authority: generated
  via: save_document_payload
id: task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- desk/inbox/20261104-233659-unclear-sldb-pron-ignora-sldb-entero-stores-check-falla-con-stores-core-ignored.md
- desk/tasks/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c.md
- .gitignore
depends_on:
- task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c
pills: []
files:
- .gitignore
- .sldb/store.yaml
- .sldb/core
- CHANGELOG.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# pron versiona .sldb/store.yaml y .sldb/core/ (opción A de JP); .sldb_cache/ sigue ignorada

## Rationale

_Explain why this task exists or the business driver behind it._

JP decidió el 2026-11-16 la opción A de la task.decision task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c (recibo owner-2 aceptado), con una precisión: se versionan .sldb/store.yaml y .sldb/core/ y no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime). Hoy .gitignore línea 10 ignora `.sldb/` entero, así que `sldb stores check` sale con error stores/core_ignored y los documentos del desk (TaskDoc, InboxNoteDoc, ReviewDoc de los recibos) que deskops escribe en .sldb/core no viajan en un clon. Medido el 2026-11-16: .sldb/ contiene solo store.yaml y core/ (789 archivos, 3,3 MB, mundo de `make world` más el desk); la caché runtime ya vive en .sldb_cache/ (23 MB), ignorada por .gitignore línea 26.

## Goal

_Describe the concrete result this task must produce._

En master de pron, .sldb/store.yaml y todo .sldb/core/ están versionados, .sldb_cache/ sigue ignorada, y `sldb stores check` ya no emite stores/core_ignored ni stores/cache_not_ignored.

## Scope

_State what is in scope and what is out of scope._

Entra: .gitignore (quitar la línea `.sldb/` y su comentario si queda huérfano; mantener `.sldb_cache/`), agregar al índice .sldb/store.yaml y .sldb/core/ completos, CHANGELOG.md. No entra: la línea `sldb/` de .gitignore (línea 11, es otro directorio), los errores store/model-unresolved de stores check (modelos del mundo de pron no importables sin el paquete; es otro problema), cambiar `make world`, el Makefile o src/pron, cambiar sldb, regenerar el mundo antes de commitear, y escribir docs/decision-store-sldb.md (lo hace la task.decision).

## Implementation Path

_Outline the expected implementation route or affected surface._

p1: en .gitignore borrar la línea '.sldb/' (línea 10) y reescribir el comentario de la línea 9, que hoy dice '# pron's own world: `make world` rebuilds the store and everything generated into it', como '# pron's own world: `make world` rebuilds these from the repo (the store .sldb/ is versioned; its cache .sldb_cache/ is not)'. La línea 'sldb/' (11) y '.sldb_cache/' (26) no se tocan. p2: viñeta en CHANGELOG.md al final de la lista bajo '## Sin publicar': '- El store de sldb de pron se versiona (.sldb/store.yaml y .sldb/core/), como en el resto de los repos; su caché .sldb_cache/ sigue ignorada (decisión de JP del 2026-11-16).' p3: correr las comprobaciones de Validation sobre el árbol de trabajo, sin git add ni commit: el ejecutor no indexa nada; el coordinador commitea .gitignore, CHANGELOG.md, .sldb/store.yaml y .sldb/core con deskops closeout commit --paths y pushea.

## Validation

_List the checks required before this task can close._

- git check-ignore -q .sldb/store.yaml; test $? -eq 1
- git check-ignore -q .sldb/core/store_index.yaml; test $? -eq 1
- git check-ignore -q .sldb_cache; test $? -eq 0
- TMPDIR=/dev/shm sldb stores check --pythonpath . 2>&1 | grep -cE 'stores/(core_ignored|cache_not_ignored)'   # imprime 0
- test $(git status --porcelain --untracked-files=all .sldb | wc -l) -eq $(find .sldb -type f | wc -l)   # git ve cada archivo del store

## Done When

_Name the observable condition that makes the task complete._

.sldb/store.yaml y todos los archivos de .sldb/core están en git (git ls-files .sldb cuenta lo mismo que find .sldb -type f); .sldb_cache/ sigue ignorada; sldb stores check sin stores/core_ignored ni stores/cache_not_ignored; commit en master de pron pusheado.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

