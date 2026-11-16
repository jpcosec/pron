## REFORMULACION
Encargo: en el repo **pron**, modificar `.gitignore` para dejar de ignorar `.sldb/` y así versionar `.sldb/store.yaml` y todo `.sldb/core/`, manteniendo ignorada `.sldb_cache/`; añadir una viñeta en `CHANGELOG.md`; y verificar el árbol de trabajo sin indexar ni commitear. Resultado: store versionado, caché ignorada y `sldb stores check` sin `stores/core_ignored` ni `stores/cache_not_ignored`. Límites: no tocar `sldb/`, errores `store/model-unresolved`, `make world`, Makefile, `src/pron`, sldb ni `docs/decision-store-sldb.md`; no regenerar el mundo. El commit/push corresponde al coordinador.

## AMBIGUEDADES
1. “agregar al índice .sldb/store.yaml y .sldb/core/ completos” frente a “sin git add ni commit: el ejecutor no indexa nada”. Obliga a inventar si el ejecutor debe hacer `git add` o solo dejar los archivos visibles para que el coordinador los añada.
2. “git check-ignore -q .sldb/core/store_index.yaml” presupone que existe esa ruta concreta; el input solo garantiza “todo .sldb/core/” y “789 archivos”. Obliga a inventar el nombre de un archivo de validación.
3. “En master de pron” no aparece como comprobación de rama en Validation ni en el camino de ejecución. Obliga a inventar si el ejecutor debe verificar la rama actual.

## DRY-RUN
Lecturas: `.gitignore`, `CHANGELOG.md`, listado de `.sldb/` y estado git de `.sldb`. Cambios previstos: borrar la línea `.sldb/`; reescribir el comentario indicado; añadir la viñeta exacta bajo `## Sin publicar`. No haría `git add`, commit ni push. Dependencias: git, `sldb` CLI, existencia de `.sldb/store.yaml` y `.sldb/core/`, y archivo `store_index.yaml` para la comprobación. Validaciones futuras: los cuatro `git check-ignore`, el conteo de `stores/(core_ignored|cache_not_ignored)` y la comparación entre `git status --porcelain --untracked-files=all .sldb` y `find .sldb -type f`. Ninguna se ejecuta ahora.

## FUTURO
El coordinador indexa y commitea `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core` con `deskops closeout commit --paths`, y pushea. La task.decision escribe `docs/decision-store-sldb.md`. Los errores `store/model-unresolved` quedan para otro trabajo.
