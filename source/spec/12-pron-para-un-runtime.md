# 12 · pron para un runtime externo

Lo que un runtime que monta pron sobre un mundo puede usar, qué le promete cada pieza y qué no. Un runtime es cualquier proceso que no es la CLI de pron: un agente, un editor, un servidor. Kinesis es el primero; este documento es el contrato con cualquiera.

Regla general: un runtime usa lo que está acá y nada más. Lo que no está nombrado es interior de pron y cambia sin aviso.

## 1. Dos formas de hablar con un mundo

**En proceso.** El runtime importa `pron` y abre el mundo. Paga los imports de sldb una vez por proceso, y desde ahí un turno cuesta lo de una sesión caliente (11 §8 da los números).

```python
from pron.world import World
from pron.session import Session

world = World(root, pythonpath)                    # root contiene .sldb
session = Session(world, projection="all", speaker="agent.zero/run-1", now="2026-09-09", read_only=True)
response = session.turn("the reservations of Ana for Friday")
```

**Por socket.** Hay un `pron serve` escuchando en el mundo (11 §8). El runtime importa solo `pron.client`, que es biblioteca estándar, y no paga nada de sldb.

```python
from pron.client import socket_path, alive, RemoteSession

sock = socket_path(root)
if alive(sock):
    session = RemoteSession(sock, projection="all", speaker="agent.zero/run-1", now="2026-09-09", read_only=True)
```

Las dos devuelven lo mismo y la sesión se usa igual. Un runtime que quiere las dos, prueba el socket y cae a proceso: es lo que hace `pron say`.

## 2. La sesión

`Session(world, projection, speaker, speaker_address, now, embedder, read_only)`; `RemoteSession(sock, projection, speaker, speaker_address, now, read_only)`.

| parámetro | qué es | quién lo decide |
|---|---|---|
| `projection` | el nombre de un `ProjectionDoc` del mundo; `all` se sintetiza si no hay ninguno (01) | el runtime, por hablante |
| `speaker` | identificador opaco; va a cada `MoveDoc` (07, 11 §6) | el runtime |
| `speaker_address` | `Modelo:doc` si el hablante es un objeto del mundo; resuelve "yo", "mi" | el runtime |
| `now` | fecha de la sesión para "Friday", "tomorrow" (11 §3) | el runtime; sin ella, el reloj |
| `read_only` | la proyección sin acciones y toda relación en modo `read`: nada dicho en esta sesión escribe, permita lo que permita la proyección (01, 05) | el runtime |
| `embedder` | el puerto de embeddings (11 §2); solo en proceso | el runtime |
| `home` (en proceso) | el store enlazado cuyo mundo es la sesión (01 §Un mundo en varios stores): sus proyecciones se leen de ahí, su `local` es ese store y ahí escribe; `None` es el store propio | el runtime |
| `world` (por socket) | a cuál mundo del daemon habla la sesión: el nombre de un store enlazado, o su raíz; por defecto el store propio del daemon | el runtime |
| `home` (por socket) | el mundo propio del que habla; cuando difiere de `world`, solo abren las proyecciones expuestas de ese mundo (§6) | el runtime |

`session.turn(sentence) -> Response`. Una sesión es un diálogo: la pendiente (06) y los referentes viven en ella. Las sesiones no son seguras entre hilos; una sesión, un hilo.

**Identidad de una sesión remota.** El servidor guarda una sesión por la tupla `(projection, speaker, read_only, speaker_address, now)`. Dos `RemoteSession` que envían los mismos cinco valores comparten el mismo diálogo, aunque sean dos objetos o dos procesos: uno pregunta, el otro puede contestar. Un valor distinto en cualquiera de los cinco es otra sesión. Para que dos ejecuciones no se contesten entre sí, el hablante lleva la ejecución (`agent.zero/run-1`). `RemoteSession.close()` descarta el diálogo en el servidor; el turno siguiente empieza de cero con la misma clave. En proceso no hay clave: cada `Session` es su propio diálogo.

Lo que la sesión no hace: no autentica, no autoriza más allá de la proyección, no decide qué hacer con una respuesta.

## 3. La respuesta

`pron.response.Response`, un dataclass con cinco campos. `pron.session.Response` es el mismo nombre.

