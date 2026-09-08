---
id: surface-pron-bridges-documentation-bridge
system: pron
surface: pron.bridges.documentation_bridge
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/bridges/documentation_bridge.py
---

# pron.bridges.documentation_bridge

## Purpose

Track and verify the executable documentation in SLDB

## How It Works

atom-pron-cli-and-modules-are-documented-from-source: Every base command (`anchors`, `eval`, `anchor add`, `model add`, `project`, `docs`) gets a tracked `CliCommandDoc`, and every public module under `src/pron` gets a tracked `SurfaceDoc`, both derived by `pron docs` from a hand-authored guide next to the command and from the module's own AST. `pron docs --check` verifies there is no drift between the generated documents and the current source, that every generated and every authored knowledge document is tracked in SLDB, and that tags, provenance, roundtrip and store integrity all hold, without writing anything. This keeps the rule that every CLI component has at least one atom from decaying into stale prose: docs are checked mechanically, the same way kinesis already does it for its own CLI.

## Commands

synchronize_documentation(root: Path, *, check: bool) -> tuple[bool, str] | Regenerate or check the tracked docs and their SLDB roundtrip and integrity.
