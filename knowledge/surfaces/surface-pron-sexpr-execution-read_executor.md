---
id: surface-pron-sexpr-execution-read_executor
system: pron
surface: sexpr.execution.read_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/read_executor.py
---

# sexpr.execution.read_executor

## Purpose

Reading a relation (spec 03, 07): the edges of a document, and what they name.

## How It Works

`(targets rel NOUN)` reads the edges leaving the resolved subject and answers with their
targets; `(sources rel NOUN)` reads the edges arriving at the object and answers with their
sources. Neither side given is not a question anybody can answer. Whatever the read found
is narrowed by the predicates the sentence's extra modifiers left, noted as reads of the
move (spec 07), and remembered as the referent the next turn may say "them" about.

## Commands

ReadExecutor
