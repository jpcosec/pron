# 09 · Una conversación, paso a paso

Ocho oraciones sobre un mundo que no es pron: las reservas de un restaurante. Para cada una: cómo se clasifican las palabras, qué interpretación parcial queda, qué se le pregunta al mundo y qué contesta, qué se descarta con eso, qué operación se hace y qué se registra. Las llamadas a sldb y kgdb son las reales.

## El mundo

Un store en `~/mundos/restaurante/.sldb`, declarado por alguien que no es pron. Modelos de contenido:

| modelo | campos | alias |
|---|---|---|
| `Cliente` | `nombre`, `telefono`, `notas` | cliente, clientes; `nombre` ← "se llama" |
| `Mesa` | `numero`, `capacidad`, `zona: Literal[terraza, salon]` | mesa, mesas; `capacidad` ← "para N", `zona` ← "en la Z" |
| `Reserva` | `fecha`, `hora`, `personas`, `estado: Literal[pendiente, confirmada, sentada, cancelada]`, `notas` | reserva, reservas; `personas` ← "para N personas" |
| `Estado` | `nombre` | uno por valor del `Literal` |

Modelos de relación de kgdb, registrados en el store:

| `RelationTypeDoc` | source → target | cardinalidad | eje | alias |
|---|---|---|---|---|
| `de` | Reserva → Cliente | many_to_one | WHAT | "de", "reservale" |
| `asignada_a` | Reserva → Mesa | many_to_one | WHERE | "asignale", "en la mesa" |
| `pasa_a` | Estado → Estado | many_to_many | WHEN | transiciones |

`RelationDoc` existentes de `pasa_a`: pendiente → confirmada con condición `personas <= 8`; pendiente → cancelada; confirmada → sentada; confirmada → cancelada. Mesas: 3 y 5 en el salón para 4; 12 y 14 en la terraza para 6 y 8; 20 en la terraza para 2. Clientes: Ana Pérez, Luis Soto. Proyección de la sesión: todo, con `leer y afirmar` en las tres relaciones y todos los verbos de acción.

## El procedimiento de comprensión

Toda oración pasa por los mismos seis pasos. El mundo interviene en los pasos 2, 4 y 5.

1. **Segmentar** la oración en constituyentes: determinante, sustantivo, adjetivo o relativa, verbo, nombre propio, literal, referente.
2. **Clasificar cada palabra contra el léxico de la proyección** (05), cargado al abrir la sesión y recargado si cambió `hash_mundo`. Una palabra es: *término* si está en el léxico; *referente* si es pronombre o demostrativo; *literal* si va entre comillas, tras "a:", tras "que diga", o tras un campo que fija valor; *nombre propio* si ocupa la posición de nombre tras un término; *desconocida* si no es nada de eso.
3. **Armar las interpretaciones parciales.** Cada frase nominal es un alcance más predicados, con su determinante. Cada verbo se clasifica como transitivo (un `RelationTypeDoc`) o de acción (una entrada del kernel). Si una palabra admite dos lecturas, se mantienen las dos.
4. **Consultar el mundo por cada frase nominal.** Nombres propios y predicados van a sldb como direcciones con `--where`. Lo que vuelve completa o descarta interpretaciones.
5. **Verificar tipos.** Verbo transitivo: clases de sujeto y objeto contra `source_types` y `target_types`. Verbo de acción: el campo existe en el modelo del sujeto y el valor cabe en su tipo.
6. **Decidir la salida.** Único, ambiguo o missing según la cardinalidad que cada determinante permite.

La interpretación es este registro, y es lo que va al ledger:

```yaml
forma: nominal | transitiva | accion
sujeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad: una | conjunto}
verbo:   {nombre, tipo: transitivo | accion, eje, modo: leer | afirmar}
objeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad}
campo:   nombre de campo
valor:   literal | payload
huecos:  []
salida:  unico | ambiguo | missing
```

---

## Turno 1 · "crea un cliente que se llame Ana Rojas, teléfono 9 5555 1234"

**Clasificar.**

| palabra | clase | fuente |
|---|---|---|
| crea | verbo de acción "crear" | kernel |
| un cliente | determinante + término | modelo `Cliente` |
| que se llame | campo | alias "se llama" → `nombre` |
| Ana Rojas | literal | sigue a un campo que fija valor |
| teléfono | campo | alias → `telefono` |
| 9 5555 1234 | literal | idem |