| campo | tipo | qué es |
|---|---|---|
| `text` | str | la respuesta en lenguaje natural, para mostrar tal cual |
| `outcome` | str | `unico`, `ambiguo`, `missing`, `error` (06) |
| `trace` | list[str] | cada llamada que el turno hizo, copiable a la shell |
| `move_id` | str | el `MoveDoc` que registró el turno (07) |
| `record` | dict | lo que el `MoveDoc` guarda: `queries`, `writes`, `edges`, `interpretation`, y según el turno `candidates`, `missing`, `corrects`, `undoes`, `error` |

Qué significa cada `outcome` para un runtime:

- `unico`: la oración se resolvió y, si escribía, escribió. `record["writes"]` lista cada escritura con `address`, `field`, `before`, `after`, `done`. Una lectura tiene `writes` vacío.
- `ambiguo`: pron preguntó y la sesión quedó pendiente. La siguiente oración de la misma sesión se prueba primero como respuesta (un número, un nombre, "none"). Es una respuesta legítima, no un error: el runtime debe mostrar `text` y dejar que el hablante conteste.
- `missing`: una palabra o un valor no existe en la proyección, o un nombre propio no dio nada. El turno terminó; `text` trae cercanos si los hay. Un fragmento que calce con el hueco en la oración siguiente se lee como corrección (06).
- `error`: el mundo rechazó la oración: una transición ilegal, una condición que no se cumple, un documento que cambió entre leer y escribir, un permiso. Lo que la prevalidación de 11 §7 detecta falla antes de tocar nada; lo que falla después (disco, un escritor concurrente) puede dejar escrituras hechas. Por eso `record["writes"]` es la verdad: cada entrada dice `done: true` o `false`, y un runtime que quiere revertir lo hecho dice `undo` (04, 11 §7).

Un runtime mira `record["writes"]` para saber qué escribió un turno, no `outcome`. Y distingue dos cosas que no son una `Response`: en proceso, `turn` solo atrapa `StoreError`; otra excepción es un defecto y sube. Por socket, `ConnectionError` es que nadie escucha, `RuntimeError` es que el servidor rechazó la petición (una operación desconocida, un modelo fuera de la proyección, un fallo interno) y su mensaje lo dice; ninguna de las dos es un `outcome == "error"`, que siempre viene dentro de una `Response` con su `MoveDoc`.

## 4. Documentos por dirección

Cuando el runtime ya sabe qué documento quiere, no necesita una oración:

- en proceso, `world.store.payload(model, name) -> dict`, una copia del payload extraído por sldb; `StoreError` si no existe. **No pasa por ninguna proyección**: lee del store lo que se le pida. El runtime autoriza la referencia antes de leerla.
- por socket, `RemoteSession.payload(model, name)`, lo mismo, salvo que el modelo tiene que estar en la proyección de la sesión: fuera de ella el servidor rechaza (`RuntimeError`, "not in projection"). `all` sin `models` declarados cubre todo modelo del mundo salvo los internos de pron.

`world.store` es la puerta a sldb entera (`find(scope, where)`, `list`, `get`, `glob`, `schema`, `matches`, y las escrituras `create`, `update_field`, `append`, `remove_field`, `clean`, `untrack`), pero un runtime que escribe por ahí está escribiendo por debajo de pron: sin verificación de verbos, sin prevalidación, sin `MoveDoc`. Es legítimo para un editor; no para un agente que quiere que sus cambios queden registrados como movimientos.

Una precisión sobre `read_only`: impide toda escritura sobre el dominio, pero cada turno sigue dejando su `MoveDoc` en `ledger/` (07): el ledger no es el dominio, y una sesión de solo lectura también deja rastro.

## 5. El mundo y el grafo

`World(root, pythonpath)`:

