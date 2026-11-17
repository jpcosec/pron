REFORMULACION
Propósito: que pron enlace el store de deskops como repo hermano (`../deskops/.sldb`) y no por la ruta de robocop2, para que `pron docs`/`make world` resuelvan en el CI de sldb y en el propio. Resultado: `.sldb/store.yaml` y `.sldb/core/store_index.yaml` con el enlace nuevo (vía `sldb stores add/declare`), un paso de clonado en `.github/workflows/check.yml` y una viñeta en `CHANGELOG.md`. Repo: `/mnt/ssd/proyectos/SLDB_1/pron` (robocop2), con deskops en `/mnt/ssd/proyectos/SLDB_1/deskops`. Límites: no toca `src/`, Makefile, tests, CI de sldb, rutas absolutas de modelos ni git add/commit/push; si aparecen otros cambios, para y reporta. Es una tarea ejecutable (task.code), no un agregado.

AMBIGUEDADES
1. “recrea con: uv venv -p 3.12 /dev/shm/pron-venv && VIRTUAL_ENV=/dev/shm/pron-venv uv pip install -e /mnt/ssd/proyectos/SLDB_1/sldb -e '.[dev,mcp]'):” — paréntesis suelto y extras relativos; obligaría a inventar si `[dev,mcp]` aplica a sldb o a pron.
2. “make world no corre tests: son las tres líneas del target world del Makefile, en references” — el Makefile no está en el bundle; obligaría a inventar el contenido del target.
3. “el coordinador commitea el desk antes del despacho y no escribe en desk/ ni en .sldb/ mientras trabaja el ejecutor” — el ejecutor no puede verificar esa precondición; obligaría a asumir un árbol limpio.
4. “check.yml clona jpcosec/opsys (repo público de deskops) en ../deskops antes de make check” — no fija el layout de Actions; obligaría a asumir dónde queda `$GITHUB_WORKSPACE`.

DRY-RUN
Lecturas: TaskDoc, rituales, `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `check.yml`, `CHANGELOG.md` y, en ejecución real, `Makefile`. Cambios previstos: dos líneas `path` más `store_hash`; paso “deskops next to pron” entre `Install` y `check`; viñeta bajo “Sin publicar”. Dependencias: venv `/dev/shm/pron-venv`, sldb editable y red para `git clone` en V4/V6. Validaciones futuras: V1-V8, con V4/V6 sobre copias temporales (timeout 40 min). Nada de esto se ejecuta aquí.

FUTURO
Coordinador: commit y push en master de pron, nota a sldb con el hash; nota aparte a sldb por las rutas absolutas de modelos; las fallas de tests (test_16, test_04, test_10) pertenecen a otra tarea.
