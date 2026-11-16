# Brief del ejecutor deskops-e-a868cc40330a (pron, task.decision del store .sldb/)

Eres el **ejecutor** de una tarea del desk de pron. No ves la conversación del coordinador: todo lo que
necesitas está aquí y en el TaskDoc. Escribes un documento y lo validas; **no** commiteas, no pusheas y no
tocas el desk. El cierre lo hace el coordinador.

- Repo (raíz de trabajo): `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. Haz `cd` ahí antes de todo.
  Tu pane arrancó en `/mnt/ssd/proyectos/SLDB_1` solo por el diálogo de confianza de Claude.
- TaskDoc (el contrato; léelo entero primero):
  `desk/tasks/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c.md`
- Recibo owner de JP (solo lectura):
  `desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/owner-2.md`
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-d-e1/`. Su `run.md` es del coordinador: no lo edites.

## Estado de partida

- **p1:** ya está. JP dispuso el recibo owner-2 como `accepted`:
  - `disposed_at: 2026-11-16T05:13:21Z`;
  - reason: «Opción A: JP 2026-11-16 (transmitida por el supervisor). Se versionan .sldb/store.yaml y .sldb/core/;
    no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime), que sigue ignorada.»

  Compruébalo con `deskops review status <id de la tarea> --root .` y leyendo el archivo del recibo.
- **p3:** ya está. La `task.code` de seguimiento existe:
  `desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md`.
  No crees otra.
- **p4:** el commit y el push los hace el coordinador. Tú no.

## Qué haces: solo p2

Crea `docs/decision-store-sldb.md` en español, en el estilo de los otros documentos de `docs/`
(por ejemplo `docs/contrato-de-capas.md`), con este contenido y en este orden:

1. Un título de nivel 1, por ejemplo `# Decisión: el store .sldb/ de pron se versiona`.
2. Una línea exacta, sola: `Opción elegida: A`.
3. La fecha del dispose de JP en formato `AAAA-MM-DD`: `2026-11-16`.
4. La razón, copiada del reason de JP, sin la letra inicial.
5. El contexto en pocas líneas:
   - el aviso de sldb c420809c, con la nota de origen
     `desk/inbox/20261104-233659-unclear-sldb-pron-ignora-sldb-entero-stores-check-falla-con-stores-core-ignored.md`;
   - que `.gitignore` ignoraba `.sldb/` entero porque `make world` lo regenera;
   - las opciones A, B y C tal como las describe el goal del TaskDoc.
6. Las consecuencias de la opción A:
   - para `sldb stores check`: deja de emitir `stores/core_ignored`;
   - para los recibos y documentos del desk: viajan en git;
   - el costo, tomado del goal: unos 740 documentos derivados versionados y diffs al correr `make world`;
   - qué sigue ignorado: `.sldb_cache/`.
7. La implementación: la `task.code` de seguimiento, nombrada por su id. El documento no implementa nada.

## Reglas

- Usa `TMPDIR=/dev/shm`.
- Toca **solo** `docs/decision-store-sldb.md`. No edites `.gitignore`, el Makefile, `src/` ni `desk/`, y no corras
  `make world` ni `sldb stores migrate-layout`.
- Prohibido: `git add`, `git commit`, `git stash`, `git push`, `pkill`, `pgrep`.

## Validación (del TaskDoc, ajustada a lo que el ejecutor puede comprobar)

- `grep -nE '^Opción elegida: [ABC]$' docs/decision-store-sldb.md` da exactamente una línea, y es `A`.
- `deskops review status <id de la tarea> --root .` muestra el recibo owner. Si no aparece, lee `owner-2.md` y
  registra su `verdict`.
- La tercera validación del TaskDoc (`git log` del documento) la cumple el coordinador con el commit de cierre.

## Qué entregas, en el run dir

- `validation.log`: los comandos con su salida y su rc.
- `git-status.txt`: la salida de `git status --short`.
- `result-summary.md`: qué escribiste y el resultado de la validación.

Al terminar, responde en una línea: `HANDOFF listo: <ruta>` o `BLOQUEADO: <motivo>`.
