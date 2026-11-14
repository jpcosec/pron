## REFORMULACION

Encargo `task.code` (ejecutable, no agregado): devolver pron a verde contra `sldb origin/main` tras el cambio de caché derivada de `.sldb/runtime/` a `.sldb_cache/`. Resultado: suite completa de a un archivo con 0 failed/0 errors, `grep -rn '.sldb/runtime' src tests` vacío y diffs de snapshots explicados. Repo: pron. Límites: no tocar sldb, no alterar comportamiento de pron salvo lo exigido, y `.gitignore` de `.sldb/` fuera de alcance.

## AMBIGUEDADES

1. «si sldb no expone la ruta, usar .sldb_cache/ con un helper único en tests» — obliga a inventar si la API de sldb existe y dónde vive el helper.
2. «test_16_golden_undo_why x2» — obliga a inventar qué dos casos concretos son.
3. «guardar la lista de fallos como línea base en runs/subagents/» — obliga a inventar nombre y formato del archivo.
4. «instalar sldb origin/main» — obliga a inventar el método de instalación (pip editable, ruta, versión).
5. «los snapshots ... que cambien por el sldb nuevo» — obliga a inventar el criterio exacto de "explicable" frente a cambio de significado.
6. CHANGELOG sin formato ni sección — obliga a inventar la convención de entrada.

## DRY-RUN

Lecturas previstas: TaskDoc, rituales `execution`, `testing` y `closeout`; Board y pills/átomos ligados (no incluidos en el cold-bundle); `tests/plnr/test_goal_stale_graph.py`, `tests/mcp_surface/test_14_mount.py`, `tests/golden/__snapshots__`, `CHANGELOG`.

Cambios previstos: sustituir rutas `.sldb/runtime/` por API de sldb o `.sldb_cache/`; actualizar lista `CACHE`; actualizar snapshots solo con diff explicado; entrada de CHANGELOG.

Dependencias: sldb origin/main instalado, pytest y plugin de snapshots, TMPDIR.

Validaciones futuras (no ejecutadas): las tres del TaskDoc más suite completa archivo por archivo. Parada si un diff implica cambio semántico de respuesta.

## FUTURO

Otro nodo ejecuta p1 (línea base de fallos) y p3 (diffs de snapshots); un humano decide la política de `.gitignore` y aprueba/descarta actualizaciones con cambio de significado; closeout actualiza board, ata conocimiento a átomos y prepara el commit; la fase integra y valida el conjunto.
