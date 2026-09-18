# 09 · Una conversación, paso a paso

Ocho oraciones sobre un mundo que no es pron: las reservas de un restaurante, declarado entero en 09a (modelos, tipos de relación, transiciones, proyección y alias). Para cada una: cómo se clasifican las palabras, qué interpretación parcial queda, qué se le pregunta al mundo y qué contesta, qué se descarta con eso, qué operación se hace y qué se registra. Las llamadas a sldb son las reales. Las oraciones están en inglés porque el mundo está declarado en inglés (11 §0); la prosa que las explica sigue en español.

## El mundo

Un store en `~/worlds/restaurant/.sldb`, declarado por alguien que no es pron. Modelos de contenido:

| modelo | campos | alias |
|---|---|---|
| `Client` | `name`, `phone`, `notes` | client, clients; `name` ← "named", "called" |
| `Table` | `number`, `capacity`, `zone: Literal[terrace, indoor]` | table, tables; `capacity` ← "for N", `zone` ← "on the Z" |
| `Reservation` | `date`, `time`, `party_size`, `status: Literal[pending, confirmed, seated, cancelled]`, `notes` | reservation, reservations, booking; `party_size` ← "for N people" |
| `State` | `machine`, `name`, `description` | uno por valor del `Literal`, con `machine: Reservation.status` |

Modelos de relación de sldb, registrados en el store:

| `RelationTypeDoc` | source → target | cardinalidad | eje | alias |
|---|---|---|---|---|
| `booked_by` | Reservation → Client | many_to_one | WHAT | "has", "of"; y el paso 2 del alias `book` |
| `assigned_to` | Reservation → Table | many_to_one | WHERE | "assign", "put it at table" · condición del tipo: `capacity >= {party_size}` |
| `transitions_to` | State → State | many_to_many | WHEN | transiciones |

`RelationDoc` existentes de `transitions_to`: pending → confirmed con condición `party_size <= 8`; pending → cancelled; confirmed → seated; confirmed → cancelled. Mesas: 3 y 5 indoor para 4; 12 y 14 en la terraza para 6 y 8; 20 en la terraza para 2. Clientes: Ana Pérez, Luis Soto. Proyección de la sesión: `all`, con `read and assert` en `booked_by` y `assigned_to`, `read` en `transitions_to`, y todos los verbos de acción.

## El procedimiento de comprensión

Toda oración pasa por los mismos seis pasos. El mundo interviene en los pasos 2, 4 y 5.

1. **Segmentar** la oración en constituyentes: determinante, sustantivo, adjetivo o relativa, verbo, nombre propio, literal, referente.
2. **Clasificar cada palabra contra el léxico de la proyección** (05), cargado al abrir la sesión y recargado si cambió `hash_mundo`. Una palabra es: *término* si está en el léxico por una de sus formas listadas; *referente* si es pronombre o demostrativo; *literal* si va entre comillas, tras "to:", tras "saying", o tras un campo que fija valor; *nombre propio* si ocupa la posición de nombre tras un término; *desconocida* si no es nada de eso.
3. **Armar las interpretaciones parciales.** Cada frase nominal es un alcance más predicados, con su determinante. Cada verbo se clasifica como transitivo (un `RelationTypeDoc`), de acción (una entrada del kernel) o compuesto (un alias `compose`). Si una palabra admite dos lecturas, se mantienen las dos.
4. **Consultar el mundo por cada frase nominal.** Nombres propios y predicados van a sldb como direcciones con `--where`. Lo que vuelve completa o descarta interpretaciones.
5. **Verificar tipos.** Verbo transitivo: clases de sujeto y objeto contra `source_types` y `target_types`, y la condición contra sldb. Verbo de acción: el campo existe en el modelo del sujeto y el valor cabe en su tipo.
6. **Decidir la salida.** Único, ambiguo o missing según la cardinalidad que cada determinante permite.

La interpretación es este registro, y es lo que va al ledger:

```yaml
forma: nominal | transitiva | accion | compuesta
sujeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad: una | conjunto}
verbo:   {nombre, tipo: transitivo | accion, eje, modo: leer | afirmar}
objeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad}
campo:   nombre de campo
valor:   literal | payload
huecos:  []
salida:  unico | ambiguo | missing
```

---

## Turno 1 · "create a client named Ana Rojas, phone 9 5555 1234"

**Clasificar.**

| palabra | clase | fuente |
|---|---|---|
| create | verbo de acción "create" | kernel |
| a client | determinante + término | modelo `Client` |
| named | campo | alias → `name` |
| Ana Rojas | literal | sigue a un campo que fija valor |
| phone | campo | alias → `phone` |
| 9 5555 1234 | literal | idem |

