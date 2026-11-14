## REFORMULACION

Encargo ejecutable `task.code` en el repo **pron**: devolver el CI a verde contra `sldb origin/main`. El resultado es la suite completa de pron ejecutada archivo por archivo con 0 failed/0 errors, sin rutas de caché `.sldb/runtime/` en `src` ni `tests`, y snapshots golden actualizados solo tras revisar su diff. Alcance: `tests/plnr/test_goal_stale_graph.py`, cualquier test/módulo que construya rutas de caché a mano, `tests/mcp_surface/test_14_mount.py`, snapshots afectados y `CHANGELOG`. Límites: no modificar sldb, no cambiar comportamiento de pron salvo lo exigido por sldb, no tocar la política de `.gitignore` de `.sldb/`.

## AMBIGUIDADES

1. «cualquier otro test o módulo de src/ que arme rutas ... a mano»: no define criterio de descubrimiento ni si incluye rutas indirectas; obligaría a inventar el universo exacto de archivos.
2. «si sldb no expone la ruta, usar .sldb_cache/ con un helper único en tests»: no dice nombre, ubicación ni si `src/` puede usar ese helper; obligaría a inventar su API y alcance.
3. «solo si el diff se explica por el sldb nuevo (orden, textos de sldb, rutas)»: no fija umbral entre cambio aceptable y cambio semántico; obligaría a inventar el criterio de revisión.
4. «suite completa de pron de a un archivo»: no especifica comando, orden ni selección; obligaría a inventar la invocación.
5. «instalar sldb origin/main»: no indica método, entorno ni pin; obligaría a inventar el procedimiento de instalación.
6. «test_16_golden_undo_why x2»: no identifica cuáles dos casos/snapshots; obligaría a inventarlos.
7. Entrada de `CHANGELOG`: sin formato ni contenido esperado; obligaría a inventar ambos.

## DRY-RUN

Lecturas previstas: TaskDoc, tests citados, `tests/golden/__snapshots__`, grep de `runtime` en `src/tests`, `CHANGELOG` y baseline en `runs/subagents/`. Cambios previstos: sustituir rutas manuales por API de sldb o `.sldb_cache/`; ajustar lista CACHE; actualizar snapshots solo con diff explicado; añadir CHANGELOG. Dependencias: sldb `origin/main` instalado y `TMPDIR=/tmp`. Validaciones futuras: pytest de `test_goal_stale_graph.py`, `tests/golden`, grep vacío y suite completa archivo por archivo. No se ejecuta nada.

## FUTURO

Un humano revisa los diffs de snapshots y aprueba la actualización; el CI/merge decide el verde final; el dueño decide `.gitignore`; sldb determina si expone o no la ruta de caché.
