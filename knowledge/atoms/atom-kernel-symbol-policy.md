---
id: atom-kernel-symbol-policy
title: Kernel Symbol Policy
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Kernel Symbol Policy

## Answer

The boundary between code-level kernel semantics and fact-level Wi semantics. Kernel symbols (and, or, not, if, instance, equivalent) are reserved for the operational kernel and cannot be asserted as domain facts. Wi-level relations (has_property, part_of, causes, etc.) are domain knowledge stored as relational content. The classify_symbol() function determines layer membership.
