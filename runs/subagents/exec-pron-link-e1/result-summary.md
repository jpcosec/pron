# Resultado: exec-pron-link-e1

## Cambios

- p0: `git status --porcelain -- . ':!runs'` mostró solo `?? .deskops.log`, que según el brief cumple la precondición. El venv `/dev/shm/pron-venv` pasó la comprobación (pron y sldb resuelven a `SLDB_1/{pron,sldb}/src`) y no se recreó.
- p1: corrí `sldb stores add ../deskops/.sldb --name deskops --replace` (rc 0) y luego `sldb stores declare --write` (rc 0). Cada uno cambió solo la línea `path:` del enlace deskops en `.sldb/core/store_index.yaml` y en `.sldb/store.yaml`. El valor pasó de `../../../herramientas/deskops/.sldb` a `../deskops/.sldb`. No cambió ningún otro archivo de `.sldb/`. Tampoco cambió la línea `store_hash`, algo que el contrato permite.
- p2: agregué a `.github/workflows/check.yml` el paso `deskops next to pron` con su comentario y `git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops`, entre `Install` y `check (...)`.
- p3: agregué la viñeta en `CHANGELOG.md` al final de `## Sin publicar`, justo antes de `## 1.0.0 — 2026-09-10`.

## Validación (detalle en validation.log)

| V | Resultado | Evidencia |
|---|---|---|
| V1 | PASA | `- deskops -> ../deskops/.sldb`, rc 0 |
| V2 | PASA | sin salida, rc 1 |
| V3 | PASA | `/mnt/ssd/proyectos/SLDB_1/deskops/.sldb`, rc 0 |
| V4 | PASA | `make world` rc 0, sin `No store_index`, Traceback ni Error (v4-world.log). Makefile:29-32 coincide con el texto del TaskDoc |
| V5 | PASA | `pron docs` rc 0, cero `No store_index.yaml` (v5-docs.log) |
| V6 | PASA | `make world` rc 2 (make Error 1), `FileNotFoundError: No store_index.yaml at /dev/herramientas/deskops/.sldb` (v6-control.log) |
| V7 | PASA | rc 0 |
| V8 | PASA | diff --stat: solo los 4 archivos de Files. Los diffs de store.yaml y store_index.yaml cambian solo la línea path de deskops |

## Desvíos o dudas

- V6: el TaskDoc preveía que la ruta vieja resolviera a `/herramientas`. Como la copia está en `/dev/shm/<W>/pron`, `../../../` sube a `/dev`, y el error cita `/dev/herramientas/deskops/.sldb`. La ruta contiene `herramientas/deskops/.sldb`, que es lo que exige el criterio, así que V6 pasa. La conclusión no cambia: la ruta vieja no resuelve fuera de robocop2.
- V4 y V6 corrieron en paralelo, en segundo plano, con `timeout 2400`.
- Borré `/dev/shm/pron-link-ci` y `/dev/shm/pron-link-ci-control`. `/dev/shm/pron-venv` sigue intacto.
- `.deskops.log` sigue untracked y no lo toqué.
