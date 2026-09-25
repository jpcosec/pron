# Changelog

## Sin publicar

- `pron serve --listen HOST:PORT`: el daemon atiende además por TCP, con el mismo
  protocolo, a un cliente que no comparte su sistema de archivos (spec 12 §7).
  `request`, `alive`, `RemoteSession`, `RemoteGraph` y `RemoteWorld` aceptan `HOST:PORT`
  donde iba la ruta del socket; `pron.remote.tcp_address` dice cuál es
  (`tests/remote/test_07_serve_tcp.py`).

## 1.0.0 — 2026-09-10

First tagged release. pron exists by its own right: SHRDLU over an sldb store whose
nouns are addresses and whose verbs are kgdb relation types plus sldb writes.

### Surface (frozen by spec 12 and `tests/test_12_runtime_surface.py`)

- `Session(world, projection, speaker, speaker_address, now, embedder, read_only, home)`
  and `turn(sentence) -> Response`.
- `pron.response.Response` with five fields: `text`, `outcome`, `trace`, `move_id`, `record`.
- `pron.client`: `socket_path`, `alive`, `request`, `RemoteSession(sock, ...)` with
  `world`/`home` and `payload(model, doc)`, `RemoteGraph`, `RemoteWorld`.
- Socket at `<world>/.pron/serve.sock`; `pron say`, `pron repl` and hosts use it when it
  answers.
- `World.store.payload(model, doc)`; export ids qualified by store (`A:Model:doc`), split
  and joined by `pron.ids` (`split_id`, `join_id`, `store_of`, `scope`, `address_of`).

### Since 1.0.0.dev1

- Composition validation: `$created`-before-`create` prevalidated in both the live and the
  dry-run paths (`tests/test_composition_validation.py`).
- Self-KB hole closed: docs are discovered by walking the package, so every module —
  including `models/*` — is checked to cite a spec chapter.
- Revision lock for sibling dependencies (`constraints.txt`) and CI running `make check`.
- Spec 12 updated to match the shipped signatures; runtime-surface freeze test added.
- Architecture catalog no longer describes the abandoned AtomDoc/deskops models.
- Makefile (`make check`), mypy hardening, dev extras pinned.
