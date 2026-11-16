## REFORMULACION

Nodo ejecutable `task.code` en el repo **pron**. **Propósito:** eliminar la única dependencia de spec2viz migrando las tres llamadas `run('spec2viz', ...)` de `docs/spec2viz/build.py` (líneas 22-24) a `specir`, con los mismos argumentos. **Resultado:** `build.py` valida, renderiza y construye el catálogo con `specir`; `python3 docs/spec2viz/build.py` termina con rc 0; se actualizan docstrings, README y CHANGELOG; se commitea y pushea en `master`; se envía a IR el hash por `deskops message send`. **Límites:** no renombrar `docs/spec2viz`, no regenerar/commitear salidas ignoradas, no tocar IR/spec2viz/sldb, no desinstalar spec2viz, no resolver la política de `.gitignore` de `.sldb/`.

## AMBIGUEDADES

1. “instalar specir en la máquina como herramienta de uv” frente a la validación con `/mnt/ssd/proyectos/SLDB_1/IR/.venv/bin/specir`: el input no dice qué hacer si ese binario del venv no existe o no corresponde a la herramienta uv instalada. Obligaría a inventar si basta `uv tool install`, si hay que instalar/crear el venv de IR o si se puede omitir ese chequeo.

## DRY-RUN

**Lecturas previstas:** `docs/spec2viz/build.py`, `docs/spec2viz/README.md`, `CHANGELOG.md`, la nota de inbox y las referencias de IR; `uv tool list`; ayudas de `specir diagram validate/render` y `specir catalog build`; estado git y remoto.

**Cambios previstos:** sustituir `'spec2viz'` por `'specir'` en las tres llamadas de las líneas 22-24; reemplazar los dos docstrings por los textos exactos indicados; cambiar comandos y “CLI de spec2viz” en README; añadir la viñeta indicada en CHANGELOG.

**Dependencias:** disponibilidad de `/mnt/ssd/proyectos/SLDB_1/IR`, instalación de `specir`, que las opciones `--backend`, `--out`, `--config` existan, `deskops` operativo y permiso de push a `origin`.

**Validaciones futuras:** `grep` sin coincidencias de `run('spec2viz'`; ejecución de `build.py` con rc 0 y salidas esperadas; `specir retirement check` sin fila `pron`; commit/push en `master`; mensaje a IR con el hash.

## FUTURO

IR recibe el mensaje y decide cuándo actualizar `acta-de-retiro.md` y cerrar G4. Un humano decide si desinstala spec2viz. Otra tarea decide la política de `.gitignore` de `.sldb/`.
