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

`session.turn(sentence) -> Response`. Una sesión es un diálogo: la pendiente (06) y los referentes viven en ella. Un runtime que quiere que dos ejecuciones no se contesten la pregunta entre sí abre una sesión por ejecución. Las sesiones no son seguras entre hilos; una sesión, un hilo.

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
- `error`: el mundo rechazó la oración: una transición ilegal, una condición que no se cumple, un documento que cambió entre leer y escribir, un permiso. Nada se escribió salvo lo que `record["writes"]` diga con `done: true`, y con la prevalidación de 11 §7 eso es nada en un movimiento con varias escrituras.

Un runtime que necesita saber si un turno escribió mira `record["writes"]`, no `outcome`.

## 4. Documentos por dirección

Cuando el runtime ya sabe qué documento quiere, no necesita una oración:

- en proceso, `world.store.payload(model, name) -> dict`, una copia del payload extraído por sldb; `StoreError` si no existe;
- por socket, `RemoteSession.payload(model, name)`, lo mismo.

`world.store` es la puerta a sldb entera (`find(scope, where)`, `list`, `get`, `glob`, `schema`, `matches`, y las escrituras `create`, `update_field`, `append`, `remove_field`, `clean`, `untrack`), pero un runtime que escribe por ahí está escribiendo por debajo de pron: sin verificación de verbos, sin prevalidación, sin `MoveDoc`. Es legítimo para un editor; no para un agente que quiere que sus cambios queden registrados como movimientos.

## 5. El mundo

`World(root, pythonpath)`:

| método | qué da |
|---|---|
| `model_names()`, `family_of(name)`, `relation_types()` | qué declara el mundo |
| `projection(name)` | el payload de un `ProjectionDoc`, o `all` sintetizada |
| `hash_mundo()` | la huella de lo que el léxico y el grafo dependen (11 §5); cambia con cualquier escritura fuera del ledger |
| `graph_is_fresh()`, `refresh()`, `refresh_if_stale()` | si el grafo tipado corresponde al store; reconstruirlo (siempre, o solo si no corresponde) |
| `graph` | el grafo tipado leído de `.pron/graph.nx.json`, sin networkx: `edges_from`, `edges_to`, `targets`, `sources`, `nodes_of_type`, `roots`, `children`, `parent`, `descendants`, `neighbors_via`, todo por nombre de relación |
| `derived_dir` | `.pron/`, fuera de git, para lo que el runtime derive |

`refresh()` importa kgdb y networkx; nada más lo hace. Un runtime que solo lee nunca los paga.

## 6. Permisos: lo que pron decide y lo que no

pron decide con la proyección: qué modelos se pueden nombrar, qué relaciones y en qué modo, qué verbos de acción. Una sesión `read_only` es esa misma proyección sin escritura. Lo que no está en la proyección no existe para la sesión: la oración vuelve con "I don't have that word" sin tocar sldb (01).

pron no decide quién es el hablante ni qué proyección le toca. Eso lo elige el runtime al abrir la sesión, y el `MoveDoc` registra lo que el runtime dijo. Un runtime con permisos propios los aplica antes de abrir la sesión, y elige `read_only` para toda lectura, de modo que un permiso de lectura no pueda escribir aunque la proyección lo permita.

## 7. El socket

`pron serve --world <root>` escucha en `socket_path(root)`: `<root>/.pron/serve.sock`, o una ruta corta en el directorio temporal, nombrada por un hash de `root`, cuando la del mundo excede el límite de un socket Unix. Servidor y clientes calculan la misma ruta con la misma función.

Protocolo: una conexión por petición, un objeto JSON por línea en cada sentido. Operaciones: `say`, `payload`, `lexicon`, `state`, `refresh`, `ping`, `stop`. Toda respuesta trae `ok`; con `ok: false`, `error`. `pron.client.request(sock, {...})` hace una petición y levanta `ConnectionError` si nadie escucha y `RuntimeError` si el servidor rechazó; `alive(sock)` dice si hay servidor, y un archivo de socket huérfano no engaña.

El servidor atiende de a una petición. No autentica: habla como el hablante que el cliente dice ser. Quién puede tocar el socket es del sistema de archivos y del runtime.

## 8. Qué es estable

Estable, y cambia solo con este documento: las firmas de `Session`, `RemoteSession`, `Response` y sus cinco campos, los cuatro `outcome`, las claves de `record` nombradas arriba, `world.store.payload`, los métodos de `World` y `Graph` listados, las funciones de `pron.client`, las operaciones del socket y `socket_path`.

Interior, sin promesa: el léxico, la superficie, `resolve`, `verbs`, `kernel`, `dialogue`, `ledger`, `display`, la forma de los `AnchorDoc` y `ProjectionDoc` más allá de lo que dicen 01 y 05, y el formato de `.pron/graph.nx.json`.

Lo que un runtime necesite y no esté acá se pide como cambio de este capítulo, no se toma de adentro.
