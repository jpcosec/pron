# 11 · Decisiones de implementación

Siete preguntas que los documentos anteriores dejan abiertas a propósito, porque no son del *qué* sino del *cómo*. Se cierran acá para que no las cierre el primer commit. Cada una dice qué decide pron, qué queda a cargo de la aplicación que monta a pron sobre un mundo, y por qué.

## 1. La gramática es artesanal, determinista y dirigida por el léxico

**Decisión.** La superficie es un parser de patrones escrito en pron, sin spaCy, sin CFG generada, sin LLM. Trabaja así:

1. tokeniza por espacios y puntuación, conservando comillas y dos puntos como marcas de literal;
2. clasifica cada token contra el léxico de la proyección (05) por **formas listadas**, no por morfología: el alias de "reserva" lista `reserva, reservas`; el de "confirmar" lista `confirma, confirmá, confirmala, confirmarla`. Un token sin forma listada es desconocido y va al calce aproximado;
3. aplica un conjunto pequeño y fijo de patrones de constituyente, los mismos para todo mundo: `det + término [+ "de" + nombre propio]`, `término + preposición + valor`, `verbo + objeto`, `referente + verbo`, `verbo + campo + literal`, coordinación con "y". Cuando dos patrones calzan, se mantienen las dos lecturas hasta el paso 4 (09);
4. no hay puntuación de probabilidad: una oración calza con uno, varios o ningún patrón, y eso es único, ambiguo o missing.

**Por qué.** La traza de un turno tiene que ser reproducible: correr las mismas direcciones en la shell da lo mismo. Un parser estadístico rompe eso, y un LLM en la superficie convierte a pron en otro operador. La morfología automática del español ahorra listar formas, pero mete errores que nadie puede auditar; listar formas en el alias es trabajo que se ve y se corrige.

**A cargo de la aplicación.** Nada. Un mundo agrega palabras por alias; no toca el parser.

**Límite declarado.** Oraciones que no calzan con los patrones fijos son missing con la lista de patrones como pista ("puedo entender: *crea un X que…*, *cambia el Y de X a…*"). Si un mundo necesita construcciones nuevas, se agregan patrones generales a pron, nunca patrones por mundo.

## 2. El calce aproximado es un puerto, con un fallback sin red

**Decisión.** pron define un puerto `Embedder` con una sola operación, `embed(textos) → vectores`, y usa similitud coseno. La aplicación inyecta la implementación al abrir la sesión. Sin implementación inyectada, pron usa similitud de cadenas (`difflib`, sobre formas normalizadas sin acentos) y lo dice en la traza. Así "no tengo *patio*, ¿querías *terraza*?" funciona siempre, mejor con embeddings, peor sin ellos, nunca nada.

Los vectores del léxico se calculan una vez por combinación de `hash_mundo`, nombre de proyección e identificador del `Embedder` (el puerto expone `id()`, por ejemplo `difflib` o `e5-small-v2`), y se guardan en `.pron/lexicon.<hash_mundo>.<proyeccion>.<embedder>.json` en la raíz del mundo: un artefacto derivado, ignorado por git, reconstruible, fuera del store de sldb porque no es un documento. Umbral de sugerencia y cantidad de cercanos (por defecto tres) van en el `ProjectionDoc`, campo `matching`, para que un mundo estricto sugiera menos.

**Por qué.** El modelo de embeddings es una elección de la aplicación (local, remoto, el que ya use el producto), no de pron. Y pron tiene que ser probable sin red: los tests del orden de construcción corren con el fallback.

**A cargo de la aplicación.** Elegir e inyectar el `Embedder`.

## 3. Las fechas y horas relativas las normaliza la superficie, con reloj de sesión

**Decisión.** En el paso 2, un literal en posición de campo de tipo fecha u hora pasa por un normalizador determinista de pron: nombres de día → la próxima ocurrencia desde la fecha de la sesión, "hoy", "mañana", "pasado mañana", "el 11", "11/9", "a las 21" → `21:00`, "y media" → `:30`. La sesión recibe `now` y zona horaria al abrirse; sin eso, usa el reloj del sistema y lo registra. La interpretación guarda el texto original y el valor normalizado, y el `MoveDoc` los dos. Un caso ambiguo ("el viernes" siendo viernes: ¿hoy o el próximo?) es una pendiente de dato con las dos opciones.

Qué campos son fecha u hora lo dice el alias del campo (`kind: date | time`) o el tipo Python si el modelo usa `date`/`time`; un `str` sin alias de tipo no se normaliza.

**Por qué.** Es la única normalización de literales que casi todo mundo necesita, y dejarla a un LLM operador rompe la reproducibilidad. Todo lo demás (monedas, unidades) es del mundo, por alias o por tipo.

**A cargo de la aplicación.** Pasar `now` y zona horaria.

## 4. El ingest unificado de kgdb es previo y es de kgdb

**Decisión.** No existe. Es el prerrequisito de 08 §kgdb, y se hace en kgdb antes del paso 6 del orden de construcción, en este orden: los modelos `RelationTypeDoc` y `RelationDoc` con `condition` a `kgdb.models`; el comando `kgdb ingest --store <.sldb>` que corre el `semantic-export` de sldb por librería, lee los `RelationDoc` con `load_runtime_documents` filtrando por tag `type.relation.instance` (la misma vía que `sldb serve /graph`, no el runtime del store), y arma el snapshot de 10 §2.3.

