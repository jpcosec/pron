---
id: surface-pron-core-results
system: pron
surface: pron.core.results
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/results.py
---

# pron.core.results

## Purpose

Typed result values shared across components

## How It Works

atom-resolution-outcomes-are-typed-values-not-exceptions: noun_resolver returns exactly one of Resolved(doc), Ambiguous(candidates, question), or Missing(motive, nearest) as plain values. Cross-component errors are typed values (including SemanticError); exceptions are reserved for bugs, never for control flow.

## Commands

Resolved: name: str; model: str; path: str; payload: dict[str, Any]
Ambiguous: question: str; candidates: list[str]
Missing: motive: str; nearest: list[str]
SemanticError: symbol: str; message: str; hint: str = ''
OperationResult: status: str; payload: Any = None; refs: list[str] = field(default_factory=list); provenance: str = ''
to_dict(value: object) -> dict[str, Any] | Project any result value to a JSON-serializable dict.
