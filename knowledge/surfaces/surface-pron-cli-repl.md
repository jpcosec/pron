---
id: surface-pron-cli-repl
system: pron
surface: pron.cli.repl
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/repl.py
---

# pron.cli.repl

## Purpose

Interactive loop over the same Meaning layer as `eval` and the surface command

## How It Works

atom-repl-shares-the-evaluator-and-answers-ambiguity-in-memory: `pron repl` has no grammar or evaluator of its own: every line is either direct Meaning (`(...)`) or surface tokens desugared through the same `AnchorRegistry`, then run through the same `Evaluator` used by `pron eval` and the non-interactive surface command. This keeps the REPL from drifting into a second dialect. The one real difference is disambiguation: outside the REPL, an ambiguous result is persisted to `.pron/session.json` so a *separate* CLI invocation can answer it later; inside the REPL, the pending question and its candidates live in a local variable for the life of the process, since the next line is already the same conversation, SHRDLU-style — a unique referent proceeds, an ambiguous one asks and waits, a missing one explains what was looked for. `:internals` exists because the default renderer never shows which anchor grounded which symbol; the REPL is where a person actually watches that resolution happen.

## Commands

run(root: Path, fmt: str='text') -> int | Read-eval-print loop: surface tokens or direct `(...)` Meaning, evaluated
against the same Evaluator as `pron eval`. An ambiguous result opens a
pending question; typing one of its candidates on the next line answers
it in place of the ambiguous selector, entirely in memory.
