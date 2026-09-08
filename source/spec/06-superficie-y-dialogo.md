# 06 · Superficie y diálogo

## La superficie

La superficie recibe una oración en lenguaje natural y produce una **interpretación**: un registro con esta forma, que es también lo que va al ledger.

```yaml
forma: nominal | transitiva | accion
sujeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad: una | conjunto}
verbo:   {nombre, tipo: transitivo | accion, eje, modo: read | assert}   # si hay verbo
objeto:  {alcance, predicados: [], determinante, direcciones: [], cardinalidad}   # si hay objeto
campo:   name de campo                     # verbos de acción sobre un campo
valor:   literal | payload                   # lo que un verbo de acción escribe
huecos:  []                                  # constituyentes sin resolver
salida:  unico | ambiguo | missing
```

Cómo se llega ahí son seis pasos fijos, desarrollados con una conversación entera en 09: segmentar; clasificar cada palabra contra el léxico (término, referente, literal, nombre propio, desconocida); armar interpretaciones parciales; consultar el mundo por cada frase nominal; verificar tipos contra el `RelationTypeDoc` o el esquema del modelo; decidir la salida. El mundo interviene en los pasos 2, 4 y 5 y en ningún otro.

Qué contiene cada construcción admitida:

| construcción | forma | qué lleva |
|---|---|---|
| "the atoms of pron" | nominal | sujeto con alcance y predicados; verbo de lectura implícito |
| "what does X implement?" | transitiva, modo `read` | sujeto resuelto, verbo, objeto interrogado |
| "X implements Y" | transitiva, modo `assert` | sujeto y objeto resueltos, verbo |
| "change the synopsis of X to …" | acción | sujeto resuelto, `campo: synopsis`, `valor: literal` |
| "create an atom saying …" | acción | `alcance: Atom`, `valor: payload` con los campos capturados; los obligatorios que falten son huecos y abren una pendiente por campo |
| "add the tag T to them" | acción | sujeto = referente plural con N direcciones, `campo: tags`, `valor: T` |
| "change it to 9 and add a note" | acción, dos escrituras | mismo sujeto, dos pares `campo`/`valor`, un movimiento |
| "book Ana a table" | compuesta, por alias `compose` (05) | pasos declarados en el alias: crear la reserva con los literales, afirmar `de`, afirmar `assigned_to`; cada paso con sus ranuras resueltas |
| "confirm it" | acción por alias | `campo: status`, `valor: confirmed`, verificada como transición (03) |

Un sujeto plural en un verbo de acción es N escrituras en un solo movimiento y un solo refresh.

## Coordinación

"and" une dos partes en **un solo movimiento** siempre, tengan el mismo sujeto o no, sean verbos de acción, transitivos o un `compose`. La regla que lo permite es que ninguna verificación depende del grafo (03 §Qué se verifica dónde): la segunda parte puede referirse a lo que la primera crea (`$created`, o "it" apuntando al documento recién creado, cuya dirección se conoce en cuanto `docs create` termina) sin necesitar un refresh en el medio. Un movimiento es una interpretación, sus escrituras en orden y un refresh al final.

Dos consecuencias: si cualquier parte es ambigua o missing, la oración entera lo es y nada se ejecuta; y "create a client named X and book her a table" es un movimiento de cuatro escrituras, no dos turnos.

Y devuelve la respuesta en natural, con la traza disponible: las direcciones exactas, el verbo, las aristas o la escritura. La traza es corta porque cada paso es una llamada a sldb o kgdb, no un razonamiento.

Quien habla puede ser una persona, un LLM operador u otro producto. Para todos la interfaz es la misma oración. Un LLM operador es un hablante que sabe su mundo por el léxico listado (05), no por prompt.

## Las tres salidas del grounding