| método | firma | qué da |
|---|---|---|
| `model_names()` | `-> list[str]` | los modelos registrados |
| `family_of(name)` | `-> list[str]` | el modelo y sus bases, el más cercano primero |
| `relation_types()` | `-> dict[str, dict]` | los `RelationTypeDoc` por `name`, con `source_types`, `target_types`, `cardinality`, `condition`, `axis`, `description` |
| `projection(name="all")` | `-> dict` | el payload de un `ProjectionDoc`, o `all` sintetizada |
| `hash_mundo()` | `-> str` | la huella de lo que el léxico y el grafo dependen (11 §5); cambia con cualquier escritura fuera del ledger |
| `model_hashes()` | `-> dict[str, str]` | modelo → `hash_b` |
| `graph_is_fresh()` | `-> bool` | si el grafo tipado corresponde a los `hash_b` actuales |
| `refresh()`, `refresh_if_stale()` | `-> dict`, `-> bool` | reconstruir el grafo (siempre; solo si no corresponde). Importan kgdb y networkx; nada más lo hace |
| `derived_dir` | `Path` | `.pron/`, fuera de git, para lo que el runtime derive |

**Identificadores de nodo.** El grafo usa los ids de la exportación de sldb, y `pron.graph` da las funciones que los arman: `doc_id("Reservation:reservation-x") == "sldb://document/Reservation:reservation-x"`, `model_id("Reservation") == "sldb://model/Reservation"`, `relation_type_id("booked_by") == "sldb://relation_type/booked_by"`, `field_id("Reservation", "status") == "sldb://field/Reservation.status"`. Un `export_id` es `Modelo:nombre`. Todo método del grafo recibe y devuelve estos ids completos.

**`World.graph` (`Graph`)**, leído de `.pron/graph.nx.json` sin networkx. Una arista es siempre `{"source": id, "target": id, "relation": str, "metadata": dict}`; `metadata` trae lo que kgdb registró (`origin`, `relation_doc`, `condition`, `axis` en las autoradas).

| método | firma | devuelve |
|---|---|---|
| `available()` | `-> bool` | si hay archivo de grafo |
| `built_from()` | `-> dict[str, str]` | modelo → `hash_b` con que se construyó |
| `has_node(node_id)` | `-> bool` | |
| `node(node_id)` | `-> dict` | el nodo como kgdb lo exportó (`identity`, `schema`…), `{}` si no existe |
| `node_type(node_id)` | `-> str \| None` | `identity.node_type`; para un documento, su modelo |
| `nodes_of_type(node_type)` | `-> list[str]` | ids, ordenados |
| `edges_from(node_id, relation=None)`, `edges_to(node_id, relation=None)` | `-> list[dict]` | aristas salientes / entrantes, filtradas por relación si se da |
| `exists(source, target, relation)` | `-> dict \| None` | la arista, o nada |
| `targets(node_id, relation)`, `sources(node_id, relation)` | `-> list[str]` | ids únicos, ordenados |
| `roots(node_type, relation)` | `-> list[str]` | nodos del tipo sin arista saliente de esa relación |
| `children(node_id, relation="semantic_parent")`, `parent(node_id, relation="semantic_parent")` | `-> list[str]`, `-> str \| None` | los que apuntan a `node_id`; el primero al que `node_id` apunta |
| `descendants(node_id, relation="semantic_parent", depth=None)` | `-> list[str]` | alcanzables siguiendo la relación hacia atrás, sin `node_id` |
| `neighbors_via(node_id, out_relation, in_relation=None, exclude_prefixes=(), same_kind=True)` | `-> list[str]` | los que comparten un destino de `out_relation` con `node_id` |

Nada del grafo sabe qué relaciones declara un mundo: toda caminata se parametriza por nombre de relación. Las estructurales de kgdb (`semantic_parent`, `tagged_as`, `has_document`, `has_model`, …) son argumentos como cualquier otro.

**Por socket**, `RemoteSession.world` y `RemoteSession.graph` exponen los mismos métodos con los mismos nombres y resultados, con argumentos por nombre: `session.graph.targets(node_id=..., relation=...)`, `session.world.relation_types()`. Un método fuera de la lista es `RuntimeError`. `refresh` es una operación aparte del socket, no un método de `world`.

## 6. Permisos: lo que pron decide y lo que no

pron decide con la proyección: qué modelos se pueden nombrar, qué relaciones y en qué modo, qué verbos de acción. Una sesión `read_only` es esa misma proyección sin escritura. Lo que no está en la proyección no existe para la sesión: la oración vuelve con "I don't have that word" sin tocar sldb (01).

