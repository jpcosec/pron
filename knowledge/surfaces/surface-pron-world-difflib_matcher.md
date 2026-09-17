---
id: surface-pron-world-difflib_matcher
system: pron
surface: world.difflib_matcher
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/world/difflib_matcher.py
---

# world.difflib_matcher

## Purpose

The no-network fallback of the approximate-matching port (spec 11 §2): difflib over
accent-stripped strings. `normalize` is that stripping, and is also how the lexicon and the
classifier compare a written word with a listed form (spec 05, 06).

## How It Works

The no-network fallback of the approximate-matching port (spec 11 §2): difflib over
accent-stripped strings. `normalize` is that stripping, and is also how the lexicon and the
classifier compare a written word with a listed form (spec 05, 06).

## Commands

normalize
DifflibMatcher
