---
id: surface-pron-sexpr-turn-form_turn
system: pron
surface: sexpr.turn.form_turn
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/form_turn.py
---

# sexpr.turn.form_turn

## Purpose

What `Session.eval` does inside its move (spec 13).

## How It Works

Forms are a move of their own: they never answer a pending question, so one that is still
open is dropped and the ledger says so. Forms that do not read as an s-expression are an
error before anything is resolved; forms that do are evaluated exactly as the forms a
sentence says, with the same permissions, pre-validation, writes, refresh and undo.

## Commands

FormTurn
