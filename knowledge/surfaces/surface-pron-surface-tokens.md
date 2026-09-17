---
id: surface-pron-surface-tokens
system: pron
surface: surface.tokens
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/surface/tokens.py
---

# surface.tokens

## Purpose

Segmenting a sentence into tokens (spec 06 step 1).

## How It Works

A quoted run is one token, so is a word ending in ':' (the marker of a literal that
follows), a word, and each of the punctuation marks pron reads. What each token turns out
to be is the classifier's business; this is only where one token ends and the next begins.

## Commands

tokenize
