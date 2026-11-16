## REFORMULACION

**Propósito:** versionar en pron el store de sldb (opción A decidida por JP) para que los documentos del desk viajen en un clon y `sldb stores check` deje de reportar `stores/core_ignored` y `stores/cache_not_ignored`.
**Resultado:** `.gitignore` sin la línea `.sldb/`, `.sldb/store.yaml` y `.sldb/core/` completos versionados, `.sldb_cache/` aún ignorada, viñeta en `CHANGELOG.md` y commit en master pusheado.
**Repo:** pron, rama master (`/mnt/ssd/proyectos/SLDB_1/pron`).
**Límites:** no tocar la línea `sldb/` ni `.sldb_cache/`, ni Makefile, `make world`, `src/pron`, sldb; no arreglar `store/model-unresolved`; no escribir `docs/decision-store-sldb.md`; el ejecutor no indexa ni commitea.

## AMBIGUEDADES

1. «el ejecutor no indexa nada; el coordinador commitea .gitignore, CHANGELOG.md, .sldb/store.yaml y .sldb/core con deskops closeout commit --paths» frente a «En master de pron, .sldb/store.yaml y todo .sldb/core/ están versionados» y «git ls-files .sldb cuenta lo mismo que find .sldb -type f». Obliga a inventar quién indexa y en qué momento se satisface Done When; el ejecutor no puede verificar `git ls-files`.
2. «test $(git status --porcelain --untracked-files=all .sldb | wc -l) -eq $(find .sldb -type f | wc -l)   # git ve cada archivo del store». Sin `git add`, git status lista untracked, no versionados; obliga a inventar si «ve» significa untracked y si el conteo contempla symlinks o archivos ya rastreados.
3. «... | grep -cE 'stores/(core_ignored|cache_not_ignored)'   # imprime 0» junto a «los errores store/model-unresolved de stores check ... es otro problema». `grep -c` sale con estado 1 sin coincidencias y el check puede fallar por model-unresolved; obliga a inventar si el criterio es el texto «0» o el exit code.
4. «no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime)». «lo que sea runtime» no está enumerado; obliga a inventar qué rutas además de `.sldb_cache/` quedan fuera.

## DRY-RUN

**Lecturas:** `.gitignore` (líneas 9–11 y 26), `CHANGELOG.md` («## Sin publicar»), `.sldb/store.yaml`, inventario de `.sldb/core` (789 archivos), `nada del store` modificado.
**Cambios previstos:** p1 borrar `.sldb/` y reescribir el comentario de la línea 9; p2 añadir la viñeta al CHANGELOG; p3 ejecutar las comprobaciones sin `git add` ni commit.
**Dependencias:** sldb CLI con `--pythonpath .`, git, `make world` sin ejecutar, decisión de JP ya tomada.
**Validaciones futuras:** los cinco comandos del TaskDoc; vigilar el exit code de `grep -c` y los `store/model-unresolved` residuales; confirmar `.sldb_cache/` ignorada y conteo de archivos.

## FUTURO

El coordinador indexa y commitea (`.gitignore`, `CHANGELOG.md`, `.sldb/store.yaml`, `.sldb/core/`) y pushea a master. La task.decisión redacta `docs/decision-store-sldb.md`. Resolver `store/model-unresolved` queda para otro nodo o humano.
