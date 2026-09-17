---
id: surface-pron-sexpr-execution-why_executor
system: pron
surface: sexpr.execution.why_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/why_executor.py
---

# sexpr.execution.why_executor

## Purpose

Why a document is the way it is (spec 07): the ledger, and the edges that ground it.

## How It Works

The ledger knows the last move that wrote this document: who said what, when, and which
fields it moved; the checks that move's trace kept — a transition, a condition — are worth
repeating, because they are the reason the write was allowed. The graph knows the edges on
the WHY and PROVENANCE axes, which are the reason someone gave. Without a document named,
the question is about whatever was last written or last talked about.

## Commands

WhyExecutor