**Interpretación.**

```yaml
forma: accion
verbo: {nombre: create, tipo: accion}
sujeto: {alcance: Client, cardinalidad: una}
valor: {name: "Ana Rojas", phone: "9 5555 1234"}
huecos: []
```

**Verificar contra el esquema.** `fields show models/Client` dice que `name` y `phone` son obligatorios y `notes` opcional. El payload cubre los obligatorios: no hay huecos. Si faltara `phone`, la salida sería ambigua con una *pendiente de dato* (06): "phone?", y la próxima oración se leería primero como ese valor.

**Operación.**

```
sldb docs create --model Client -o clients/ana-rojas.md --name client-ana-rojas \
  '{"name": "Ana Rojas", "phone": "9 5555 1234", "notes": ""}'
```

El nombre del documento sale de la regla `naming` del `ProjectionDoc`, `client-{name}`; si chocara con uno existente, pron lo diría antes de crear.

**Refresh.** `stores update`, `sldb.api.rebuild_edges` — sin nada que hacer: `docs create` ya dejó al día el shard de aristas del documento nuevo.

**Respuesta.** "Created client Ana Rojas." La dirección `st.{Client}.client-ana-rojas` queda como referente singular de clase `Client`.

**Registro.** `MoveDoc` con el payload, la dirección creada, `hash_mundo` antes y después.

---

## Turno 2 · "book her a table on the patio for 6 people on Friday at 9pm"

**Clasificar.** "book her" es una forma del alias compuesto `book` (09a): crear una `Reservation` con los literales, afirmar `booked_by` hacia el referente de clase `Client` ("her"), afirmar `assigned_to` hacia la frase nominal de clase `Table`. "a table" es determinante + término. "on the patio" es un predicado sobre `zone`, pero "patio" no es un valor de `zone`. "for 6 people" es `party_size = 6` de la reserva y, por el alias de `capacity`, también el predicado `capacity >= 6` sobre la mesa. "on Friday" y "at 9pm" son literales de `date` y `time`; la superficie los normaliza a `2026-09-11` y `21:00` con la fecha de la sesión (11 §3).

**Salida: missing**, en el paso 2. "patio" está en posición de valor de un campo enumerado y no está en el léxico. Cercanos por embeddings sobre los valores de `zone`:

> There is no zone "patio". Did you mean *terrace* or *indoor*?

Nada se consultó a sldb, nada se creó. **Registro** del hueco y los cercanos.

---

## Turno 3 · "on the terrace"

No hay pendiente, porque missing termina el turno. Es una frase sin verbo con un predicado suelto: la superficie la lee como **corrección del último movimiento missing** si el fragmento calza con el hueco registrado (06). Calza: `zone = "terrace"`. Se reinterpreta la oración del turno 2 con el hueco relleno.

**Interpretación.**

```yaml
forma: compuesta
alias: book
pasos:
  - {do: create, model: Reservation, $literals: {date: "2026-09-11", time: "21:00", party_size: 6, status: pending}}
  - {do: assert, relation: booked_by, source: $created, target: {$referent:Client: ["st.{Client}.client-ana-rojas"]}}
  - {do: assert, relation: assigned_to, source: $created, target: {$object:Table: {alcance: "st.{Table}", predicados: ['zone = "terrace"', 'capacity >= 6'], determinante: a}}}
```

Las ranuras del alias se llenan desde la oración: `$literals` con los campos que los alias de `Reservation` reconocen; `$referent:Client` con "her", el último singular de clase `Client`, Ana Rojas; `$object:Table` con la frase nominal "a table on the terrace for 6". Nada es implícito: los tres pasos están escritos en el alias.

**Consulta al mundo.**

```
find 'st.{Table}' --where 'zone = "terrace"'   → table-12, table-14, table-20
find 'st.{Table}' --where 'capacity >= 6'      → table-12, table-14
∩                                               → table-12, table-14
```

Determinante "a": cualquiera. pron toma la primera y lo dice.

**Verificar tipos.** `booked_by`: Reservation → Client, sí. `assigned_to`: Reservation → Table, sí; `many_to_one`, una reserva tiene una mesa, se cumple porque la reserva es nueva.

**Operación.** Tres documentos en un movimiento:

