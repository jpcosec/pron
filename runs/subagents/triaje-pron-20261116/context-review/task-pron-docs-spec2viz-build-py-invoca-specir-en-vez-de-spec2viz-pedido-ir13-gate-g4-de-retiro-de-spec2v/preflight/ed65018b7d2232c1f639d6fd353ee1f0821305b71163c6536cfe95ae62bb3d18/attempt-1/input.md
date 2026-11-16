FILE:desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md
---
sldb:
  by: agent
  at: '2026-11-16T03:55:51Z'
  authority: generated
  via: save_document_payload
id: task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
current_node: ritual-execution
history: []
references:
- desk/inbox/20261115-224816-suggestion-ir13-pide-pasar-docs-spec2viz-build-py-de-pron-de-spec2viz-a-specir.md
- ../IR/docs/spec2viz/correspondencia-cli.md
- ../IR/docs/spec2viz/acta-de-retiro.md
depends_on: []
pills: []
files:
- docs/spec2viz/build.py
- docs/spec2viz/README.md
- CHANGELOG.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# pron docs/spec2viz/build.py invoca specir en vez de spec2viz (pedido IR13, gate G4 de retiro de spec2viz)

## Rationale

_Explain why this task exists or the business driver behind it._

IR13 (repo IR, gate de retiro de spec2viz) pide a pron migrar su única dependencia de spec2viz: las tres llamadas run('spec2viz', ...) de docs/spec2viz/build.py líneas 22, 23 y 24. Mientras estén, la fila de pron en IR/docs/spec2viz/acta-de-retiro.md (línea 53) queda "pendiente" y spec2viz no se puede retirar. specIR (repo IR, script `specir`) ofrece los mismos comandos con las mismas opciones (IR/docs/spec2viz/correspondencia-cli.md filas SV-K16, SV-K13 y SV-K04). Origen: nota del inbox desk/inbox/20261115-224816-suggestion-ir13-pide-pasar-docs-spec2viz-build-py-de-pron-de-spec2viz-a-specir.md.

## Goal

_Describe the concrete result this task must produce._

docs/spec2viz/build.py llama a `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos que hoy pasa a spec2viz, `python3 docs/spec2viz/build.py` termina con rc 0 sin spec2viz en el camino, y IR recibe por deskops message send el hash del commit que lo resuelve.

## Scope

_State what is in scope and what is out of scope._

Entra: docs/spec2viz/build.py (solo los tres run() de las líneas 22-24 y los docstrings de las líneas 1 y 30 que nombran el comando), docs/spec2viz/README.md (líneas 14 y 20-25, que documentan los comandos de spec2viz), CHANGELOG.md, instalar specir en la máquina como herramienta de uv, y la respuesta a IR con el commit. No entra: renombrar el directorio docs/spec2viz ni sus specs o catalog.yml; regenerar y commitear las salidas (docs/spec2viz/out/, index.html, offline.html y diagrams.md están en .gitignore); tocar el repo IR, spec2viz o sldb; desinstalar spec2viz; la política de .gitignore de .sldb/ (tarea task.decision aparte).

## Implementation Path

_Outline the expected implementation route or affected surface._

Dos binarios de specir con papeles distintos: build.py llama a 'specir' del PATH, que es la herramienta uv que instala p1; la comprobación de retiro usa /mnt/ssd/proyectos/SLDB_1/IR/.venv/bin/specir, que ya existe en robocop2 (verificado el 2026-11-16) y no se toca. Las líneas citadas son las de master al crear la tarea; si cambiaron, ubicar cada cambio por el texto citado. p1: instalar specir en el PATH: si 'uv tool list' ya muestra specir, 'uv tool install --reinstall --editable /mnt/ssd/proyectos/SLDB_1/IR'; si no, 'uv tool install --editable /mnt/ssd/proyectos/SLDB_1/IR'. Comprobar que 'specir diagram validate --help', 'specir diagram render --help' (acepta --backend y --out) y 'specir catalog build --help' (acepta --config y --out) salen con rc 0; si alguno falla, parar y reportar sin tocar pron. p2: en docs/spec2viz/build.py cambiar solo el primer argumento 'spec2viz' por 'specir' en las tres llamadas run('spec2viz', ...) de main() (líneas 22, 23 y 24: diagram validate, diagram render, catalog build); el resto de los argumentos y export_views no cambian. Docstring del módulo (línea 1), texto exacto: """Rebuild the specIR catalog and portable SVG views from semantic YAML.""" ; docstring de export_views (línea 30), texto exacto: """Export a specIR catalog with pre-rendered Mermaid to portable views.""". p3: en docs/spec2viz/README.md, en la frase de requisitos 'Desde este directorio, con spec2viz, mmdc, Python y PyYAML disponibles' (línea 14) y en el bloque 'Comandos principales del CLI de spec2viz' con sus tres comandos (líneas 20-25), reemplazar el comando spec2viz por specir y 'CLI de spec2viz' por 'CLI de specIR'; el nombre del directorio docs/spec2viz y el resto del README no cambian. p4: agregar en CHANGELOG.md, al final de la lista bajo '## Sin publicar', con el mismo formato de viñeta: '- docs/spec2viz/build.py valida, renderiza y arma el catálogo con specir en vez de spec2viz (pedido IR13 del gate de retiro de spec2viz).' p5: correr las tres comprobaciones de Validation, en ese orden, sobre el árbol de trabajo antes de commitear (la de retiro lee los archivos en disco); con las tres en verde, commit de build.py, README.md y CHANGELOG.md en master y push a origin. p6: deskops message send --root . --to IR --title 'pron: IR13 resuelto' '<hash del commit de p5>: docs/spec2viz/build.py usa specir (líneas 22-24)'.

## Validation

_List the checks required before this task can close._

- grep -nE "run\('spec2viz'" docs/spec2viz/build.py   # sin salida: ninguna llamada run() con spec2viz como comando
- cd docs/spec2viz && TMPDIR=/dev/shm python3 build.py   # rc 0; deja out/mermaid/*.mmd e index.html
- cd /mnt/ssd/proyectos/SLDB_1/IR && .venv/bin/specir retirement check --path graph_ui=../UIs/graph_ui --path deskops=../deskops --path pron=../pron --path sldb=../sldb --path spec2viz/.sldb=../spec2viz/.sldb | grep -P '^\s*pron\t'   # sin salida (el rc global sigue en 1 por otros repos)

## Done When

_Name the observable condition that makes the task complete._

grep -nE "run\('spec2viz'" docs/spec2viz/build.py vacío; python3 docs/spec2viz/build.py rc 0 con specir; specir retirement check no lista filas de pron; commit en master de pron pusheado; mensaje a IR enviado con ese hash.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

