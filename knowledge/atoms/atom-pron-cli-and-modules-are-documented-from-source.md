---
id: atom-pron-cli-and-modules-are-documented-from-source
title: Every base CLI command and public module surface is documented from source, not by hand
five_wh_one_plus: why
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/documentation.py; src/pron/bridges/documentation_bridge.py
---

# Every base CLI command and public module surface is documented from source, not by hand

## Answer

Every base command (`anchors`, `eval`, `anchor add`, `model add`, `project`, `docs`) gets a tracked `CliCommandDoc`, and every public module under `src/pron` gets a tracked `SurfaceDoc`, both derived by `pron docs` from a hand-authored guide next to the command and from the module's own AST. `pron docs --check` verifies there is no drift between the generated documents and the current source, that every generated and every authored knowledge document is tracked in SLDB, and that tags, provenance, roundtrip and store integrity all hold, without writing anything. This keeps the rule that every CLI component has at least one atom from decaying into stale prose: docs are checked mechanically, the same way kinesis already does it for its own CLI.
