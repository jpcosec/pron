# 07 · Ledger

## Qué se registra

Cada turno deja un movimiento con:

- la oración tal como entró y quién la dijo;
- el estado del diálogo antes y después;
- las direcciones y predicados pedidos a sldb, y lo que devolvieron;
- el verbo, sujeto y objeto resueltos;
- las aristas leídas de kgdb, o la escritura hecha en sldb con el valor anterior y el nuevo;
- la salida del grounding: único, ambiguo o missing, con los candidatos o los cercanos;
- el `hash_a` del mundo antes y después.

El ledger es un documento del mundo, una instancia de `MoveDoc` por movimiento, trackeada en el store como cualquier otra. Así se consulta por dirección: "los movimientos de hoy sobre el repl" es `st.{MoveDoc}` con un `--where`.

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
