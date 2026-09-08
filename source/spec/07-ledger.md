# 07 · Ledger

## Qué se registra

Cada turno deja un movimiento con:

- la oración tal como entró y quién la dijo;
- el estado del diálogo antes y después;
- las direcciones y predicados pedidos a sldb, y lo que devolvieron;
- el verbo, sujeto y objeto resueltos;
- las aristas leídas de kgdb, o la escritura hecha en sldb con el valor anterior y el nuevo;
- la salida del grounding: único, ambiguo o missing, con los candidatos o los cercanos;
- el `hash_mundo` antes y después (ver abajo).

El ledger es un documento del mundo, una instancia de `MoveDoc` por movimiento, trackeada en el store como cualquier otra. Así se consulta por dirección: "los movimientos de hoy sobre el repl" es `st.{MoveDoc}` con un `--where`.

## Frescura: tres huellas, no una

Escribir un `MoveDoc` cambia el `hash_a` del store. Si el léxico y el grafo dependieran de `hash_a`, registrar una consulta los invalidaría. Por eso pron distingue:

| huella | qué cubre | quién la calcula | qué invalida |
|---|---|---|---|
| `hash_a` | todo el store | sldb | nada en pron; es la huella de integridad |
| `hash_mundo` | los `hash_b` de todos los modelos menos `MoveDoc` | pron, desde los índices de modelos | el léxico, los embeddings y la frescura del snapshot de kgdb |
| `hash_b` de `MoveDoc` | el ledger | sldb | nada; el ledger no está en el léxico ni en el grafo |

El snapshot de kgdb registra el `hash_mundo` con que se construyó. Los `MoveDoc` llevan el tag `type.pron.move` y el ingest de kgdb los excluye, así que registrar no desfasa el grafo.

## Orden dentro de un turno

1. interpretar (06);
2. ejecutar: leer sldb o kgdb, o escribir sldb (04);
3. si hubo escritura: refresh, y `hash_mundo` nuevo;
4. escribir el `MoveDoc` con `hash_mundo` antes y después;
5. responder.

Un turno de lectura no hace refresh. El `MoveDoc` se escribe antes de responder y después del refresh, y no dispara otro refresh.

## Cómo se contesta "¿por qué?"

"¿Por qué X?" combina dos fuentes, en este orden:

1. **el ledger**: el último movimiento que escribió sobre la dirección de X: quién, cuándo, con qué oración;
2. **el grafo**: las aristas de X cuyo verbo tiene eje WHY o PROVENANCE (`grounded_by`, `explains_failure_of`, …), y los links con predicado de esos ejes dentro del documento.

"¿Cómo?" usa el eje HOW; "¿qué es?" usa WHAT y la descripción del modelo. La respuesta cita ambas fuentes por separado: lo que dice el registro y lo que dice el mundo.

## Provenance de lo escrito

Todo documento creado por pron lleva en su `provenance` el id del movimiento que lo creó. Así de cualquier objeto se llega a la oración que lo produjo, y de la oración a quién la dijo.

## Invariantes

- No hay movimiento sin registro, incluidos los que no cambian de estado.
- El registro se escribe antes de responder al hablante.
- Un movimiento no se edita; una corrección es otro movimiento que lo referencia.
