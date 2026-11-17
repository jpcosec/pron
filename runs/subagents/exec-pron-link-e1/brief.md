# Brief del ejecutor (pron, enlace a deskops como repo hermano)

Eres el **ejecutor** de una tarea del desk de pron. No ves la conversación del coordinador: todo lo que necesitas
está aquí y en el TaskDoc. Implementas y validas. **No** indexas, no commiteas, no pusheas y no tocas `desk/` ni el
store fuera de lo que piden los comandos de la tarea. El cierre lo hace el coordinador.

- Repo (raíz de trabajo): `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. Haz `cd` ahí antes de todo.
- TaskDoc (el contrato; léelo entero primero):
  `desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md`
- Run dir (tu evidencia): `runs/subagents/exec-pron-link-e1/`. Este brief es del coordinador: no lo edites.

## Qué haces

p0, p1, p2, p3 y p4 del Implementation Path, al pie de la letra, y después V1 a V8 de Validation en orden.

Precisiones del coordinador (resuelven residuales de la revisión de contexto):

- p0(a): `.deskops.log` aparece como untracked en la raíz y es un log local ignorable. Si `git status --porcelain -- . ':!runs'`
  muestra solo `?? .deskops.log`, la precondición se da por cumplida. Cualquier otra línea → BLOQUEADO.
- p2: el comentario va como línea YAML propia, indentada igual que las claves del paso y ubicada entre `- name:` y `run:`:
  ```yaml
      - name: deskops next to pron
        # .sldb/store.yaml links deskops as ../deskops/.sldb (sibling checkout)
        run: git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops
  ```
  Respeta la indentación que ya usan los pasos de `check.yml`.
- V4 y V6 tardan más de 10 min cada uno. Córrelos con un timeout generoso (40 min) y guarda la salida completa en archivos del run dir.
  Pueden ir en primer o segundo plano: cuentan el rc y la salida, no el modo.
- V4 y V6 clonan `https://github.com/jpcosec/opsys.git` (público). Si no hay red, BLOQUEADO.
- Al terminar, borra `/dev/shm/pron-link-ci` y `/dev/shm/pron-link-ci-control`. **No** borres `/dev/shm/pron-venv`.

## Reglas

- Usa `TMPDIR=/dev/shm` en todo.
- Edita solo lo que dice el TaskDoc: `.github/workflows/check.yml` y `CHANGELOG.md` a mano, y `.sldb/store.yaml` y
  `.sldb/core/store_index.yaml` **solo** con los dos comandos de sldb de p1.
- Prohibido: `git add`, `git commit`, `git stash` (ni autostash), `git push`, `git checkout`/`restore` sobre archivos, `pkill`,
  `pgrep` y `make world` o `make check` en el checkout real (`make world` solo en las copias de `/dev/shm` de V4 y V6).
- Ante cualquier desvío: para, escribe el motivo con la salida que lo muestra en `result-summary.md` y responde `BLOQUEADO: <motivo>`.

## Qué entregas, en el run dir

- `validation.log`: cada comando de V1–V8 con su salida (o la ruta del archivo con la salida completa, para V4 y V6) y su rc, en orden.
- `v4-world.log`, `v5-docs.log`, `v6-control.log`: salidas completas.
- `git-diff.txt`: `git diff HEAD -- .sldb/store.yaml .sldb/core/store_index.yaml .github/workflows/check.yml CHANGELOG.md`.
- `git-status.txt`: `git status --porcelain`.
- `result-summary.md`: qué cambiaste, el resultado de cada validación (PASA/FALLA con la evidencia) y los desvíos o dudas.

Al terminar, responde en una línea: `HANDOFF listo: runs/subagents/exec-pron-link-e1/result-summary.md` o `BLOQUEADO: <motivo>`.
