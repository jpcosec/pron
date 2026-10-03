---
id: atom-desk-health-delegates-store-diagnostics-to-sldb
title: Desk health delegates store diagnostics to SLDB
five_wh_one_plus: why
tags:
- system:deskops
- topic:workspace-health
- topic:boundary
- topic:sldb
---

# Desk health delegates store diagnostics to SLDB

## Answer

Desk health deliberately separates desk workspace repair from SLDB store health. The `deskops doctor` command delegates store-level diagnostics (model registration, document validity, field integrity) to `sldb stores check`, keeping the boundary clean between workflow-domain surfaces and shared document infrastructure.

## Boundary Rationale

- **Desk** owns workflow artifacts: tasks, boards, pills, rituals, atoms, routines, primitives
- **SLDB** owns document infrastructure: models, templates, fields, store indexes, validation

Mixing these concerns into one health command creates ambiguity about ownership and repair responsibility.

## Delegation Pattern

```
deskops doctor
  ├── desk structure checks  → deskops (own repair)
  ├── stale runtime files    → deskops (own repair)
  ├── untracked docs         → deskops (report only)
  ├── invalid docs           → sldb stores check (report via delegation)
  └── store integrity        → sldb stores check (delegate)
```

## Evidence

`deskops/cli/commands/doctor.py` calls `sldb stores check` for document validity and propagates findings to the operator.

## Tags

- system:deskops
- topic:workspace-health
- topic:boundary
- topic:sldb