```
sldb docs create --model Reservation -o reservations/2026-09-11-ana-rojas.md --name reservation-2026-09-11-ana-rojas \
  '{"date": "2026-09-11", "time": "21:00", "party_size": 6, "status": "pending", "notes": ""}'
sldb docs create --model RelationDoc -o relations/booked_by--reservation-…--client-ana-rojas.md \
  '{"source_id": "Reservation:reservation-2026-09-11-ana-rojas", "target_id": "Client:client-ana-rojas", "relation_type": "booked_by", "condition": ""}'
sldb docs create --model RelationDoc -o relations/assigned_to--reservation-…--table-12.md \
  '{"source_id": "Reservation:reservation-2026-09-11-ana-rojas", "target_id": "Table:table-12", "relation_type": "assigned_to", "condition": ""}'
```

El `RelationDoc` de `assigned_to` no lleva condición propia: hereda la del tipo, `capacity >= {party_size}` (09a). Antes de crearlo pron la evaluó sobre table-12 con `party_size = 6`: `find st.{Table} --where 'capacity >= 6'` contiene table-12. Es la misma condición que vuelve en el turno 7.

**Refresh**, una vez.

**Respuesta.** "Reservation for Ana Rojas on Friday the 11th at 21:00, 6 people, table 12 on the terrace, pending. Table 14 would also work."

**Registro.** Las dos consultas con sus resultados, la elección de table-12 y la alternativa, los tres documentos creados.

---

## Turno 4 · "what reservations does Ana have for Friday?"

**Clasificar.** "what reservations" es término plural interrogado; "have" es la lectura inversa del verbo `booked_by` (alias "has, have" → `booked_by` leído desde el target); "Ana" es nombre propio en posición de nombre; "for Friday" es `date = "2026-09-11"`.

**Consulta al mundo.**

```
find 'st.{Client}' --where 'name ~ "Ana"'   → client-ana-perez, client-ana-rojas
```

Dos direcciones y la posición gramatical pide una persona. **Salida: ambiguo.**

> Which one? (1) Ana Pérez · (2) Ana Rojas

**Registro**, estado `libre → pendiente`.

---

## Turno 5 · "Rojas"

Hay pendiente de elección. "Rojas" no tiene verbo ni determinante: se prueba como designación. Se compara con los nombres naturales de los candidatos: calza solo con "Ana Rojas". Rellena el hueco y se completa el turno 4.

**Consulta al grafo y al mundo.**

```
sldb edges_to("sldb://document/Client:client-ana-rojas", "booked_by")   → Reservation:reservation-2026-09-11-ana-rojas
find 'st.{Reservation}' --where 'date = "2026-09-11"'                    → reservation-2026-09-11-ana-rojas, reservation-2026-09-11-luis-soto
∩                                                                         → reservation-2026-09-11-ana-rojas
```

La intersección cruza la lista que dio el índice de aristas con la que dio la consulta estructural: direcciones, no payloads, las dos de sldb (03). Si el índice tuviera algo desactualizado, la primera lista podría venir de un documento tocado por fuera de sldb, y la traza lo diría igual.

**Respuesta.** "One: Friday the 11th at 21:00, 6 people, table 12, pending." El resultado es un conjunto de una dirección; un conjunto de exactamente un elemento califica también como antecedente singular (06), así que queda disponible para "it" y para "that reservation".

**Registro**, estado `pendiente → libre`.

---

## Turno 6 · "confirm it"

**Clasificar.** "confirm it" es una forma del alias `confirm` → `(change (it "it" Reservation) status "confirmed")`; "it" es referente singular. Un alias puede nombrar un verbo de acción con campo y valor fijos; es una de las dos formas en que un mundo agrega verbos sin código.

**Referente.** "it" en un verbo que exige `Reservation`: el último singular de esa clase, el del turno 5.

**Interpretación.**

```yaml
forma: accion
verbo: {nombre: change, tipo: accion}
sujeto: {direcciones: ["st.{Reservation}.reservation-2026-09-11-ana-rojas"], cardinalidad: una}
campo: status
valor: confirmed
```

**Verificar la transición.** `status` es un campo `Literal` y el mundo tiene documentos `State` con `machine = "Reservation.status"`: cambiar ese campo es una transición (03).

```
get 'st.{Reservation}.reservation-2026-09-11-ana-rojas.status'                         → pending
find st.{State} --where 'machine = "Reservation.status"' ∩ --where 'name = "pending"'   → state-reservation-pending
find st.{RelationDoc} --where 'source_id = "State:state-reservation-pending"' ∩ 'relation_type = "transitions_to"'
  → transitions_to--…-pending--…-confirmed (condition: "party_size <= 8"), transitions_to--…-pending--…-cancelled
find 'st.{Reservation}' --where 'party_size <= 8'                                      → contiene reservation-2026-09-11-ana-rojas
```

