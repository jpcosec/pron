---
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co.md
- desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md
- desk/tasks/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/phase.md
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb, workspace:desk
tags:
- workspace:desk
---

# pron-repair Board

## Purpose

_Explain what this board routes and why it exists._

Route the active execution set for pron-repair.

## Notes

_Add short operational notes about the current routed set._

Bootstrap complete. Add active task docs under `desk/tasks/` and route them here.

## Task Details

_Generated from the task references above._

- pron vuelve a verde contra sldb main: la caché de aristas se lee de .sldb_cache y los goldens de la conversación se actualizan con su diff revisado [draft] - Con sldb origin/main instalado, la suite de pron pasa entera de a un archivo (0 failed, 0 errors) y el job check del CI vuelve a verde; ningún test ni código de pron nombra .sldb/runtime/ como ruta de caché.
- pron docs/spec2viz/build.py invoca specir en vez de spec2viz (pedido IR13, gate G4 de retiro de spec2viz) [draft] - docs/spec2viz/build.py llama a `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos que hoy pasa a spec2viz, `python3 docs/spec2viz/build.py` termina con rc 0 sin spec2viz en el camino, y IR recibe por deskops message send el hash del commit que lo resuelve.
- Decisión de JP: pron versiona .sldb/ (store.yaml + core/) o queda como excepción al layout de sldb c420809c [draft] - JP elige una de tres opciones y la elección queda escrita y commiteada en pron: (A) versionar .sldb/ como el resto de los repos: quitar la línea `.sldb/` de .gitignore y commitear store.yaml y core/, mundo derivado incluido; (B) separar stores: el mundo derivado de pron sale de .sldb/ a otro store ignorado y .sldb/ queda versionado solo con el desk (exige cambiar `pron init --world` y el Makefile); (C) pron queda como excepción declarada: .sldb/ sigue ignorado, stores check sigue en error y los recibos del desk no se versionan. Recomendación del coordinador: A, porque cumple la decisión del 2026-10-29 sin tocar código de pron y hace versionables los recibos; su costo es versionar unos 740 documentos regenerables y sus diffs al correr make world.
