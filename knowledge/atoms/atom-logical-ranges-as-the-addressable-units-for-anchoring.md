---
id: atom-logical-ranges-as-the-addressable-units-for-anchoring
title: Logical ranges as the addressable units for anchoring
five_wh_one_plus: what
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Logical ranges as the addressable units for anchoring

## Answer

Paired open/close markers normalize into a LogicalRange with key, namespace, classification, facets, start/end positions (line+column+offset), and extracted plain text. The symbolic marker key (e.g. rhet:decision.use_asg) is the durable identity for anchoring; byte offsets are derived evidence that change on source edits.
