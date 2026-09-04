---
id: atom-canonical-json-as-stable-interchange-format
title: Canonical JSON as stable interchange format
five_wh_one_plus: how
tags:
- system:marcado
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Canonical JSON as stable interchange format

## Answer

The canonical JSON separates the authoring surface (Markdown + HTML-comment markers) from the computational model. The JSON structure includes format metadata, document info, plain text, marker tokens, normalized logical ranges with spans, graph edges, anchor listings, and validation diagnostics. The schema is defined in schema/canonical.schema.json and the export_document function in export.py assembles the full document graph.
