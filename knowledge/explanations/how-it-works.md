# Cómo funciona

## Question

¿Cómo funciona pron, paso a paso?

## Answer

pron no guarda nada del mundo por su cuenta: sldb es el store de documentos (los sustantivos, cada uno con dirección y campos) y kgdb es el grafo de relaciones tipadas (los verbos transitivos, declarados en `RelationTypeDoc` y afirmados como `RelationDoc`). pron traduce entre una oración y esas dos cosas; no tiene su propia base de datos ni su propio esquema.

El diccionario con el que entiende una oración no está escrito en el código de pron: sale de los datos, cada vez que se carga un mundo.

- **Sustantivos** — de los modelos de sldb: el nombre del modelo, sus campos, los valores que ya existen (`lexicon.py`).
- **Verbos transitivos** — de los `RelationTypeDoc` de kgdb: cada tipo de relación declarado se vuelve una palabra-verbo (`booked_by`, `implements`), en modo lectura o lectura-y-afirmación según lo que la proyección permita.
- **Verbos de acción** (`create`, `change`, `add`, `remove`, `forget`…) y la gramática (`the`, `it`, `who`, `on`) son lo único fijo de pron, iguales para cualquier mundo (spec 04, 11 §0).

Un turno (`Session.turn`, spec 06/07/11) sigue siempre el mismo camino:

1. **Interpretar** — la oración se tokeniza y se prueba contra un puñado fijo de construcciones (crear, cambiar, preguntar, deshacer…) hasta que una calza.
2. **Bajar a formas** — lo entendido se escribe como una s-expression (spec 13): `(create Reservation (party_size 6))`, `(assert booked_by … …)`. Es un lenguaje intermedio, chico y sin ambigüedad — el mismo que produciría un click en `graph_ui` en vez de una oración escrita. Todo lo que sigue trabaja sobre esta forma, no sobre la oración original.
3. **Resolver los sustantivos** — cada frase nominal de las formas se convierte en direcciones concretas de sldb (`find --where`, un referente como "it", o una dirección exacta). Si hay ambigüedad, se abre una pregunta pendiente en vez de adivinar.
4. **Prevalidar** — antes de escribir nada, se simula el movimiento completo (coerción de tipos, transiciones de estado, condiciones de las aristas) contra una copia en memoria; si algo fallaría, no se toca el store.
5. **Ejecutar** — recién ahí se escribe de verdad: `docs create`, `fields update`, un `RelationDoc` nuevo.
6. **Refrescar** — el grafo de kgdb se reconstruye a partir de lo que sldb acaba de guardar.
7. **Registrar** — todo el turno (qué se leyó, qué se escribió, el hash del mundo antes y después) queda en un `MoveDoc` (el ledger); ahí se apoya "¿por qué?".

El estado propio de una sesión es mínimo: si hay o no una pregunta pendiente, y los referentes recientes ("it", "the previous one"). Nada más persiste entre turnos que no esté ya en sldb o en el ledger.

Afuera de pron: **sldb** (el store de documentos y direcciones), **kgdb** (el grafo de relaciones tipadas, derivado y de solo lectura), **graph_ui** (otra superficie, gestos en vez de oraciones, que produce las mismas formas de spec 13) y **legos** (consume pron como librería, sin pasar por ninguna superficie — ver §Quién lo usa).

Las capas de código que implementan cada paso están en la tabla de la siguiente sección (§Capas); una versión dibujada de este mismo recorrido, con un turno completo de ejemplo, está en [`docs/spec2viz`](docs/spec2viz/README.md) (`offline.html`, sin dependencias de red).

## Sources

- SpecDoc:spec-06
- SpecDoc:spec-07
- SpecDoc:spec-11
- SpecDoc:spec-13
