## REFORMULACION
Nodo ejecutable de código (no agregado), en el repo `pron`, rama `master`. Propósito: versionar `.sldb/store.yaml` y todo `.sldb/core/` para que el store viaje en un clon, manteniendo `.sldb_cache/` ignorada y dejando constancia en `CHANGELOG.md`. Resultado: `sldb stores check` deja de emitir `stores/core_ignored` y `stores/cache_not_ignored`; el resto de errores (`model-unresolved`) queda fuera. Límites: el ejecutor solo modifica `.gitignore` (quita `.sldb/`, reescribe su comentario) y una viñeta de `CHANGELOG.md`; no indexa ni commitea. No toca `sldb/`, `make world`, `Makefile`, `src/pron`, `sldb`, docs ni el mundo. Si en `.sldb/` aparece algo distinto de `store.yaml` o `core/`, para y reporta.

## AMBIGUEDADES
1. “no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime)”: “lo que sea runtime” no está definido; obligaría a inventar qué rutas cuentan como runtime si aparecen. El Scope lo acota: parar y reportar.
2. “el ejecutor para y lo reporta sin ignorarlo ni versionarlo”: no indica formato ni destino del reporte; obligaría a inventar el canal.
3. “store_index.yaml existe en .sldb/core (verificado 2026-11-16)”: el input no incluye el listado; obligaría a asumir que sigue existiendo, aunque la propia validación lo comprueba.

## DRY-RUN
Lecturas: `desk/tasks/task-...md`, `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml`, listado de `.sldb/` y `.sldb/core/`, `git branch --show-current`, `git status`. Cambios previstos: borrar la línea `.sldb/`; sustituir el comentario de la línea 9 por el texto indicado; añadir al final de `## Sin publicar` la viñeta indicada. Dependencias: decisión de JP ya tomada, rama `master`, `sldb` disponible, `.sldb_cache/` existente e ignorada. Validaciones futuras: las seis comprobaciones del TaskDoc sobre el árbol de trabajo, sin `git add` ni commit. El cierre del coordinador verifica que `git ls-files .sldb` iguala `find .sldb -type f`.

## FUTURO
El coordinador indexa y commitea `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core` con `deskops closeout commit --paths` en `master`, y pushea. Después se comprueba el resultado conjunto: store versionado, caché ignorada y `stores check` sin los dos errores citados.
