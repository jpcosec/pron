---
id: atom-desk-health-is-measured-by-cli-diagnostics
title: Desk health is measured by CLI diagnostics
five_wh_one_plus: how
tags:
- system:deskops
- topic:workspace-health
- topic:diagnosis
- topic:cli
---

# Desk health is measured by CLI diagnostics

## Answer

Desk health is measured through `deskops doctor`, which runs a fixed diagnostic surface over the workspace. The command returns findings grouped by severity: missing structure, untracked documents, invalid documents, and stale runtime files.

## Diagnostic Surface

`deskops doctor` reports:
1. **Missing desk structure** — `desk/`, `desk/tasks/`, `desk/drawer/`, `desk/tasks/Board.md`
2. **Untracked desk documents** — Markdown files in `desk/` not registered in `.sldb`
3. **Invalid desk documents** — Documents with malformed YAML, missing required fields, or validation errors
4. **Stale runtime files** — Leftover `.sldb/runtime/*.json` files from interrupted graph builds

## Repairability

| Finding | Auto-repair | Manual required |
|---------|-------------|-----------------|
| Missing structure | Scaffold with `deskops doctor --repair` | — |
| Untracked docs | Report only | Use `sldb docs track` |
| Invalid docs | Report only | Fix syntax or run `sldb stores update` |
| Stale runtime | Delete with `deskops doctor --repair` | — |

## Evidence

`deskops/cli/commands/doctor.py` — `DoctorCLI.run()` method implements these checks.

## Tags

- system:deskops
- topic:workspace-health
- topic:diagnosis
- topic:cli
