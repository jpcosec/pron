---
id: surface-pron-sexpr-unknown_words
system: pron
surface: sexpr.unknown_words
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/unknown_words.py
---

# sexpr.unknown_words

## Purpose

A word this projection does not have (spec 05 §Calce aproximado, spec 06).

## How It Works

Nothing is guessed and nothing is run. The lexicon's nearest words are offered, and if none
of them is a value, the existing values of the world are ranked too and offered as the
sentence that would resolve. The trace says which matcher decided and what it found, so an
answer nobody expected can be explained without running anything again.

## Commands

UnknownWords
