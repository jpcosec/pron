# 07 · Ledger

## Qué se registra

Cada turno deja un movimiento con:

- la oración tal como entró y quién la dijo;
- el estado del diálogo antes y después;
- las direcciones y predicados pedidos a sldb, y lo que devolvieron;
- el verbo, sujeto y objeto resueltos;
- las aristas leídas del índice de sldb, o la escritura hecha en sldb con el valor anterior y el nuevo;
- la salida del grounding: único, ambiguo o missing, con los candidatos o los cercanos;
- el `hash_mundo` antes y después (ver abajo).

El ledger es un documento del mundo, una instancia de `MoveDoc` por movimiento, trackeada en el store como cualquier otra. Así se consulta por dirección: "today's moves on the repl" es `st.{MoveDoc}` con un `--where`.

El `MoveDoc` se escribe en el primer store de la proyección de la sesión (01 §Un mundo en varios stores): el ledger de un nodo vive con el nodo, también cuando habla a través de un daemon.

El `record` guarda además **lo que el turno leyó**: `reads`, una entrada por documento que una frase nominal resolvió, incluidos los complementos ("of Luis Soto" lee al cliente) y los extremos de las aristas que una lectura devolvió, cada una con la dirección `Modelo:doc` y el `hash_c` que el documento tenía en ese momento. Es la revisión observada por lectura que un runtime necesita para saber sobre qué versión decidió (12 §3); no es una copia del documento.

## Frescura: tres huellas, no una

Escribir un `MoveDoc` cambia el `hash_a` del store. Si el léxico y el grafo dependieran de `hash_a`, registrar una consulta los invalidaría. Por eso pron distingue:

| huella | qué cubre | quién la calcula | qué invalida |
|---|---|---|---|
| `hash_a` | todo el store | sldb | nada en pron; es la huella de integridad |
| `hash_mundo` | por cada modelo menos `MoveDoc`: nombre, versión, `hash_b` y su esquema (campos, tipos, descripciones, como los da `serve /schema`); la lista de predicados; la lista de stores enlazados con el `hash_mundo` de cada uno | pron, desde los índices del store y el esquema de los modelos | el léxico y los embeddings; no el índice de aristas, que se invalida por documento (abajo) |
| `hash_b` de `MoveDoc` | el ledger | sldb | nada: los movimientos no son nodos del índice de aristas y sus valores no entran al léxico |

El índice de aristas no tiene una huella única "con la que se construyó": cada documento invalida su propio shard por su `hash_c`/`hash_d` (03). Los `MoveDoc` llevan el tag `type.pron.move`, y ese tag queda fuera del índice que pron lee (`doc_kind.tags_outside_graph()`), así que registrar un movimiento nunca desactualiza nada.

El ledger sí está en el léxico como **modelo**: `MoveDoc` tiene alias ("move", "moves") y sus campos se preguntan como los de cualquier otro (10 §1), por eso "today's moves on the repl" funciona. Lo que queda fuera de la frescura es su contenido: escribir un movimiento nuevo no agrega palabras, no cambia el esquema y no crea aristas, así que no invalida nada.

## Orden dentro de un turno

1. interpretar (06);
2. ejecutar: leer sldb (documentos o su índice de aristas), o escribir sldb (04);
3. si hubo escritura: refresh, y `hash_mundo` nuevo;
4. escribir el `MoveDoc` con `hash_mundo` antes y después;
5. responder.

Un turno de lectura no hace refresh. El `MoveDoc` se escribe antes de responder y después del refresh, y no dispara otro refresh.

## Cómo se contesta "why?"

"why X?" combina dos fuentes, en este orden:

1. **el ledger**: el último movimiento que escribió sobre la dirección de X: quién, cuándo, con qué oración;
2. **el grafo**: las aristas de X cuyo verbo tiene eje WHY o PROVENANCE (`grounded_by`, `explains_failure_of`, …), y los links con predicado de esos ejes dentro del documento.

"how?" usa el eje HOW; "what is it?" usa WHAT y la descripción del modelo. La respuesta cita ambas fuentes por separado: lo que dice el registro y lo que dice el mundo.

## Provenance de lo escrito

Todo documento creado por pron lleva en su `provenance` el id del movimiento que lo creó. Así de cualquier objeto se llega a la oración que lo produjo, y de la oración a quién la dijo.

## Invariantes

- No hay movimiento sin registro, incluidos los que no cambian de estado.
- El registro se escribe antes de responder al hablante.
- Un movimiento no se edita; una corrección es otro movimiento que lo referencia.
