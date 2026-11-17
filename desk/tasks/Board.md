---
sldb:
  by: agent
  at: '2026-11-17T01:37:14Z'
  authority: generated
  via: save_document_payload
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co.md
- desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md
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
- pron/.sldb enlaza deskops como repo hermano ../deskops/.sldb en vez de la ruta de robocop2 ../../../herramientas, y el check de pron clona deskops al lado [draft] - El enlace deskops de pron es '../deskops/.sldb' en .sldb/store.yaml y en .sldb/core/store_index.yaml. Resuelve en robocop2, en un layout como el del CI de sldb (pron y deskops lado a lado, sin /mnt/ssd/herramientas a la vista) y en el CI propio de pron, porque check.yml clona jpcosec/opsys (repo público de deskops) en ../deskops antes de make check.
