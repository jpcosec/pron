---
id: surface-pron-core-session
system: pron
surface: pron.core.session
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/session.py
---

# pron.core.session

## Purpose

Clarification session

## How It Works

atom-session-expires-by-ttl-and-store-hash: The clarification session lives in .knowledge/session.json under the cwd, holds exactly one pending expression with candidates, and is discarded when 15 minutes pass since creation or when the store's hash_a changes, since candidates may no longer exist after a store mutation. A new command always replaces the pending one.

## Commands

Session
Session.load(self) -> dict | None | The pending state, or None if absent/expired/invalidated.
Session.save(self, pending_sexpr: str, candidates: list[str]) -> None | Persist one pending expression (replaces any previous one).
Session.clear(self) -> None | Drop the pending state.