**Entre mundos.** Un cliente cuyo `home` es otro mundo solo abre las proyecciones que el mundo destino marca `exposed: true` (01 §Interfaz entre mundos): su léxico de interfaz. Por ellas dice oraciones, pide el léxico y el estado, y nada más: `payload`, `graph`, `world` y `refresh` se rechazan (`RuntimeError`, "may only speak"). Hablarle a otro mundo es semántico; su store no se toca. Dentro de la proyección expuesta rigen las reglas de cualquier sesión, y el `MoveDoc` queda en el mundo destino con el hablante que el cliente declaró.

pron no decide quién es el hablante ni qué proyección le toca. Eso lo elige el runtime al abrir la sesión, y el `MoveDoc` registra lo que el runtime dijo. Un runtime con permisos propios los aplica antes de abrir la sesión, y elige `read_only` para toda lectura, de modo que un permiso de lectura no pueda escribir aunque la proyección lo permita.

## 7. El socket

`pron serve --world <root> [--world name=<root2> ...]` abre **un** store, el del primer `--world`, y enlaza en él los stores de los demás mundos bajo su nombre (01 §Un mundo en varios stores); el socket es el de ese store. Cada mundo montado recibe un `<root>/.pron/serve.sock` que apunta al daemon, así un cliente que solo conoce su mundo lo encuentra. `mount` enlaza un mundo en un daemon corriendo; `worlds` los lista. Una sesión sobre el mundo `A` es una sesión con hogar `A`: lee las proyecciones de A, resuelve en A, escribe en A. Cada petición lleva `world` y `home` (§2). El daemon escucha en `socket_path(root)`: `<root>/.pron/serve.sock`, o una ruta corta en el directorio temporal, nombrada por un hash de `root`, cuando la del mundo excede el límite de un socket Unix. Servidor y clientes calculan la misma ruta con la misma función.

Protocolo: una conexión por petición, un objeto JSON por línea en cada sentido. Operaciones: `say`, `payload`, `lexicon`, `state`, `close` (descartar el diálogo de esa clave), `graph` y `world` (`method` de la lista de §5 más `args` por nombre), `refresh`, `ping`, `worlds`, `mount`, `stop`. Un cliente de otro mundo solo puede `say`, `lexicon`, `state`, `close`, `ping`, `worlds`. Las que hablan de una sesión llevan los cinco parámetros de §2. Toda respuesta trae `ok`; con `ok: false`, `error`. `pron.client.request(sock, {...})` hace una petición y levanta `ConnectionError` si nadie escucha y `RuntimeError` si el servidor rechazó; `alive(sock)` dice si hay servidor, y un archivo de socket huérfano no engaña.

El servidor atiende de a una petición. No autentica: habla como el hablante que el cliente dice ser. Quién puede tocar el socket es del sistema de archivos y del runtime.

## 8. Plantilla de mundo

Un runtime que crea muchos mundos de la misma clase les da su vocabulario con una plantilla (01 §Plantilla de un mundo): `init_world(root, pythonpath, template=DIR)` o `pron init --template DIR`; `apply_template(root, DIR)` sobre un mundo que ya existe. La plantilla trae los `AnchorDoc`, los `ProjectionDoc` (incluida la interfaz expuesta) y los `RelationTypeDoc` que la clase de nodo necesita. Es del runtime; pron la aplica y no la interpreta.

## 9. Qué es estable

Estable, y cambia solo con este documento: las firmas de `Session`, `RemoteSession`, `Response` y sus cinco campos, los cuatro `outcome`, las claves de `record` nombradas arriba, la clave de sesión remota, `world` y `home` y la regla de las proyecciones expuestas, `world.store.payload`, los métodos de `World` y `Graph` con las firmas y resultados de §5, las cuatro funciones de id de `pron.graph`, las funciones y clases de `pron.client`, las operaciones del socket, `socket_path`, y `init_world(template=)` / `apply_template` con la forma de la plantilla.

Interior, sin promesa: el léxico, la superficie, `resolve`, `verbs`, `kernel`, `dialogue`, `ledger`, `display`, la forma de los `AnchorDoc` y `ProjectionDoc` más allá de lo que dicen 01 y 05, y el formato de `.pron/graph.nx.json`.

Lo que un runtime necesite y no esté acá se pide como cambio de este capítulo, no se toma de adentro.
