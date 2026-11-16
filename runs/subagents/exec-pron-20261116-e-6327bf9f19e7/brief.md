# Brief del ejecutor deskops-e-6327bf9f19e7 (pron, IR13), intento 1

Eres el **ejecutor** de una tarea del desk de pron. No ves la conversación del coordinador: todo lo que
necesitas está aquí y en el TaskDoc. Implementas y validas; **no** commiteas, no pusheas, no mandas
mensajes y no tocas el desk. El cierre lo hace el coordinador.

- Repo (raíz de trabajo): `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. Haz `cd` ahí antes de todo.
  Tu pane arrancó en `/mnt/ssd/proyectos/SLDB_1` solo por el diálogo de confianza de Claude.
- TaskDoc (el contrato; léelo entero primero):
  `desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md`
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-e-6327bf9f19e7/`. Ya tiene `run.md`, que es el RunDoc del
  coordinador: **no lo edites**.

## Qué haces

Los pasos p1 a p4 del Implementation Path del TaskDoc, al pie de la letra:

1. **p1:** instalar specir como herramienta uv.
2. **p2:** cambiar las tres llamadas `run()` y los dos docstrings de `docs/spec2viz/build.py`.
3. **p3:** actualizar `docs/spec2viz/README.md`. La frase de requisitos queda «con `specir`, `mmdc`, Python y PyYAML
   disponibles».
4. **p4:** agregar la viñeta de `CHANGELOG.md` al final de la lista bajo `## Sin publicar`.

Después corre la validación de **p5**: las tres comprobaciones de la sección Validation del TaskDoc, en orden,
sobre el árbol de trabajo. La de retiro pasa si `grep` no da salida; el rc 1 del pipeline es lo esperado.

**No hagas** el commit ni el push de p5, ni el mensaje a IR de p6: eso lo hace el coordinador.

## Reglas

- Usa `TMPDIR=/dev/shm` en cada comando.
- Toca solo `docs/spec2viz/build.py`, `docs/spec2viz/README.md` y `CHANGELOG.md`. La instalación de specir
  ocurre fuera del repo.
- No regeneres salidas para commitearlas: `docs/spec2viz/out/`, `index.html`, `offline.html` y
  `diagrams.md` están en `.gitignore`. Correr `build.py` las regenera, y eso está bien.
- Prohibido: `git add`, `git commit`, `git stash`, `--autostash`, `git push`, `pkill`, `pgrep`. Tampoco edites
  `desk/` ni `.sldb/`, ni toques los repos IR, spec2viz o sldb.
- Si p1 falla (specir no se instala o sus `--help` fallan), para sin tocar pron y repórtalo.
- Si una validación falla, puedes corregir dentro de los tres archivos permitidos. Si no se arregla así,
  para y repórtalo.

## Qué entregas, en el run dir

- `validation.log`: cada comando de validación con su salida completa y su rc, en orden, más la salida de
  `specir --help | head -5` y de `uv tool list | grep -A2 specir`.
- `git-diff.txt`: la salida de `git diff -- docs/spec2viz/build.py docs/spec2viz/README.md CHANGELOG.md`.
- `git-status.txt`: la salida de `git status --short`.
- `result-summary.md`: qué hiciste en cada paso, el resultado de cada validación, y cualquier desvío o duda.

Al terminar, responde en una línea: `HANDOFF listo: <ruta de result-summary.md>`, o `BLOQUEADO: <motivo>`.
