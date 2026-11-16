# Decisión: el store .sldb/ de pron se versiona

Opción elegida: A

Fecha del dispose de JP: 2026-11-16

## Razón

Copiada del reason del recibo owner
`review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-owner-2`:

> JP 2026-11-16 (transmitida por el supervisor). Se versionan .sldb/store.yaml y .sldb/core/;
> no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime), que sigue
> ignorada.

## Contexto

- sldb c420809c (2026-11-04) aplica la decisión del dueño del 2026-10-29: el store `.sldb/`
  (`store.yaml` + `core/`) se versiona y `.sldb_cache/` es la caché ignorada. El aviso llegó a pron
  en la nota del inbox
  `desk/inbox/20261104-233659-unclear-sldb-pron-ignora-sldb-entero-stores-check-falla-con-stores-core-ignored.md`.
- `.gitignore` de pron ignoraba `.sldb/` entero, bajo el comentario "pron's own world: make world
  rebuilds the store", porque `make world` regenera ahí el mundo de pron.
- Las opciones, tal como las describe el goal de la tarea de decisión:
  - **(A)** versionar `.sldb/` como el resto de los repos: quitar la línea `.sldb/` de `.gitignore`
    y commitear `store.yaml` y `core/`, mundo derivado incluido.
  - **(B)** separar stores: el mundo derivado de pron sale de `.sldb/` a otro store ignorado y
    `.sldb/` queda versionado solo con el desk (exige cambiar `pron init --world` y el Makefile).
  - **(C)** pron queda como excepción declarada: `.sldb/` sigue ignorado, `stores check` sigue en
    error y los recibos del desk no se versionan.

## Consecuencias de la opción A

- **`sldb stores check`:** deja de emitir `stores/core_ignored`.
- **Recibos y documentos del desk** (TaskCodeDoc, InboxNoteDoc, los ReviewDoc de los recibos
  preflight/bundle/owner): viajan en git, así que una tarea de pron puede activarse en otra máquina.
- **Costo:** se versionan unos 740 documentos derivados y regenerables de `.sldb/core/documents`,
  y aparecen sus diffs al correr `make world`.
- **Sigue ignorado:** `.sldb_cache/` (la parte runtime/caché del store).

## Implementación

Este documento no implementa nada. Los cambios (`.gitignore` y el commit de `.sldb/store.yaml` y
`.sldb/core/`) los hace la `task.code` de seguimiento
`task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada`
(`desk/tasks/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada.md`).
