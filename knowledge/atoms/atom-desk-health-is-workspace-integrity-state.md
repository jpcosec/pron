---
id: atom-desk-health-is-workspace-integrity-state
title: Desk health is workspace integrity state
five_wh_one_plus: what
tags:
- system:deskops
- topic:workspace-health
- topic:diagnosis
---

# Desk health is workspace integrity state

## Answer

Desk health measures whether a desk workspace contains the expected structure, tracked documents, and operational surfaces without corruption or drift. It is the runtime integrity state of the `desk/` directory and its relationship to the tracking infrastructure.

## Evidence

`deskops/cli/commands/doctor.py` checks:
- Missing or malformed `desk/` directory structure
- Untracked modeled documents in `desk/`
- Invalid task/pill/atom/routine documents (malformed YAML frontmatter)
- Stale graph runtime files (`.sldb/runtime/`)

## Related Atoms

- `atom-stale-state-causes-agent-hallucination` — explains why health matters for agents
- `atom-desk-health-delegates-store-diagnostics-to-sldb` — defines the boundary

## Tags

- system:deskops
- topic:workspace-health
- topic:diagnosis
