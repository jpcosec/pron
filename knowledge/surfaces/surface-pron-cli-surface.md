---
id: surface-pron-cli-surface
system: pron
surface: pron.cli.surface
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/surface.py
---

# pron.cli.surface

## Purpose

Surface tokenizer + desugarer: positional grammar -> s-expression

## How It Works

atom-surface-grammar-is-positional-and-order-agnostic: The surface grammar accepts noun-first ('user juanito check preferences') and verb-first ('next task --summary') orders, and both desugar deterministically to the same s-expression. There is no free NLP: every token must resolve against the anchor table, and the first unanchored token determines the error message.

## Commands

desugar(tokens: list[str], registry: AnchorRegistry) -> SExpr | SemanticError | Deterministically translate surface tokens into one s-expression.
