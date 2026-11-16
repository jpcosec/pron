## REFORMULACION
Propósito: ejecutar la opción A de JP: versionar `.sldb/store.yaml` y `.sldb/core/`, manteniendo `.sldb_cache/` ignorada. Resultado: en `master` de pron, el store es versionable y `sldb stores check` no emite `stores/core_ignored` ni `stores/cache_not_ignored`. Repo: pron. Límites: el ejecutor solo edita `.gitignore` (quita `.sldb/`, línea 10, y reescribe el comentario de la línea 9) y añade una viñeta en `CHANGELOG.md`; no indexa, commitea ni pushea. No toca `sldb/` (línea 11), `.sldb_cache/` (26), Makefile, `src/pron`, sldb, el mundo, ni `docs/decision-store-sldb.md`. Si aparece en `.sldb/` algo distinto de `store.yaml` o `core/`, para y reporta.

## AMBIGUEDADES
1. Cita: “el ejecutor para y lo reporta sin ignorarlo ni versionarlo”. Obliga a inventar el canal, formato y destinatario del reporte; no el hecho de parar.
2. Cita: “las seis comprobaciones de Validation pasan sobre el árbol de trabajo con solo .gitignore y CHANGELOG.md modificados”, frente a “cada archivo del store aparece como untracked (??)”. Obliga a decidir si “modificados” excluye los untracked de `.sldb` que la validación 6 espera.

## DRY-RUN
Lecturas: TaskDoc, `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml`, listado de `.sldb/` y estado git. Cambios previstos: en `.gitignore`, eliminar `.sldb/` y sustituir el comentario por el texto indicado; en `CHANGELOG.md`, añadir la viñeta exacta al final de la lista de “## Sin publicar”. Sin `git add`, commit ni push. Dependencias: task.decision cerrada con recibo owner-2; `.sldb/` contiene solo `store.yaml` y `core/`; `.sldb_cache/` sigue ignorada. Validaciones futuras: las seis órdenes de Validation; `stores check` puede salir rc 1 por `model-unresolved`, pero el `grep` debe imprimir 0; contar untracked de `.sldb` frente a `find`.

## FUTURO
El coordinador indexa y commitea `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core` con `deskops closeout commit --paths`, y pushea. La task.decision produce `docs/decision-store-sldb.md`. Los errores `store/model-unresolved` quedan fuera.
