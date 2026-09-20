# API de pron que se movió — mapa para los consumidores

Estado al **2026-09-20**. Esta tabla existe porque hay repos que importan módulos de pron que
ya no están, y venían rotos sin que nadie lo notara.

El refactor `4064a72` (**2026-09-17**, "una clase por archivo en cuatro ejes") movió la
superficie pública de pron. Ninguno de los consumidores se actualizó, así que **todos los
imports de la columna izquierda revientan hoy** con `ModuleNotFoundError` o `ImportError`.

## El mapa

| import que ya no existe | dónde vive ahora |
|---|---|
| `from pron.store import Store` | `from pron.world.store import Store` |
| `from pron.store import StoreError` | `from pron.world.store_error import StoreError` |
| `from pron.world import World` | `from pron.world.world import World` |
| `from pron.world import init_world` | `from pron.world.world_init import init_world` |
| `from pron.lexicon import Lexicon` | `from pron.world.lexicon import Lexicon` |
| `from pron.verbs import Verbs` | `from pron.world.lexicon_parts.verbs_for import Verbs` |
| `from pron.client import RemoteSession` | `from pron.remote.remote_session import RemoteSession` |
| `from pron.client import request, alive, socket_path` | `from pron.remote.client import request, alive, socket_path` |

No se movieron: `pron.session.Session` y `pron.serve` siguen donde estaban.

## Quién está roto hoy

| repo | qué importa | estado |
|---|---|---|
| `hum-ecosystem/tools/graph_ui` | `pron.store`, `pron.lexicon`, `pron.verbs`, `pron.world.World` | **roto** — la suite no colecciona (`No module named 'pron.store'`) |
| `legos` | `pron.client`, `pron.world.init_world`, `pron.world.World` | **roto** — `test_composition_documents` falla en collection |
| `legos-agentes-nodo` | lo mismo que legos | **roto** por los mismos imports |

Verificado el 2026-09-20: los tres fallan igual con y sin los cambios de la fusión sldb↔kgdb, o
sea que esto es independiente de la fusión y viene del 2026-09-17.

## Qué NO se decidió

Hay tres caminos y ninguno está tomado:

1. **Shims de compatibilidad en pron** — reponer `pron/store.py`, `pron/client.py`, etc. como
   re-exports. Barato, pero reintroduce los módulos que el refactor sacó a propósito.
2. **Actualizar los consumidores** — tres repos, imports de una línea cada uno. Es el camino
   limpio, pero toca repos que no son de pron.
3. **Dejarlo roto** — si esos consumidores ya no se mantienen, declararlo y no arrastrar el peso.

La decisión es del dueño de los repos, no de pron.

## Lo relacionado

- La fusión de kgdb dentro de sldb, que es otra cosa y esa sí quedó resuelta:
  [el ADR](../../hum-ecosystem/tools/sldb/docs/architecture/sldb-absorbs-kgdb.md) y el mapa en el
  README de kgdb.