Mientras no exista, pron construye y prueba los pasos 1 a 5 sin kgdb, y buena parte del 6, porque **toda verificación sobre relaciones autoradas se hace contra sldb, no contra el grafo** (03 §Qué se verifica dónde): existencia de una arista, cardinalidad, transición legal y condición son consultas a `st.{RelationDoc}` y al sujeto. kgdb es la superficie de lectura: `edges_from`, `edges_to`, los links en prosa, el recorrido por tags y alcances. Sin grafo, o con grafo viejo, las lecturas de aristas autoradas caen a sldb con la traza diciéndolo, y solo quedan sin respuesta las aristas de links en prosa y los recorridos. pron **no** ensambla aristas por su cuenta mientras tanto, ni llamando a `assemble_authored_graph` desde su proyector: la regla 4 del índice vale también en el intervalo.

**Por qué.** Un ensamblador provisorio en pron sería exactamente el código que la v1 tenía de más.

**A cargo de la aplicación.** Nada; es trabajo en kgdb, chico y acotado.

## 5. Un turno lee `hash_mundo` dos veces y cada escritura verifica su documento

**Decisión.** El turno toma `hash_mundo` al empezar (antes del paso 2) y lo vuelve a leer justo antes de ejecutar (después del paso 6). Si cambió, el turno no ejecuta: recarga léxico y proyección, registra un movimiento externo, y repite la comprensión una vez desde el paso 2 con la misma oración. Si vuelve a cambiar, responde "el mundo está cambiando, repetí la oración" y registra.

Además, cada escritura por campo compara el `hash_c` esperado del documento con el actual antes de escribir; si difiere, esa escritura no se hace y se reporta con el valor que encontró. El esperado es el `hash_c` leído en el paso 4, y **después de cada escritura propia se reemplaza por el que sldb deja en el índice** al terminar `save_payload`; así "cambiá personas y ponele una nota" hace dos escrituras sobre el mismo documento sin rechazarse a sí misma. Es la única protección; no hay bloqueo de documentos.

**Por qué.** Un mundo con editor y agente expansor tiene escritores concurrentes de verdad. La ventana entre comprender y ejecutar es corta, pero existe, y el costo de dos lecturas de índice es nulo.

**A cargo de la aplicación.** Serializar escritores si quiere garantías más fuertes.

## 6. La identidad la trae la aplicación; pron solo la usa y la registra

**Decisión.** Al abrir una sesión, la aplicación pasa `speaker`: un identificador opaco y, si el hablante es un objeto del mundo, su dirección (`Cliente:cliente-ana-rojas`, `Usuario:jp`). pron no autentica ni verifica. "yo", "mi", "al usuario" resuelven a esa dirección; sin dirección, son missing con "no sé quién sos en este mundo". Todo `MoveDoc` lleva `speaker`, y el `ProjectionDoc` se elige por sesión, así que quién puede afirmar o crear es una decisión de la aplicación al elegir la proyección del hablante.

**Por qué.** pron es una superficie; la identidad y los permisos de personas son del producto que la monta.

## 7. Sin rollback: validación previa, registro por dirección y un verbo "deshacer" explícito

**Decisión.** Tres cosas en vez de una transacción:

- **Validación previa.** Antes de la primera escritura de un movimiento con varias, pron valida todas: para cada dirección calcula el payload nuevo y corre el roundtrip de sldb (`validate_model_data_roundtrip`) sin escribir. Lo que fallaría por forma falla antes de tocar nada. Lo que puede fallar después es solo el disco o un cambio concurrente (§5).
- **Registro por dirección.** El `MoveDoc` lleva, por escritura, `hecha | no hecha` y el valor anterior. La respuesta dice cuáles quedaron.
- **Deshacer, como verbo.** "deshacé el último movimiento" es un verbo de acción del kernel que aplica las escrituras inversas registradas en ese `MoveDoc`. Las inversas son: de "cambiar", el valor anterior por campo; de "crear", `docs untrack` (el archivo queda en disco, fuera del store); de "olvidar" y de negar una relación, `docs track` del mismo archivo con el mismo nombre, que el `MoveDoc` guardó; de "agregar", quitar el ítem; de "limpiar", la lista anterior. Restaurar un campo de estado **no** pasa por una transición inversa: deshacer no es una transición nueva, es volver al estado que el mundo tenía, y se registra como `deshacer` referenciando al movimiento original (07). Un mundo que no quiera eso quita `deshacer` de `actions`. Solo deshace el último movimiento con escritura del mismo `speaker`, y solo si los documentos no cambiaron después (mismo `hash_c` que dejó el movimiento); si cambiaron, dice cuáles y no toca esos. Un refresh no se deshace: se vuelve a correr.

**Por qué.** sldb escribe documentos independientes y no tiene transacciones; simularlas en pron sería otra capa de verdad. Compensar de forma explícita y visible es coherente con "pron no deshace": no deshace solo, deshace cuando se lo piden y muestra qué hizo.

**A cargo de la aplicación.** Nada.

## Resumen

| pregunta | pron decide | la aplicación aporta |
|---|---|---|
| parser | patrones fijos, formas listadas en alias, sin estadística ni LLM | alias con sus formas |
| calce aproximado | puerto `Embedder`, coseno, fallback `difflib`, caché por `hash_mundo` | la implementación del puerto |
| fechas relativas | normalizador determinista con reloj de sesión | `now` y zona horaria |
| ingest de kgdb | esperar a kgdb; pasos 1–5 sin grafo; nunca ensamblar en pron | — |
| cambio durante el turno | `hash_mundo` al inicio y antes de ejecutar; `hash_c` por escritura | serializar escritores si quiere más |
| identidad | `speaker` opaco más dirección opcional; se registra, no se verifica | quién habla y con qué proyección |
| fallo parcial | validación previa, registro por dirección, verbo "deshacer" | — |