**Interpretación.**

```yaml
forma: accion
verbo: {nombre: crear, tipo: accion}
sujeto: {alcance: Cliente, cardinalidad: una}
valor: {nombre: "Ana Rojas", telefono: "9 5555 1234"}
huecos: []
```

**Verificar contra el esquema.** `fields show models/Cliente` dice que `nombre` y `telefono` son obligatorios y `notas` opcional. El payload cubre los obligatorios: no hay huecos. Si faltara `telefono`, la salida sería ambigua con una pendiente "¿teléfono?" y la próxima oración se leería como ese valor.

**Operación.**

```
sldb docs create --model Cliente -o clientes/ana-rojas.md --name cliente-ana-rojas \
  '{"nombre": "Ana Rojas", "telefono": "9 5555 1234", "notas": ""}'
```

El nombre del documento sale de una regla del mundo, `cliente-<slug del nombre>`, declarada en el `ProjectionDoc`; si chocara con uno existente, pron lo diría antes de crear.

**Refresh.** `stores update`, `semantic-export`, `kgdb ingest`.

**Respuesta.** "Creado el cliente Ana Rojas." La dirección `st.{Cliente}.cliente-ana-rojas` queda como referente singular de clase `Cliente`.

**Registro.** `MoveDoc` con el payload, la dirección creada, `hash_mundo` antes y después.

---

## Turno 2 · "reservale una mesa en el patio para 6 personas el viernes a las 21"

**Clasificar.** "reservale" es el alias del verbo transitivo `de` más el referente "le"; también implica crear una `Reserva`, porque `de` tiene `source_types: [Reserva]` y no hay reserva todavía: el verbo transitivo con un sujeto que no existe se lee como *crear el sujeto y afirmar el verbo*. "una mesa" es determinante + término. "en el patio" es un predicado sobre `zona`, pero "patio" no es un valor de `zona`. "para 6 personas" es `personas = 6` de la reserva, y por el alias de `capacidad` también un predicado `capacidad >= 6` sobre la mesa. "el viernes" y "a las 21" son literales de `fecha` y `hora`; la superficie los normaliza a `2026-09-11` y `21:00` con la fecha de la sesión.

**Salida: missing**, en el paso 2. "patio" está en posición de valor de un campo enumerado y no está en el léxico. Cercanos por embeddings sobre los valores de `zona`:

> No hay zona "patio". ¿Querías *terraza* o *salón*?

Nada se consultó a sldb, nada se creó. **Registro** del hueco y los cercanos.

---

## Turno 3 · "en la terraza"

No hay pendiente, porque missing termina el turno. Es una frase nominal sin verbo con un predicado suelto: la superficie la lee como **corrección del último movimiento missing**, si el fragmento calza con el hueco registrado. Calza: `zona = "terraza"`. Se reinterpreta la oración del turno 2 con el hueco relleno.

**Interpretación.**

```yaml
forma: transitiva
verbo: {nombre: de, tipo: transitivo, eje: WHAT, modo: afirmar, crea_sujeto: true}
sujeto: {alcance: Reserva, cardinalidad: una, valor: {fecha: "2026-09-11", hora: "21:00", personas: 6, estado: pendiente}}
objeto: {direcciones: ["st.{Cliente}.cliente-ana-rojas"], cardinalidad: una}      # "le"
mesa:   {alcance: "st.{Mesa}", predicados: ['zona = "terraza"', 'capacidad >= 6'], determinante: una}
```

"le" es referente singular; el verbo pide `Cliente` en target; el último singular de clase `Cliente` es Ana Rojas. "una mesa" es un segundo objeto, del verbo `asignada_a` implícito por el alias "reservale una mesa".

**Consulta al mundo.**

```
find 'st.{Mesa}' --where 'zona = "terraza"'   → mesa-12, mesa-14, mesa-20
find 'st.{Mesa}' --where 'capacidad >= 6'     → mesa-12, mesa-14
∩                                              → mesa-12, mesa-14
```

Determinante "una": cualquiera. pron toma la primera y lo dice.

