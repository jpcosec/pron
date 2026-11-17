REFORMULACION
Nodo ejecutable `task.code`, no agregado. Propósito: corregir en `pron` el enlace al store de `deskops`, hoy apuntando a `../../../herramientas/deskops/.sldb`, y hacer que su CI tenga `deskops` al lado. Resultado: `../deskops/.sldb` en `.sldb/store.yaml` y `.sldb/core/store_index.yaml`, un paso de clonado en `.github/workflows/check.yml` y una viñeta en `CHANGELOG.md`. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Límites: usar el CLI de sldb, no editar a mano los stores; no tocar rutas absolutas de modelos de sldb, tests, `src/`, `Makefile` ni el CI de sldb; no hacer `git add`, commit ni push; parar y reportar ante cambios extra.

AMBIGUEDADES
1. “`git diff HEAD -- .sldb/store.yaml` cambia solo la línea path del enlace deskops”: el cold-bundle no incluye el contenido de `.sldb/store.yaml`. Obliga a inventar la línea actual y el diff esperado; el ejecutor tendría que leerlo del repo.
2. “`Makefile:29-32; el ejecutor lo comprueba con sed -n 29,32p Makefile`”: tampoco se aporta `Makefile`. Obliga a inventar el contenido exacto del target `world`; V4 solo ordena comprobarlo y parar si no coincide.

DRY-RUN
Lecturas: TaskDoc, rituales, `.sldb/core/store_index.yaml`, `check.yml`, `CHANGELOG.md`; además `.sldb/store.yaml`, `Makefile`, `git status/diff` y la salida de `sldb`. Cambios previstos: p0 comprobar árbol limpio y venv; p1 ejecutar `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write`; p2 insertar el paso `deskops next to pron` tras `Install`; p3 añadir la viñeta antes de `## 1.0.0`; p4 ejecutar V1–V8 y dejar evidencia en el run dir. Dependencias: sldb, uv, Python 3.12, git/red para clonar `jpcosec/opsys`, `/dev/shm` y `make world` (más de 10 minutos). Validaciones futuras: V1 `stores list`; V2 ausencia de `herramientas/deskops`; V3 `linked_store`; V4/V5 layout CI con caché fría; V6 control con HEAD; V7 orden del YAML; V8 diff limitado a cuatro archivos. Cualquier desvío detiene y se reporta.

FUTURO
El coordinador commiteará y pusheará los cuatro archivos y enviará la nota a sldb con el hash. sldb atenderá las rutas absolutas de modelos; otra tarea resolverá los tests `test_16`, `test_04` y `test_10`. El humano/coordinador cierra el run.
