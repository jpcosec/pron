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
provenance: src/pron/cli/main.py:_cmd_docs
---

# pron docs

## Synopsis

Derive CLI command docs and module surface docs from the source tree.

## Purpose

Derive CLI command docs and module surface docs from the source tree.

## How It Works

Describes every base command from its handler's own docstring (kept
next to the implementation, not a parallel file) and every public
module under src/pron from its AST, registers CliCommandDoc/SurfaceDoc
if needed, writes and tracks the documents, and refreshes the store.
--check instead verifies there is no drift, that every generated and
every authored document is tracked, and that tags, provenance,
roundtrip and store integrity all hold, without writing anything.

## Arguments

--check | optional | Verify instead of regenerating; exits non-zero on drift.
--kb <root> | optional | KB root; defaults to the current working directory.

## Usage

pron docs
pron docs --check
