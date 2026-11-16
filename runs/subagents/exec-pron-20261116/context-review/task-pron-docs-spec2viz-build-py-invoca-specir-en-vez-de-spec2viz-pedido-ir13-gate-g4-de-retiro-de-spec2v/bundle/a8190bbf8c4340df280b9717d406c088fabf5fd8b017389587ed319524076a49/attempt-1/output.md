## REFORMULACION

**Propósito:** eliminar la única dependencia de pron con spec2viz (IR13, gate G4 de retiro): las tres llamadas `run('spec2viz', ...)` de `docs/spec2viz/build.py`.

**Resultado:** `build.py` invoca `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos; docstrings, README y CHANGELOG actualizados; `specir` instalado como herramienta uv; las tres validaciones en verde; commit en `master` pusheado a origin; mensaje a IR con ese hash.

**Repo:** pron. Superficie: `docs/spec2viz/build.py`, `docs/spec2viz/README.md`, `CHANGELOG.md`.

**Límites:** no renombrar `docs/spec2viz`, sus specs ni `catalog.yml`; no regenerar ni commitear salidas ignoradas; no tocar IR, spec2viz ni sldb; no desinstalar spec2viz; no abordar la política de `.gitignore` de `.sldb/`.

## AMBIGUEDADES

1. «con `spec2viz`, `mmdc`, Python y PyYAML disponibles» y «reemplazar el comando spec2viz por specir»: no precisa si la frase queda «con `specir`» o «con el CLI `specir`»; forzaría inventar la redacción exacta.
2. «Las líneas citadas son las de master al crear la tarea; si cambiaron, ubicar cada cambio por el texto citado»: no aclara si esa regla vale también para README y CHANGELOG o solo para `build.py`; forzaría inventar el criterio de localización si las líneas difieren.

## DRY-RUN

**Lecturas:** TaskDoc, `docs/spec2viz/build.py`, `docs/spec2viz/README.md`, `CHANGELOG.md`; las referencias de IR no vienen en el bundle.

**Cambios previstos:** p1 instalar/reinstalar specir editable desde IR y comprobar los tres `--help`; p2 sustituir el primer argumento en las tres `run()` y actualizar los dos docstrings; p3 sustituir el comando en README y el rótulo «CLI de spec2viz»; p4 añadir la viñeta en CHANGELOG; p5 ejecutar las tres validaciones y, si pasan, commit y push; p6 enviar el mensaje a IR con el hash.

**Dependencias:** `uv`, fuente de IR, `python3`, `mmdc`, PyYAML, git con remoto y `deskops`.

**Validaciones futuras:** las tres del TaskDoc, en orden: grep sin salida; `build.py` con rc 0; `specir retirement check` sin fila `pron`.

## FUTURO

IR recibe el hash, actualiza su `acta-de-retiro.md` y decide el cierre de G4; la desinstalación de spec2viz y la revisión del commit quedan fuera de este nodo.
