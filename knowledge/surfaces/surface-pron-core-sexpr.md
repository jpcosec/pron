---
id: surface-pron-core-sexpr
system: pron
surface: pron.core.sexpr
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/sexpr.py
---

# pron.core.sexpr

## Purpose

S-expression kernel: parse and serialize the Meaning layer

## How It Works

atom-sexpr-serialization-quotes-selectors-and-roundtrips: The canonical s-expression format is a small lisp subset: symbols are unquoted, selectors are always double-quoted strings with escaped inner quotes, options are trailing :keyword-symbol pairs, and refs take three shapes: (docs model), (doc model "selector"), (rel relation expr). Every valid expression roundtrips: parse(serialize(e)) equals e, and Meaning-to-Surface serialization uses the canonical noun-first order.

## Commands

Symbol: name: str
Keyword: name: str
SexprError
parse(text: str) -> SExpr | Parse canonical s-expression text into the Meaning structure.
serialize(expr: SExpr) -> str | Serialize a Meaning structure back to canonical text (roundtrips).
