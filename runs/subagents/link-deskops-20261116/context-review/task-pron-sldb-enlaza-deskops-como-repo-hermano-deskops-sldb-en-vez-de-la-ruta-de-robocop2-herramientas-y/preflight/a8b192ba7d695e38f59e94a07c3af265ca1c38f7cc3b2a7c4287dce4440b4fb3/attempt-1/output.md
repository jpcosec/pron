## REFORMULACION

Propósito: corregir en `pron` el enlace al store de deskops para que use el repo hermano `../deskops/.sldb` en vez de la ruta de robocop2 `../../../herramientas/deskops/.sldb`. Resultado: enlace actualizado mediante el CLI de sldb, `check.yml` clonando deskops en `../deskops` antes de `make check`, viñeta en `CHANGELOG.md` y evidencias V1–V8. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Límites: no editar a mano `.sldb/store.yaml` ni `.sldb/core/store_index.yaml`; no tocar rutas absolutas de modelos, tests fallidos, `src/`, `Makefile`, CI de sldb, checkout real ni hacer git add/commit/push. Si los comandos de sldb cambian algo más que la línea `path` y `store_hash`, el ejecutor para y reporta.

## AMBIGUEDADES

1. «Tampoco entran las fallas de tests de pron (goldens test_16, test_04 y test_10…)» frente a «make world PYTHON=python # rc 0». No se aclara si `make world` ejecuta esos tests; obligaría a inventar si V4 debe pasar pese a fallos ajenos o si basta con aislar el fallo del enlace.
2. «aparte de esa línea y de store_hash, solo puede haber entradas de documentos de desk/ o runs/ que escribe el coordinador». Si aparecen en el working tree, no se define cómo distinguirlas de cambios propios; obligaría a inventar un criterio de aceptación para V8.

## DRY-RUN

Lecturas: task, `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `.github/workflows/check.yml`, `CHANGELOG.md`; verificar venv. Cambios previstos: ejecutar `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write`; añadir paso de clonado en `check.yml`; añadir viñeta en `CHANGELOG.md`. Dependencias: venv con pron y sldb editables, acceso a GitHub para V4/V5, deskops disponible en robocop2. Validaciones futuras: V1–V8, incluida comprobación del layout CI, control negativo, estructura YAML y `git diff` limitado. No se ejecuta nada.

## FUTURO

El coordinador hará commit y push en master de pron y enviará a sldb el hash. sldb decidirá sobre las rutas absolutas de modelos. Un humano resolverá cualquier fallo de V4 atribuible a tests ajenos o a infraestructura.
