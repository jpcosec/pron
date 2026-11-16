---
sldb:
  by: agent
  at: '2026-11-16T07:12:21Z'
  authority: generated
  via: save_document_payload
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co.md
- desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md
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
- pron versiona .sldb/store.yaml y .sldb/core/ (opción A de JP); .sldb_cache/ sigue ignorada [draft] - En master de pron, .sldb/store.yaml y todo .sldb/core/ están versionados, .sldb_cache/ sigue ignorada, y `sldb stores check` ya no emite stores/core_ignored ni stores/cache_not_ignored.
