---
id: atom-offsets-and-spans-are-derived-evidence-not-durable-identity
title: Offsets and spans are derived evidence, not durable identity
five_wh_one_plus: why
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Offsets and spans are derived evidence, not durable identity

## Answer

Byte offsets and character spans change whenever the source document is edited — inserting a word shifts every subsequent offset. The symbolic marker key (e.g. rhet:decision.use_asg) is the durable anchor reference because it is invariant under most edits. Offsets are computed during parsing as derived evidence for tooling but must never be treated as the canonical anchor identity.
