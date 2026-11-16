---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: IR
# e.g., target_repo
target_project: pron-repair
# ISO 8601 timestamp
created_at: '2026-11-15T22:48:16'
# open | closed
status: open
# project identity that acknowledged the note
# ISO 8601 timestamp, set when acknowledged
---

# IR13 pide pasar docs/spec2viz/build.py de pron de spec2viz a specir

_Describe the incoming message with enough evidence to triage._

IR13 (gate de retiro de spec2viz, repo IR) pide migrar la única dependencia de pron sobre spec2viz. El retiro no está declarado y no se borra nada todavía: este es el pedido de migración que exige el gate (G4). Salida del comprobador `specir retirement check` (IR, solo lectura) sobre pron:

- `docs/spec2viz/build.py:22` `run('spec2viz', 'diagram', 'validate', *specs)` -> `specir diagram validate` (provisional en specIR hasta que sldb tenga su comando de validación; misma entrada).
- `docs/spec2viz/build.py:23` `run('spec2viz', 'diagram', 'render', *specs, '--backend', 'mermaid', '--out', 'out/mermaid')` -> `specir diagram render` (mismas opciones, `--backend` sigue siendo alias de `--renderer`).
- `docs/spec2viz/build.py:24` `run('spec2viz', 'catalog', 'build', '--config', 'catalog.yml', '--out', 'index.html')` -> `specir catalog build` (mismas opciones; la página es la de spec2viz byte a byte, IR13b).

specIR se instala desde el repo IR (`uv pip install -e <IR>`, script `specir`); la tabla completa está en `IR/docs/spec2viz/correspondencia-cli.md`. Cuando esté resuelto, respondan con la referencia del commit para registrarla en `IR/docs/spec2viz/acta-de-retiro.md`.
