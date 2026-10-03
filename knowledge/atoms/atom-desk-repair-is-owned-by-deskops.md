---
id: atom-desk-repair-is-owned-by-deskops
title: Desk repair is owned by deskops
five_wh_one_plus: what
tags:
- system:deskops
- topic:workspace-health
- topic:ownership
- topic:boundary
---

# Desk repair is owned by deskops

## Answer

Desk repair covers all operations that fix or scaffold desk-owned workflow surfaces. This includes creating missing `desk/` directories, removing stale runtime files, and detecting untracked or invalid documents.

## Owned Operations

`deskops` owns repair for:
- Missing or incomplete `desk/` directory structure
- Stale graph runtime files (`.sldb/runtime/`)
- Detection and reporting of untracked desk documents
- Detection and reporting of malformed desk artifacts

## Not Owned

`deskops` does not own:
- SLDB store initialization or repair
- Model registration or field schema changes
- Document content repair (only detection, not correction)

## Evidence

`deskops/cli/commands/doctor.py` — implements the desk-owned repair surface.

## Tags

- system:deskops
- topic:workspace-health
- topic:ownership
- topic:boundary
