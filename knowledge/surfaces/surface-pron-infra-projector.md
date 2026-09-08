---
id: surface-pron-infra-projector
system: pron
surface: pron.infra.projector
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/infra/projector.py
---

# pron.infra.projector

## Purpose

Projector: gives the evaluator a world

## How It Works

atom-the-projector-gives-the-evaluator-a-world: The infra layer ('knowledge model add' to register models, 'knowledge project' to materialize the kgdb snapshot) exists so the evaluator has referents to resolve against. It is component number nine, subordinate to the core: projection freshness is a usability concern (warn and instruct), never a hidden failure.

## Commands

model_add(root: Path, model_ref: str, pythonpath: str | None=None) -> tuple[bool, str] | Register a model in the local store through the sldb CLI surface.
refresh(root: Path, pythonpath: str | None=None) -> tuple[bool, str] | Single post-write hook: reindex sldb (semantic + sections) and rebuild graph.

Every write operation (create, assert, ingest, anchor add) must call this
so evaluators and kgdb never read stale indexes or a stale snapshot.
project(root: Path, pythonpath: str | None=None) -> tuple[bool, str] | Materialize the graph: semantic-export then ingest-sldb.
