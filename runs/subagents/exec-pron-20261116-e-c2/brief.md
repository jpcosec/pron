# Brief del ejecutor deskops-e-fe40ac7a9ef8-a2 (pron, IR13), ciclo de corrección 2

Eres el **ejecutor** de una tarea del desk de pron. No ves la conversación del coordinador: todo lo que
necesitas está aquí y en el TaskDoc. Implementas y validas; **no** commiteas, no pusheas, no mandas
mensajes y no tocas el desk. El cierre lo hace el coordinador.

- Repo (raíz de trabajo): `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. Haz `cd` ahí antes de todo.
  Tu pane arrancó en `/mnt/ssd/proyectos/SLDB_1` solo por el diálogo de confianza de Claude.
- TaskDoc (el contrato; léelo entero primero):
  `desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md`
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-e-c2/`. Ya tiene `run.md`, que es el RunDoc del
  coordinador: **no lo edites**.

## Estado de partida: no repitas lo que ya está hecho

Un intento anterior (evidencia en `runs/subagents/exec-pron-20261116-e-a2/`, no la toques) ya dejó en el árbol de
trabajo los pasos **p1 a p4**:

- specir instalado con `--with-editable /home/robocop/herramientas/sldb`;
- las tres `run('specir', ...)` y los dos docstrings en `docs/spec2viz/build.py`;
- `docs/spec2viz/README.md` actualizado;
- la viñeta de `CHANGELOG.md`.

Ese intento paró en la validación V2 por dos fallos que ya existían en master. Ahora el TaskDoc trae el paso **p3b**
para arreglarlos.

1. **Verifica sin duplicar.** Comprueba con `git diff` y `specir diagram validate --help` (rc 0) que p1-p4 están
   como pide el TaskDoc:
   - Si algo falta o difiere del texto exacto del TaskDoc, corrígelo.
   - Si ya está, no lo vuelvas a aplicar. No dupliques la viñeta del CHANGELOG.
2. **Aplica p3b** tal como lo dice el TaskDoc:
   - (i) entrecomillar los `label` de las líneas 121 y 128 de `docs/spec2viz/specs/target.components.yml`;
   - (ii) en `docs/spec2viz/build.py`, en la llamada a `mmdc` de `export_views`, cambiar `'-w', '1800'` por
     `'--size', '1800'`.

   Si un texto citado no aparece exactamente una vez, para y repórtalo sin improvisar.
3. **Corre las tres comprobaciones de Validation, en orden.** La segunda lleva
   `PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH`. Las tres tienen que dar:
   - V1: sin salida;
   - V2: rc 0, imprimiendo `Generated 4 SVGs, diagrams.md and offline.html`;
   - V3: sin filas de pron. El rc 1 del pipeline es lo esperado; «verde» significa sin filas de pron.

## Reglas

- Usa `TMPDIR=/dev/shm` en cada comando.
- Toca solo los cuatro archivos de `files` del TaskDoc:
  - `docs/spec2viz/build.py`
  - `docs/spec2viz/README.md`
  - `docs/spec2viz/specs/target.components.yml`
  - `CHANGELOG.md`
- Correr `build.py` regenera salidas ignoradas por git (`out/`, `index.html`, `offline.html`, `diagrams.md`):
  está bien, pero no las agregues.
- Prohibido: `git add`, `git commit`, `git stash`, `--autostash`, `git push`, `pkill`, `pgrep`. Tampoco edites
  `desk/` ni `.sldb/`, no toques IR, spec2viz, sldb ni `/mnt/ssd/herramientas`, y no instales ni cambies mermaid-cli.
- Si una comprobación falla y no se arregla dentro de los cuatro archivos y del alcance del TaskDoc, para y
  repórtalo con la salida completa.

## Qué entregas, en el run dir

- `validation.log`: cada comando con su salida completa y su rc, en orden, más la verificación de p1-p4.
- `git-diff.txt`: la salida de `git diff -- docs/spec2viz/build.py docs/spec2viz/README.md docs/spec2viz/specs/target.components.yml CHANGELOG.md`.
- `git-status.txt`: la salida de `git status --short`.
- `result-summary.md`: qué verificaste, qué cambiaste, el resultado de cada validación, y cualquier desvío o duda.

Al terminar, responde en una línea: `HANDOFF listo: <ruta de result-summary.md>`, o `BLOQUEADO: <motivo>`.
