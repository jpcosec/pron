---
id: atom-document-identity-resolves-from-explicit-frontmatter-first
title: Document identity resolves from explicit frontmatter first
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Document identity resolves from explicit frontmatter first

## Answer

The extract_document_id function in anchors.py resolves document identity with this priority: asg.document_id in frontmatter overrides all; then document.id or document.document_id in frontmatter; then the file stem (Path.stem) as fallback. Returns None only when no path is available and no frontmatter id is set. This allows stable cross-document anchor references independent of filenames.
