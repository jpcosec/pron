---
id: atom-graph-edge-endpoints-validate-locally-defer-remotely
title: Graph edge endpoints validate locally, defer remotely
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Graph edge endpoints validate locally, defer remotely

## Answer

Local endpoints (without '#') are validated immediately: they must exist in the parsed document and be unique. Remote endpoints (with '#') are checked for syntactically valid anchor shape but their actual resolution is deferred — a lint finding is emitted. This allows graph edges to reference cross-document anchors without requiring the remote document to be loaded during local validation.
