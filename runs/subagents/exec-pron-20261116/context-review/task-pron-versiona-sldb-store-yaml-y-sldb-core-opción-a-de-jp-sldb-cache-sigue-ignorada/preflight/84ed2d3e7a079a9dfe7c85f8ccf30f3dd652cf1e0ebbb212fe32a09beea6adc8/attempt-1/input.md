FILE:desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md
---
sldb:
  by: agent
  at: '2026-11-16T05:21:28Z'
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

Entra (ejecutor): .gitignore (quitar la línea '.sldb/' y reescribir su comentario; mantener '.sldb_cache/') y la viñeta de CHANGELOG.md; nada más en el árbol de trabajo. Entra (coordinador, en el cierre): indexar y commitear .gitignore, CHANGELOG.md, .sldb/store.yaml y .sldb/core con deskops closeout commit --paths en master, y pushear. 'Lo que sea runtime' del store ya está fuera de .sldb/: el 2026-11-16 .sldb/ contiene solo store.yaml y core/ (verificado con ls y find), y la caché runtime vive en .sldb_cache/; si al ejecutar aparece en .sldb/ algo que no sea store.yaml ni core/, el ejecutor para y lo reporta sin ignorarlo ni versionarlo. No entra: la línea 'sldb/' de .gitignore (línea 11, otro directorio), los errores store/model-unresolved de stores check (otro problema; hacen que stores check salga con rc 1 igual), cambiar make world, el Makefile o src/pron, cambiar sldb, regenerar el mundo, y escribir docs/decision-store-sldb.md (lo hace la task.decision).

## Implementation Path

_Outline the expected implementation route or affected surface._

p1: en .gitignore borrar la línea '.sldb/' (línea 10) y reescribir el comentario de la línea 9, que hoy dice '# pron's own world: `make world` rebuilds the store and everything generated into it', como '# pron's own world: `make world` rebuilds these from the repo (the store .sldb/ is versioned; its cache .sldb_cache/ is not)'. La línea 'sldb/' (11) y '.sldb_cache/' (26) no se tocan. p2: viñeta en CHANGELOG.md al final de la lista bajo '## Sin publicar': '- El store de sldb de pron se versiona (.sldb/store.yaml y .sldb/core/), como en el resto de los repos; su caché .sldb_cache/ sigue ignorada (decisión de JP del 2026-11-16).' p3: correr las comprobaciones de Validation sobre el árbol de trabajo, sin git add ni commit: el ejecutor no indexa nada; el coordinador commitea .gitignore, CHANGELOG.md, .sldb/store.yaml y .sldb/core con deskops closeout commit --paths y pushea.

## Validation

_List the checks required before this task can close._

- git branch --show-current   # imprime master
- git check-ignore -q .sldb/store.yaml; test $? -eq 1   # rc 0 de test: store.yaml no ignorado
- git check-ignore -q .sldb/core/store_index.yaml; test $? -eq 1   # store_index.yaml existe en .sldb/core (verificado 2026-11-16); rc 0 de test
- git check-ignore -q .sldb_cache; test $? -eq 0   # rc 0: la caché sigue ignorada
- TMPDIR=/dev/shm sldb stores check --pythonpath . 2>&1 | grep -cE 'stores/(core_ignored|cache_not_ignored)'   # pasa si imprime 0 (grep sale con rc 1 en ese caso, es lo esperado; el rc de stores check no cuenta por los model-unresolved)
- test $(git status --porcelain --untracked-files=all .sldb | wc -l) -eq $(find .sldb -type f | wc -l)   # antes del commit: cada archivo del store aparece como untracked (??), ninguno ignorado

## Done When

_Name the observable condition that makes the task complete._

Ejecutor: las seis comprobaciones de Validation pasan sobre el árbol de trabajo con solo .gitignore y CHANGELOG.md modificados. Coordinador, tras el closeout: git ls-files .sldb | wc -l igual a find .sldb -type f | wc -l, commit en master de pron pusheado.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

