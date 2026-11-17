# Brief del tester (pron, enlace a deskops como repo hermano)

Eres el **tester independiente** de una tarea del desk de pron. Un ejecutor ya implementó el cambio en el árbol de
trabajo, sin commit. Tú **no implementas, no corriges, no commiteas ni pusheas**: verificas y entregas evidencia, con
veredicto PASA o FALLA. No te fíes de la evidencia del ejecutor: rehaz las comprobaciones por tu cuenta.

- Repo: `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. El cambio está sin commitear contra `HEAD`.
- Contrato: `desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md`
  (léelo entero: Goal, Scope, Implementation Path y Validation V1–V8).
- Notas que originan la tarea (contexto):
  `desk/inbox/20261116-194348-*.md` y `desk/inbox/20261116-195724-*.md`.
- Evidencia del ejecutor (solo para contrastar): `runs/subagents/exec-pron-link-e1/`.
- Tu run dir: `runs/subagents/test-pron-link-t1/`. Este brief es del coordinador: no lo edites.
- Venv: `/dev/shm/pron-venv` (pron y sldb main editables). Compruébalo con
  `/dev/shm/pron-venv/bin/python -c "import pron, sldb; print(pron.__file__, sldb.__file__)"`. **No lo borres.**

## Qué verificas

1. **Diff según contrato.** `git status --porcelain` y `git diff HEAD`: solo `.sldb/store.yaml`, `.sldb/core/store_index.yaml`,
   `.github/workflows/check.yml` y `CHANGELOG.md` (más `?? .deskops.log` y `?? runs/...`, que no cuentan). En los dos `.sldb`
   solo cambia la línea `path:` del enlace deskops (si cambiara `store_hash`, también se acepta). El paso de `check.yml` coincide
   con p2 del TaskDoc y queda entre `Install` y `check (lints + typecheck + tests + docs)`. La viñeta de CHANGELOG coincide con p3.
2. **V1, V2, V3, V7** del TaskDoc, tal cual, en el checkout real.
3. **Layout del CI de sldb con caché fría (V4+V5)**, con tus propias rutas: `W=/dev/shm/pron-link-t1`, y la copia de control
   en `/dev/shm/pron-link-t1-control` (V6). Mismo procedimiento que el TaskDoc, sustituyendo esas rutas. `make world` tarda
   más de 10 min: usa un timeout de 40 min. Guarda las salidas completas.
4. **Layout del CI propio de pron**: simula lo que hace `check.yml` en Actions. Haz otra copia `/dev/shm/pron-link-t1-gh/pron`
   (rsync como en V4), y desde `/dev/shm/pron-link-t1-gh/pron` ejecuta literalmente el `run:` del paso nuevo
   (`git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops`). Después corre
   `PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python`: rc 0, sin `No store_index.yaml`.
5. **Suite completa de pron** en el checkout real (no la acotes):
   `cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 3600 /dev/shm/pron-venv/bin/python -m pytest -q -p syrupy -p xdist -n 4`
   → `suite.log`. La línea base conocida del 2026-11-16 es 475 passed y 7 failed, ninguno por esta tarea: 4 goldens de
   `tests/golden/test_16_*`, `test_09` (solo falla con xdist), `tests/world/test_04_store_by_doc_id.py` y
   `tests/world/test_10_federation.py` (deriva de sldb, Doc 'table-77' not found). Lista cada FAIL y di si está en esa línea
   base. Un FAIL nuevo hace FALLAR el veredicto, salvo que demuestres que también falla en HEAD sin el cambio. Para eso, usa
   una copia de `git archive HEAD` en `/dev/shm`, nunca stash ni checkout en el repo.
   Si el plugin xdist no está, instala `pytest-xdist` en el venv con `VIRTUAL_ENV=/dev/shm/pron-venv uv pip install pytest-xdist`.
6. `tests/world/test_01_world_store.py` pasa por sí solo (es la evidencia de tests del cierre).

## Reglas

- `TMPDIR=/dev/shm` en todo. Prohibido: `git add`, `commit`, `stash` (ni autostash), `push`, `checkout`/`restore`, `pkill`, `pgrep`,
  editar archivos del repo y correr `make world` o `make check` en el checkout real.
- Al terminar, borra tus copias `/dev/shm/pron-link-t1*` (no el venv).

## Qué entregas, en tu run dir

- `test.log`: cada comprobación (1–6), con comando, rc y salida, o la ruta del archivo con la salida.
- `v4-world.log`, `v5-docs.log`, `v6-control.log`, `gh-layout.log`, `suite.log`.
- `result-summary.md`: veredicto global **PASA** o **FALLA**, una línea por comprobación con su evidencia, y la lista de FAIL
  de la suite clasificados.

Responde en una línea: `TEST PASA: runs/subagents/test-pron-link-t1/result-summary.md` o `TEST FALLA: <motivo>`.
