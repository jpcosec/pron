---
id: atom-sldb-should-own-tracked-document-structure-for-future-kb-documents
title: SLDB should own tracked document structure for future KB documents
five_wh_one_plus: what
tags:
  - system:sldb
  - topic:document_structure
  - layer:document
  - entity:tracked-document
provenance: Derived from `spec/source_apps/sldb.md` and `spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md` as a synthesis about where tracked KB document structure should live.
---

# SLDB should own tracked document structure for future KB documents

## Answer

For future KB documents, the tracked document structure should be treated as an SLDB responsibility rather than as an ad hoc property of a higher-level workflow surface. SLDB already owns the structurally aware Markdown model, field-level extraction, document tracking, store registration, and indexing needed to keep document structure stable and queryable. That distinction matters because authoring surfaces such as deskops can change, while the tracked document contract has to remain the durable substrate for creation, parsing, and recovery.