La arista existe, leída desde sldb porque la verificación no depende del grafo (03 §Qué se verifica dónde), y la condición, evaluada por sldb sobre el sujeto, se cumple. Si la reserva fuera de 9, la respuesta sería "cannot confirm: the condition is party_size <= 8 and it has 9", con la arista citada.

**Operación.**

```
sldb fields update docs/reservation-2026-09-11-ana-rojas/status '"confirmed"'
```

**Refresh. Respuesta.** "Confirmed." **Registro** con el estado anterior, el nuevo, la arista y la condición evaluada.

---

## Turno 7 · "change it to 9 people and add a note saying: birthday"

**Clasificar.** Dos verbos de acción coordinados sobre el mismo referente: "change" con campo `party_size` (por la forma "N people") y literal `9`; "add a note" es la forma del alias `note` sobre `notes`, y "saying:" abre el literal. Una oración con dos verbos de acción coordinados con "and" es un movimiento con dos escrituras (06 §Coordinación).

**Verificar.** `party_size` es entero: `9` cabe. `notes` es texto. No es transición: ninguno de los dos campos tiene documentos `State`.

**Operación.**

```
sldb fields update docs/reservation-2026-09-11-ana-rojas/party_size 9
sldb fields update docs/reservation-2026-09-11-ana-rojas/notes '"birthday"'
```

Después de la primera escritura, el `hash_c` esperado del documento se reemplaza por el que sldb dejó, así la segunda no se rechaza (11 §5). **Refresh**, una vez.

**Respuesta.** "Done: 9 people, note *birthday*. Heads up: table 12 seats 6." Esa advertencia sale de una regla del mundo, no de pron: el tipo `assigned_to` declara la condición `capacity >= {party_size}` (09a) y la arista de esta reserva la hereda; después de cambiar `party_size` pron reevalúa las condiciones de las aristas que salen del sujeto y de las que entran a él, y avisa de las que dejaron de cumplirse. No deshace nada.

**Registro** con los dos valores anteriores y nuevos y la condición que dejó de cumplirse.

---

## Turno 8 · "why did you warn me about the table?"

**Clasificar.** Interrogativo de causa sobre el último movimiento, con "the table" acotando a qué parte de la respuesta.

**Dos fuentes.**

1. El ledger: el `MoveDoc` del turno 7 tiene la condición reevaluada: `assigned_to → table-12`, `capacity >= {party_size}` con `capacity = 6`, `party_size = 9`, falsa.
2. El mundo: las aristas del sujeto con eje WHEN o WHERE que tengan condición: la misma.

Antes de ofrecer alternativas pron evalúa la misma condición sobre las otras mesas: `find st.{Table} --where 'capacity >= 9'` devuelve vacío.

**Respuesta.** "Because the reservation is assigned to table 12, and that assignment requires capacity >= party size: 6 >= 9 stopped holding when you changed it to 9. No table seats 9; the largest is table 14, for 8. I can drop it to 8 and move it to table 14, or leave it as is."

**Registro** de lectura, sin refresh.

---

## Lo que esta conversación fija

- El mundo interviene tres veces por oración: léxico (paso 2), direcciones (paso 4), tipos y condiciones (paso 5). Nunca antes de segmentar, nunca después de decidir la salida.
- Un valor de campo enumerado que no existe es missing en el léxico, antes de consultar sldb. Un nombre propio se busca en sldb y cero resultados es missing después de consultar.
- Un missing termina el turno, pero un fragmento que calza con el hueco registrado se lee como corrección y reinterpreta la oración entera.
- Crear es un verbo de acción con payload; los campos obligatorios que falten abren una pendiente de dato por campo. Crear un sujeto y afirmar verbos sobre él en un movimiento es un alias `compose` con sus pasos escritos.
- Dos restricciones son dos consultas y una intersección de direcciones, también cuando una lista viene del índice de aristas y otra de una consulta estructural.
- Una transición es cambiar el campo de estado, permitida por una arista `transitions_to` y su condición, ambas verificadas en sldb, con o sin grafo.
- Un mundo agrega verbos sin código de dos maneras: un alias de acción con campo y valor fijos ("confirm"), o un `RelationTypeDoc` que es un verbo transitivo nuevo; y oraciones nuevas con un alias `compose`.
- Después de una escritura pron reevalúa las condiciones de las aristas del sujeto en las dos direcciones y avisa; no deshace ni decide.
- Un referente se elige por número y por la clase que el verbo exige.
- Afirmar y leer un verbo son dos permisos distintos de la proyección; un paso `create` dentro de un `compose` exige además `create` en `actions`.
