# Brief del tester deskops-t-5c0748a304c0 (pron, versionar .sldb/)

Eres el **tester independiente**, con el rol `deskops-tester` en modo tester. No implementas, no corriges, no ruteas
y no cierras: compruebas y entregas evidencia. No ves la conversación del coordinador y **no debes leer** otros run
dirs.

- Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Haz `cd` ahí. Tu pane arrancó en `/mnt/ssd/proyectos/SLDB_1` solo por el
  diálogo de confianza.
- TaskDoc:
  `desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md`
- La decisión que implementa: `docs/decision-store-sldb.md`.
- El ejecutor dejó, sin indexar, cambios en `.gitignore` y `CHANGELOG.md`. El coordinador indexa y commitea después
  `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core`.
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-s-t1/`. Su `run.md` es del coordinador: no lo edites.

## Qué compruebas

1. **El diff contra el contrato.** `git diff -- .gitignore CHANGELOG.md` contra Scope e Implementation Path:
   - se quitó solo la línea `.sldb/`;
   - el comentario quedó con el texto exacto;
   - `sldb/` y `.sldb_cache/` siguen;
   - la viñeta de CHANGELOG es exacta y está al final de `## Sin publicar`.
2. **Las seis comprobaciones de Validation, tal cual y en orden.** V5 pasa si imprime `0`; el rc de stores check no
   cuenta. V6 pasa si los conteos son iguales.
3. **La decisión de JP: no se versiona nada runtime.**
   - Lista lo que hay en `.sldb/` (`find .sldb -maxdepth 2`): solo `store.yaml` y `core/` con `store_index.yaml`,
     `models/` y `documents/`.
   - Confirma que nada de `.sldb_cache/` aparece en `git status --porcelain --untracked-files=all`.
   - Busca dentro de `.sldb/` archivos que parezcan runtime o caché (locks, `*.lock`, `*.tmp`, `runtime/`, `edges/`,
     `sections/`, `semantic/`, `graphs/`) y, si los hay, repórtalos.
4. **Nada más cambió.** En `git status --short`, fuera de `desk/`, `runs/`, `.deskops.log` y los untracked de
   `.sldb/`, solo deben aparecer `.gitignore` y `CHANGELOG.md`.
5. **El store se lee bien.** `TMPDIR=/dev/shm sldb stores check --pythonpath .` no tiene errores `stores/*`. Lista los
   errores que tenga y di si son solo `store/model-unresolved`.

## Reglas

- Usa `TMPDIR=/dev/shm`. No edites nada.
- Prohibido: `git add`, `git commit`, `git stash`, `git checkout`, `git restore`, `git push`, `pkill`, `pgrep`. No
  corras `make world`.

## Qué entregas, en el run dir

- `test.log`: los comandos con su salida y su rc.
- `result-summary.md`: `PASS` o `FAIL` en la primera línea; después, cada comprobación (1 a 5) con su evidencia.

Al terminar, responde en una línea: `TEST PASS: <ruta>` o `TEST FAIL: <ruta>`.
