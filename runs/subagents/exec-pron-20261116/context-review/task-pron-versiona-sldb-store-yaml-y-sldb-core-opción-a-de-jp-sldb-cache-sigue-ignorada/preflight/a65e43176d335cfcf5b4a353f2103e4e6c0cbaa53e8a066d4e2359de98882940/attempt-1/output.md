## REFORMULACION

Encargo ejecutable (`task.code`), no agregado. Propósito: implementar la opción A de JP (2026-11-16) en el repo pron: versionar `.sldb/store.yaml` y `.sldb/core/` y mantener `.sldb_cache/` ignorada. Resultado: en master, `.gitignore` deja de ignorar `.sldb/` entero, el store queda versionado y `sldb stores check` no emite `stores/core_ignored` ni `stores/cache_not_ignored`. Límites: el ejecutor solo modifica `.gitignore` (quita `.sldb/`, reescribe el comentario) y añade una viñeta en `CHANGELOG.md` bajo `## Sin publicar`; no hace `git add` ni commit. Fuera: la línea `sldb/`, `model-unresolved`, `make world`, Makefile, `src/pron`, `sldb`, regenerar el mundo y `docs/decision-store-sldb.md`. El commit y push son del coordinador en el cierre con `deskops closeout commit --paths`.

## AMBIGUEDADES

1. "git branch --show-current   # imprime master": no dice qué hacer si la rama no es master; obligaría a inventar si parar, cambiar o reportar.
2. "con solo .gitignore y CHANGELOG.md modificados": no aclara si los untracked de `.sldb` cuentan como modificados, aunque la última validación exige que aparezcan como untracked; obligaría a decidir esa lectura.
3. "al final de la lista bajo '## Sin publicar'": no concreta el formato de la lista; obligaría a inferir el punto exacto de inserción.

## DRY-RUN

Lecturas: `.gitignore` (líneas 9-11 y 26), `## Sin publicar` de `CHANGELOG.md`, listado de `.sldb/` para confirmar solo `store.yaml` y `core/`, y `docs/decision-store-sldb.md`. Cambios previstos: borrar `.sldb/`, reescribir el comentario de la línea 9 con el texto indicado y añadir la viñeta exacta al final de la lista. Sin `git add` ni commit. Dependencias: master, `.sldb/store.yaml` y `.sldb/core/store_index.yaml` presentes, `.sldb_cache/` presente e ignorada, CLI `sldb` y `deskops` disponibles. Validaciones futuras: las seis comprobaciones de Validation en el árbol de trabajo; luego el coordinador indexa y commitea `.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml` y `.sldb/core` con `deskops closeout commit --paths`, pushea y verifica `git ls-files .sldb | wc -l` = `find .sldb -type f | wc -l`. Si aparece algo distinto de `store.yaml` o `core/` en `.sldb/`, el ejecutor para y reporta.

## FUTURO

El coordinador hace el closeout commit y push, y valida el recuento tras el commit. JP ya decidió la opción A; la `task.decision` escribe `docs/decision-store-sldb.md`. Contenido inesperado en `.sldb/` se reporta para decisión humana. El push en master cierra la tarea.
