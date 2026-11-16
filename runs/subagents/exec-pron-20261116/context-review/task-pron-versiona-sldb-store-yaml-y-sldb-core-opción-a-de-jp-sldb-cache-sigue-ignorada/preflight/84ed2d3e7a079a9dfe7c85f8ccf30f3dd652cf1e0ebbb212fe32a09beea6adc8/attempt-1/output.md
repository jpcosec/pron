## REFORMULACION

Encargo ejecutable (task.code) en el repo `pron`, rama master. Propósito: versionar `.sldb/store.yaml` y todo `.sldb/core/`, manteniendo `.sldb_cache/` ignorada, para que `sldb stores check` deje de emitir `stores/core_ignored` y `stores/cache_not_ignored` y los documentos del desk viajen en un clon. Resultado: `.gitignore` sin la línea `.sldb/` (comentario reescrito), viñeta en `CHANGELOG.md`, y las seis comprobaciones de Validation pasando sobre el árbol de trabajo; el coordinador commitea y pushea después. Límites: solo se modifican `.gitignore` y `CHANGELOG.md`; el ejecutor no hace `git add`/commit; no se toca la línea `sldb/`, ni los errores `model-unresolved`, ni `make world`, Makefile, `src/pron`, `sldb`, ni `docs/decision-store-sldb.md`.

## AMBIGUEDADES

1. "borrar la línea '.sldb/' (línea 10) y reescribir el comentario de la línea 9" — obligaría a inventar qué hacer si los números de línea no coinciden con ese contenido.
2. "al final de la lista bajo '## Sin publicar'" — obligaría a inventar qué lista si hay varias o el encabezado difiere.
3. "todo .sldb/core/ están versionados" — obligaría a decidir si incluye recursivamente subdirectorios y dotfiles.
4. "si al ejecutar aparece en .sldb/ algo que no sea store.yaml ni core/, el ejecutor para y lo reporta" — obligaría a inventar el canal y formato del reporte.
5. "test $(git status --porcelain --untracked-files=all .sldb | wc -l) -eq $(find .sldb -type f | wc -l)" — obligaría a decidir el tratamiento de symlinks (find no cuenta `-type f` igual que git).
6. "grep -cE 'stores/(core_ignored|cache_not_ignored)' ... pasa si imprime 0" — obligaría a decidir si un fallo previo de `stores check` que no imprima nada cuenta como éxito.

## DRY-RUN

Lecturas: `.gitignore`, `CHANGELOG.md`, `git branch --show-current`, listado de `.sldb` (`ls`/`find`) para confirmar solo `store.yaml` y `core/`. Cambios previstos: borrar `.sldb/`, reescribir el comentario con el texto indicado, añadir la viñeta. Dependencias: decisión de JP ya tomada, rama master, CLI `sldb` disponible, estado de `.sldb` sin elementos runtime. Validaciones futuras: las seis de Validation. Nada ejecutado.

## FUTURO

El coordinador indexa y commitea `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core` con `deskops closeout commit --paths`, pushea, y verifica `git ls-files .sldb | wc -l`. La task.decision escribe `docs/decision-store-sldb.md`. El owner valida el cierre.
