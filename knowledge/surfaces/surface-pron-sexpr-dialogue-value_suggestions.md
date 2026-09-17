---
id: surface-pron-sexpr-dialogue-value_suggestions
system: pron
surface: sexpr.dialogue.value_suggestions
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/dialogue/value_suggestions.py
---

# sexpr.dialogue.value_suggestions

## Purpose

PLAN 11 P2 (spec 05 §Calce aproximado): an unknown word ranked against real values.

## How It Works

When an unknown word has no vocabulary neighbor of kind 'value', it is ranked against the
existing values of every string, non-enum field of this projection's models, and what is
offered is the sentence that would resolve — 'the <model> <alias-field or field> <value>' —
so the candidate is usable as said. Free prose is not a nameable value and is skipped; a
field with more distinct values than matching.max_values is too wide to rank and says so in
the trace. Same cap as P1; this never executes anything on its own.

## Commands

ValueSuggestions
