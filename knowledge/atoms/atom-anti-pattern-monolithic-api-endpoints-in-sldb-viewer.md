---
id: atom-anti-pattern-monolithic-api-endpoints-in-sldb-viewer
title: 'Anti-pattern: monolithic API endpoints in SLDB Viewer'
five_wh_one_plus: what
tags: []
provenance: null
---

# Anti-pattern: monolithic API endpoints in SLDB Viewer

## Answer

SLDB surfaces (AST, StructuredDocModel, fields, markdown frontmatter) must be queried via independent commands (sldb ast show, sldb fields), not through a single monolithic UI endpoint. Markdown frontmatter must be preserved on save. No mocked 'coming soon' states for unbuilt surfaces are acceptable.