| salida | condición | qué hace pron |
|---|---|---|
| único | cada frase nominal tiene la cardinalidad que su determinante permite: una dirección para "the table", un conjunto (incluso vacío) para "the tables" | ejecuta el verbo, responde, registra |
| ambiguo | una frase nominal singular dio más de una dirección, o un referente no tiene un antecedente único | guarda candidatos y la interpretación con hueco, pregunta "¿cuál?", registra |
| missing | un término no está en la proyección, o un nombre propio dio cero direcciones | busca cercanos (05), registra el hueco, responde "no existe, ¿querías…?", termina el turno |

Con dos frases ambiguas en la misma oración se pregunta por la primera en orden de aparición; la segunda queda como hueco y se pregunta después, en la misma pendiente.

Qué pasa después de un missing no es de pron. Puede ser que el hablante reformule, o que un agente expansor agregue lo que falta al mundo. Una excepción chica: si la oración siguiente es un fragmento sin verbo que calza con el hueco registrado ("on the terrace" tras un missing en `zone`), se lee como corrección y la oración anterior se reinterpreta entera con el hueco relleno. No es una pendiente: el turno missing ya terminó y quedó registrado.

## El diálogo

El único estado propio de pron por sesión es si hay una pregunta pendiente. Es la conversación estilo SHRDLU:

- **libre**: sin pendiente. Una oración única o missing vuelve a libre. Una ambigua pasa a pendiente.
- **pendiente**: hay una interpretación con un hueco y la próxima oración se prueba primero como respuesta. Hay dos clases de pendiente:
  - **de elección**: el hueco tiene candidatos guardados (una frase nominal ambigua, un referente con varios antecedentes);
  - **de dato**: el hueco es un campo obligatorio sin valor (un `create` al que le falta `phone`), y lo que se espera es un literal del tipo de ese campo.

Reglas de continuación, en este orden:

1. Es **respuesta** si calza con la clase de la pendiente. Para una pendiente de elección, una designación de candidato: un número, un nombre, "the first one", "the X one", "none"; "X" se compara con los nombres naturales de los candidatos con los mismos embeddings del léxico, y esto no contradice la regla de que un calce aproximado nunca se ejecuta (05): aquí el conjunto es cerrado y ya fue mostrado, y un calce que no es único deja la pendiente como está. Para una pendiente de dato, un literal que cabe en el tipo del campo. Un calce único rellena el hueco y completa el turno original; "none" cancela la pendiente.
2. Es **orden nueva** si tiene verbo, o si es una frase nominal con determinante. Se descarta la pendiente, se registra el descarte, y la oración se interpreta desde cero.
3. Si no es ninguna de las dos, o la designación calza con más de un candidato, **sigue pendiente**: pron repite los candidatos y lo dice.

Una pendiente dura hasta que se contesta, se cancela o se descarta por una orden nueva. No caduca sola.

Los referentes se resuelven en el diálogo antes de armar direcciones, por número y por clase:

- "that X", "it", "the same", "the previous one": la última dirección **singular** cuya clase es X, o la clase que pide el verbo. Un conjunto de más de un elemento no califica como antecedente singular; un conjunto de exactamente uno, sí.
- "those", "them", "all of them": el último **conjunto**. Una dirección sola no califica.
- Si el turno anterior dejó varias direcciones singulares de la misma clase (por ejemplo, los dos targets de un verbo leído), "that X" es ambiguo y se pregunta.
- "me", "my", "the user": la identidad de la sesión.

## Lo que la superficie no hace

- No resuelve sustantivos: los pide a sldb.
- No decide si un verbo aplica: lo verifica contra el `RelationTypeDoc`.
- No ejecuta nada por calce aproximado.
- No guarda más estado que la pendiente y los referentes recientes.

## Invariantes

- Toda oración termina en un movimiento registrado (07), incluidas las ambiguas y las missing.
- Hay a lo sumo una pendiente por sesión; una orden nueva la reemplaza.
- La traza de un turno es reproducible: correr sus direcciones y su escritura en la shell da el mismo resultado.