**Verificar tipos.** `de`: Reserva → Cliente, sí. `asignada_a`: Reserva → Mesa, sí, `many_to_one`: una reserva tiene una mesa, se cumple.

**Operación.** Tres documentos en un movimiento:

```
sldb docs create --model Reserva -o reservas/2026-09-11-ana-rojas.md --name reserva-2026-09-11-ana-rojas \
  '{"fecha": "2026-09-11", "hora": "21:00", "personas": 6, "estado": "pendiente", "notas": ""}'
sldb docs create --model RelationDoc -o relations/de--reserva-…--cliente-ana-rojas.md \
  '{"source_id": "Reserva:reserva-2026-09-11-ana-rojas", "target_id": "Cliente:cliente-ana-rojas", "relation_type": "de"}'
sldb docs create --model RelationDoc -o relations/asignada_a--reserva-…--mesa-12.md \
  '{"source_id": "Reserva:reserva-2026-09-11-ana-rojas", "target_id": "Mesa:mesa-12", "relation_type": "asignada_a"}'
```

**Refresh**, una vez.

**Respuesta.** "Reserva para Ana Rojas el viernes 11 a las 21:00, 6 personas, mesa 12 en la terraza, pendiente. También servía la 14."

**Registro.** Las dos consultas con sus resultados, la elección de mesa-12 y la alternativa, los tres documentos creados.

---

## Turno 4 · "¿qué reservas tiene Ana para el viernes?"

**Clasificar.** "qué reservas" es término plural interrogado; "tiene" es la lectura inversa del verbo `de` (alias "tiene" → `de` leído desde el target); "Ana" es nombre propio en posición de nombre tras el verbo; "para el viernes" es `fecha = "2026-09-11"`.

**Consulta al mundo.**

```
find 'st.{Cliente}' --where 'nombre ~ "Ana"'   → cliente-ana-perez, cliente-ana-rojas
```

Dos direcciones y la posición gramatical pide una persona. **Salida: ambiguo.**

> ¿Cuál? (1) Ana Pérez · (2) Ana Rojas

**Registro**, estado `libre → pendiente`.

---

## Turno 5 · "Rojas"

Hay pendiente. "Rojas" no tiene verbo ni determinante: se prueba como designación. Se compara con los títulos de los candidatos: calza solo con "Ana Rojas". Rellena el hueco y se completa el turno 4.

**Consulta al grafo y al mundo.**

```
kgdb edges_to("sldb://document/Cliente:cliente-ana-rojas", "de")   → Reserva:reserva-2026-09-11-ana-rojas
find 'st.{Reserva}' --where 'fecha = "2026-09-11"'                 → reserva-2026-09-11-ana-rojas, reserva-2026-09-11-luis-soto
∩                                                                   → reserva-2026-09-11-ana-rojas
```

La intersección cruza la lista que dio kgdb con la que dio sldb: direcciones, no payloads.

**Respuesta.** "Una: el viernes 11 a las 21:00, 6 personas, mesa 12, pendiente." La dirección queda como referente singular de clase `Reserva`.

**Registro**, estado `pendiente → libre`.

---

## Turno 6 · "confirmala"

**Clasificar.** "confirmala" es un verbo de acción del mundo: el alias "confirmar" → cambiar `estado` a `confirmada`; "la" es referente singular. Un alias puede nombrar un verbo de acción con campo y valor fijos; es la única forma en que un mundo agrega verbos sin código.

**Referente.** "la" en un verbo que exige `Reserva`: el último singular de esa clase, el del turno 5.

**Interpretación.**

```yaml
forma: accion
verbo: {nombre: cambiar, tipo: accion}
sujeto: {direcciones: ["st.{Reserva}.reserva-2026-09-11-ana-rojas"], cardinalidad: una}
campo: estado
valor: confirmada
```

**Verificar la transición.** `estado` es un campo con `Literal`, y el mundo tiene `Estado` con `pasa_a`: cambiar ese campo es una transición (03).

```
get 'st.{Reserva}.reserva-2026-09-11-ana-rojas.estado'                  → pendiente
kgdb edges_from("sldb://document/Estado:pendiente", "pasa_a")             → Estado:confirmada (condition: "personas <= 8"), Estado:cancelada
find 'st.{Reserva}' --where 'personas <= 8'                                → contiene reserva-2026-09-11-ana-rojas
```

