---
id: surface-pron-bridges-write-models
system: pron
surface: pron.bridges.write_models
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/bridges/write_models.py
---

# pron.bridges.write_models

## Purpose

Doc contracts for write-produced knowledge docs, defined at the bridge door

## How It Works

atom-write-operations-record-provenance-of-the-command-that-produced-them: Every write operation (assert, create, ingest) goes through sldb document and field operations and records the evaluated command as provenance. This is SHRDLU's action memory made auditable: any stored fact can be traced back to the exact expression, anchors, and referents that produced it.

## Commands

FactDoc: id: str = Field(description="Stable id, conventionally 'fact-<slug>-<timestamp>'."); fact: str = Field(description='The asserted statement, stored verbatim as a true fact.'); tags: list[KnowledgeTag] = Field(default_factory=list, description='Namespaced semantic tags for retrieval and grouping.'); provenance: str | None = Field(default=None, description='The full evaluated s-expression command that produced this fact.'); provenance_at: str | None = Field(default=None, description='UTC ISO-8601 timestamp of the write that produced this fact.')
PropositionDoc: id: str = Field(description="Stable id, conventionally 'proposition-<timestamp>'."); title: str = Field(description='Short human title of the ingested proposition or document.'); proposition: str = Field(description='The registered content: a proposition or document text, stored verbatim.'); tags: list[KnowledgeTag] = Field(default_factory=list, description='Namespaced semantic tags for retrieval and grouping.'); provenance: str | None = Field(default=None, description='The full evaluated s-expression command that produced this registration.'); provenance_at: str | None = Field(default=None, description='UTC ISO-8601 timestamp of the write that produced this registration.')
