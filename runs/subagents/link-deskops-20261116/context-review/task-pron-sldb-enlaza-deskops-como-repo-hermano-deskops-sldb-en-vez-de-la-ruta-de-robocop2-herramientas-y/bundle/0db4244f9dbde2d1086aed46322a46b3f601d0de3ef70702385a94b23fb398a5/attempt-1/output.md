REFORMULACION
Propósito: que pron enlace el store de deskops como repo hermano `../deskops/.sldb` en vez de la ruta de robocop2 `../../../herramientas/deskops/.sldb`, y que su CI clone jpcosec/opsys en `../deskops`. Resultado: path corregido en `.sldb/store.yaml` y `.sldb/core/store_index.yaml` (vía CLI sldb, no a mano), paso nuevo en `.github/workflows/check.yml` y viñeta en `CHANGELOG.md`; V1-V8 en verde y solo esos cuatro archivos tocados. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`; nodo ejecutable (`task.code`), no agregado. Límites: no tocar modelos de paquete ni `store_hash`, no `git add/commit/push`, no arreglar tests; ante desvío, parar y reportar `BLOQUEADO`.

AMBIGUEDADES
1. Cita: «El coordinador lo probó el 2026-11-17 en una copia de HEAD: los dos comandos cambian solo .sldb/store.yaml y .sldb/core/store_index.yaml». El cold-bundle no incluye `.sldb/store.yaml` (sí `store_index.yaml`); obligaría a inventar su contenido base y la forma exacta de la línea del enlace para decidir qué cuenta como desvío.
2. Cita: «su paso docs-check (make world)». El `Makefile` no está en el bundle; obligaría a inventar que el target `check` ejecuta `world`/docs.
3. Cita: «con el comentario '# .sldb/store.yaml links deskops as ../deskops/.sldb (sibling checkout)'». No fija si el comentario va sobre el ítem YAML o dentro de `run`; V7 no lo comprueba.

DRY-RUN
Lecturas: `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `.github/workflows/check.yml`, `CHANGELOG.md`, `Makefile:29-32`, `git status --porcelain -- . ':!runs'` y la comprobación del venv. Cambios previstos: p0 árbol limpio y venv (recrear si falla); p1 `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write` desde la raíz de pron con `TMPDIR=/dev/shm`; p2 insertar el paso de clone entre Install y check; p3 viñeta bajo «Sin publicar»; p4 correr V1-V8 y guardar evidencia. Dependencias: sldb editable en `/mnt/ssd/proyectos/SLDB_1/sldb`, `pron[dev,mcp]`, `uv`, red para los clones de V4/V6, timeout de 40 min. Validaciones futuras: V1 lista, V2 grep, V3 `linked_store`, V4 `make world` en layout CI, V5 `pron docs`, V6 control con HEAD, V7 YAML de steps, V8 diff acotado. Paradas: archivo o línea extra, Makefile distinto, precondición fallida → `BLOQUEADO`.

FUTURO
El coordinador hace commit en master de pron, push y envía nota a sldb con el hash; sldb atiende aparte las rutas absolutas de modelos de paquete; otra tarea (`task-pron-vuelve-a-verde-…`) arregla test_16/test_04/test_10.
