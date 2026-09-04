---
id: atom-contradictions-stored-not-resolved
title: Contradictions Stored Not Resolved
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- topic:provenance
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Contradictions Stored Not Resolved

## Answer

When a new proposition conflicts with an existing truth value in a WiGame (e.g., asserting true where false is already stored), the system rejects with status 'widerspruechlich' instead of overwriting. This preserves data integrity and forces explicit resolution through context or provenance, never silent mutation.