La arista existe y la condición, evaluada por sldb sobre el sujeto, se cumple. Si la reserva fuera de 9 personas, la respuesta sería "no se puede confirmar: la condición es personas <= 8 y tiene 9", con la arista citada.

**Operación.**

```
sldb fields update docs/reserva-2026-09-11-ana-rojas/estado '"confirmada"'
```

**Refresh. Respuesta.** "Confirmada." **Registro** con el estado anterior, el nuevo, la arista y la condición evaluada.

---

## Turno 7 · "cámbiala a 9 personas y ponle una nota que diga: cumpleaños"

**Clasificar.** Dos verbos de acción sobre el mismo referente: "cambiar" con campo `personas` y literal `9`; "poner una nota" es alias de cambiar `notas`, y "que diga:" abre el literal. Una oración con dos verbos de acción coordinados es un movimiento con dos escrituras sobre el mismo sujeto.

**Verificar.** `personas` es entero: `9` cabe. `notas` es texto. No es transición: ninguno de los dos campos es `estado`.

**Operación.**

```
sldb fields update docs/reserva-2026-09-11-ana-rojas/personas 9
sldb fields update docs/reserva-2026-09-11-ana-rojas/notas '"cumpleaños"'
```

**Refresh**, una vez. **Respuesta.** "Hecho: 9 personas, nota *cumpleaños*. Ojo: la mesa 12 es para 6." Esa advertencia sale de una regla del mundo, no de pron: `asignada_a` tiene condición `capacidad >= {personas}`, y después de cambiar `personas` pron reevalúa las condiciones de las aristas del sujeto y avisa de las que dejaron de cumplirse. No deshace nada.

**Registro** con los dos valores anteriores y nuevos y la condición que dejó de cumplirse.

---

## Turno 8 · "¿por qué me avisaste de la mesa?"

**Clasificar.** Interrogativo de causa sobre el último movimiento, con "la mesa" acotando a qué parte de la respuesta.

**Dos fuentes.**

1. El ledger: el `MoveDoc` del turno 7 tiene la condición reevaluada: `asignada_a → mesa-12`, `capacidad >= {personas}` con `capacidad = 6`, `personas = 9`, falsa.
2. El mundo: las aristas del sujeto con eje WHEN o WHERE que tengan condición: la misma.

**Respuesta.** "Porque la reserva está asignada a la mesa 12, y esa asignación exige capacidad >= personas: 6 >= 9 no se cumple desde que la cambiaste a 9. Puedo asignarle la 14, que es para 8, o dejarla así."

**Registro** de lectura, sin refresh.

---

## Lo que esta conversación fija

- El mundo interviene tres veces por oración: léxico (paso 2), direcciones (paso 4), tipos y condiciones (paso 5). Nunca antes de segmentar, nunca después de decidir la salida.
- Un valor de campo enumerado que no existe es missing en el léxico, antes de consultar sldb. Un nombre propio se busca en sldb y cero resultados es missing después de consultar.
- Un missing termina el turno, pero un fragmento que calza con el hueco registrado se lee como corrección y reinterpreta la oración entera.
- Crear es un verbo de acción con payload; los campos obligatorios que falten abren una pendiente por campo. Un verbo transitivo cuyo sujeto no existe crea el sujeto y afirma el verbo en el mismo movimiento.
- Dos restricciones son dos consultas y una intersección de direcciones, también cuando una lista viene de kgdb y otra de sldb.
- Una transición es cambiar el campo de estado, permitida por una arista `pasa_a` y su condición evaluada por sldb sobre el sujeto.
- Un mundo agrega verbos sin código: un alias puede nombrar un verbo de acción con campo y valor fijos ("confirmar"), y un `RelationTypeDoc` es un verbo transitivo nuevo.
- Después de una escritura pron reevalúa las condiciones de las aristas del sujeto y avisa; no deshace ni decide.
- Un referente se elige por número y por la clase que el verbo exige.
- Afirmar y leer un verbo son dos permisos distintos de la proyección; crear un sujeto por verbo transitivo exige ambos: `crear` en `actions` y `afirmar` en la relación.
