---
id: surface-pron-kernel-sexp-read_write
system: pron
surface: kernel.sexp.read_write
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/kernel/sexp/read_write.py
---

# kernel.sexp.read_write

## Purpose

S-expressions: pron's structured language (spec 06, 13). A move is a list of forms; the natural
language surface is a wrapper that resolves a sentence to these forms and evaluates them.

## How It Works

Only the reader and the printer live here; what each form means is in pron.sexpr.forms.compiler.
Atoms are symbols (Sym), strings, integers, floats, and the symbols true, false and nil.

## Commands

read
read_one
write
