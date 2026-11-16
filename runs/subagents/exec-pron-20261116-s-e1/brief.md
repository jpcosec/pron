# Brief del ejecutor deskops-e-5772eb9505bd (pron, versionar .sldb/)

Eres el **ejecutor** de una tarea del desk de pron. No ves la conversación del coordinador: todo lo que
necesitas está aquí y en el TaskDoc. Implementas y validas; **no** indexas, no commiteas, no pusheas y no tocas el
desk. El cierre lo hace el coordinador.

- Repo (raíz de trabajo): `/mnt/ssd/proyectos/SLDB_1/pron`. Haz `cd` ahí antes de todo. Tu pane arrancó en
  `/mnt/ssd/proyectos/SLDB_1` solo por el diálogo de confianza de Claude.
- TaskDoc (el contrato; léelo entero primero):
  `desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md`
- La decisión que implementa: `docs/decision-store-sldb.md` (solo lectura).
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-s-e1/`. Su `run.md` es del coordinador: no lo edites.

## Qué haces

Los pasos p1, p2 y p3 del Implementation Path, al pie de la letra:

1. **p1:** en `.gitignore`, borrar la línea `.sldb/` y reescribir el comentario anterior con el texto exacto del
   TaskDoc.
2. **p2:** agregar la viñeta de `CHANGELOG.md` al final de la lista de viñetas con guion bajo `## Sin publicar`,
   justo antes de `## 1.0.0`.
3. **p3:** correr las seis comprobaciones de Validation, en orden, sobre el árbol de trabajo.

Cómo se leen:

- Si `git branch --show-current` no imprime `master`, para y repórtalo sin tocar nada.
- Los archivos de `.sldb/` **deben** aparecer como untracked (`??`) en V6. Que aparezcan es lo esperado: no
  cuentan como «modificados».
- V5 pasa si imprime `0`. El rc de `sldb stores check` no cuenta, porque los errores store/model-unresolved quedan
  fuera de alcance.

## Reglas

- Usa `TMPDIR=/dev/shm`.
- Edita solo `.gitignore` y `CHANGELOG.md`. No toques `.sldb/` ni `.sldb_cache/` (ni los borres, ni los
  regeneres), ni el Makefile, `src/` o `desk/`. No corras `make world` ni `sldb stores migrate-layout`.
- Prohibido: `git add`, `git commit`, `git stash`, `git push`, `pkill`, `pgrep`.
- Si en `.sldb/` aparece algo distinto de `store.yaml` y `core/`, para y repórtalo sin ignorarlo ni versionarlo.

## Qué entregas, en el run dir

- `validation.log`: cada comando con su salida y su rc, en orden. Para `sldb stores check`, incluye también su
  salida completa.
- `git-diff.txt`: la salida de `git diff -- .gitignore CHANGELOG.md`.
- `git-status.txt`: la salida de `git status --short | grep -v '^?? .sldb/'`, más el conteo de
  `git status --porcelain --untracked-files=all .sldb | wc -l`.
- `result-summary.md`: qué cambiaste, el resultado de cada validación y los desvíos o dudas.

Al terminar, responde en una línea: `HANDOFF listo: <ruta>` o `BLOQUEADO: <motivo>`.
