---
id: cmd-pron-docs
system: pron
command_path: pron docs
synopsis: Derive CLI command docs and module surface docs from the source tree.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:main
---

# pron docs

## Synopsis

Derive CLI command docs and module surface docs from the source tree.

## Purpose

Derive CLI command docs and module surface docs from the source tree.

## How It Works

Describes every base CLI command from a hand-authored guide (kept next to the command's implementation) and every public module under src/pron from its AST, registers CliCommandDoc/SurfaceDoc if needed, writes and tracks the documents, and refreshes the store. --check instead verifies there is no drift, that every generated document is tracked, that every authored document is tracked, and that tags/provenance/roundtrip/store integrity all hold, without writing anything.

## Arguments

--check | optional | Verify instead of regenerating; exits non-zero on drift.
--kb <root> | optional | KB root; defaults to the current working directory.

## Usage

pron docs
pron docs --check
