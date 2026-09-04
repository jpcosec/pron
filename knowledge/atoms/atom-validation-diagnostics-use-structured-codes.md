---
id: atom-validation-diagnostics-use-structured-codes
title: Validation diagnostics use structured codes
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Validation diagnostics use structured codes

## Answer

Each diagnostic carries a code and severity (error or warning) plus optional line, column, offset, namespace, and human-readable hint. Codes are grouped by subsystem: frontmatter_ (frontmatter_invalid_yaml, frontmatter_unclosed), marker_ (marker_syntax_invalid, marker_open_without_close), anchor_ (anchor_invalid_local_shape, anchor_missing), namespace_ (namespace_not_declared, namespace_crossing_forbidden), and graph_ (graph_endpoint_missing, graph_endpoint_not_unique, graph_endpoint_remote_deferred).
