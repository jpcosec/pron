REFORMULACION
Encargo ejecutable (`task.code`, no agregado ni paquete): en el repo `pron` (`/mnt/ssd/proyectos/SLDB_1/pron`), reenlazar el store de deskops de `../../../herramientas/deskops/.sldb` a `../deskops/.sldb` usando el CLI de sldb, sin editar a mano los YAML. Además, en `.github/workflows/check.yml`, insertar entre `Install` y `check (...)` un paso que clone `https://github.com/jpcosec/opsys.git` en `../deskops`, y añadir una viñeta bajo `## Sin publicar` de `CHANGELOG.md`. Resultado observable: V1–V8 pasan y solo cambian `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `.github/workflows/check.yml` y `CHANGELOG.md`. Límites: no tocar rutas absolutas de modelos, tests, `src/`, `Makefile`, CI de sldb, ni hacer git add/commit/push; si los comandos de sldb alteran algo más que la línea `path` del enlace y `store_hash`, parar y reportar.

AMBIGUEDADES
Ninguna.

DRY-RUN
Un ejecutor leería el TaskDoc, sus referencias, ambos archivos `.sldb`, `check.yml` y `CHANGELOG.md`; verificaría el árbol limpio en esas rutas. Después, desde la raíz de pron, usaría el venv indicado (recreándolo si falta) y ejecutaría `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write`. Editaría el YAML del workflow y el CHANGELOG según p2/p3. Dependencias: sldb editable, red para clonar en V4 y tiempo suficiente. Validaría V1–V8, incluida la resolución de `linked_store`, ausencia de `herramientas`, layout CI con clone, control negativo, orden de pasos y diff acotado; guardaría evidencia en el run dir. Ante un diff fuera de lo previsto, se detendría.

FUTURO
El coordinador hará commit/push en master y enviará el hash a sldb; sldb atiende las rutas absolutas de modelos. Las fallas de tests pertenecen a otra tarea.
