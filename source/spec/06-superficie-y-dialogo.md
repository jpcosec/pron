# 06 · Superficie y diálogo

## La superficie

La superficie recibe una oración en lenguaje natural y produce una de dos formas:

- `(alcance, predicado)` para una frase nominal: una dirección de sldb (02);
- `(verbo, sujeto, objeto)` para una oración con verbo: transitivo (03) o de acción (04), con sujeto y objeto ya resueltos a direcciones.

Y devuelve la respuesta en natural, con la traza disponible: las direcciones exactas, el verbo, las aristas o la escritura. La traza es corta porque cada paso es una llamada a sldb o kgdb, no un razonamiento.

Quien habla puede ser una persona, un LLM operador u otro producto. Para todos la interfaz es la misma oración. Un LLM operador es un hablante que sabe su mundo por el léxico listado (05), no por prompt.

## Las tres salidas del grounding

| salida | condición | qué hace pron |
|---|---|---|
| único | cada sustantivo dio una dirección | ejecuta el verbo, responde, registra |
| ambiguo | un sustantivo con "el" dio más de una | guarda candidatos y la oración con hueco, pregunta "¿cuál?", registra |
| missing | una palabra no está en la proyección, o el sustantivo dio cero | busca cercanos (05), registra el hueco, responde "no existe, ¿querías…?", termina el turno |

Qué pasa después de un missing no es de pron. Puede ser que el hablante reformule, o que un agente expansor agregue lo que falta al mundo.

## El diálogo

El único estado propio de pron por sesión es si hay una pregunta pendiente. Es la conversación estilo SHRDLU:

- **libre**: sin pendiente. Una oración única o missing vuelve a libre. Una ambigua pasa a pendiente.
- **pendiente**: hay candidatos guardados y una oración con hueco. La próxima oración se interpreta primero como respuesta: si calza con un candidato, se rellena el hueco y se completa el turno original; si no calza, sigue pendiente y pron lo dice; si es una orden nueva, se descarta la pendiente y se registra el descarte.

Los referentes ("ese", "la anterior", "el mismo", "al usuario") se resuelven en el diálogo antes de armar direcciones: apuntan a direcciones de turnos anteriores o a la identidad de la sesión.

## Lo que la superficie no hace

- No resuelve sustantivos: los pide a sldb.
- No decide si un verbo aplica: lo verifica contra el `RelationTypeDoc`.
- No ejecuta nada por calce aproximado.
- No guarda más estado que la pendiente y los referentes recientes.

## Invariantes

- Toda oración termina en un movimiento registrado (07), incluidas las ambiguas y las missing.
- Una pendiente sobrevive solo hasta la siguiente oración.
- La traza de un turno es reproducible: correr sus direcciones y su escritura en la shell da el mismo resultado.
