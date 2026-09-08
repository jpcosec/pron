# pron — especificación

pron es un SHRDLU sobre un mundo que ya existe: los documentos de sldb son los objetos, los modelos de relación de kgdb son los verbos transitivos, y las escrituras de sldb son los verbos de acción. pron no resuelve, no filtra, no declara verbos ni guarda estado del mundo. Convierte oraciones en direcciones, aristas y escrituras, sostiene el diálogo cuando una oración no alcanza, y deja rastro de cada movimiento.

La v1 (código, KB, store, tests) vive entera en la rama `v1-code-and-kb` y el tag `v1-frozen`. Esta especificación se escribió después de leer cómo funcionan sldb y kgdb de verdad, y reemplaza a la v1 en vez de extenderla.

## Documentos

| # | documento | contesta |
|---|---|---|
| 01 | [El mundo](01-mundo.md) | qué es un mundo, qué lo declara, qué es una proyección |
| 02 | [Sustantivos](02-sustantivos.md) | cómo una frase nominal se vuelve una dirección de sldb |
| 03 | [Verbos transitivos](03-verbos-transitivos.md) | qué es un verbo, quién lo declara, cómo se lee y cómo se afirma |
| 04 | [Verbos de acción](04-verbos-de-accion.md) | el kernel: las cuatro escrituras y el refresh |
| 05 | [Léxico y proyección](05-lexico-y-proyeccion.md) | de dónde salen las palabras, qué son los anchors, qué hacen los embeddings |
| 06 | [Superficie y diálogo](06-superficie-y-dialogo.md) | la oración, sus tres salidas, la pendiente y los referentes |
| 07 | [Ledger](07-ledger.md) | qué se registra y cómo se contesta "¿por qué?" |
| 08 | [Prerrequisitos y orden](08-prerequisitos-y-orden.md) | qué falta en sldb y kgdb, en qué orden se construye, qué lints lo cuidan |
| 09 | [Una conversación, paso a paso](09-una-conversacion.md) | ocho oraciones sobre un mundo externo (reservas de un restaurante): creación, asignación, transición con condición, ambigüedad, missing, "¿por qué?" |

Si hay que leer uno solo, es el 09: fija con ejemplos cada decisión que los otros enuncian.

Las vistas spec2viz en [`views/spec2viz`](../../views/spec2viz) son la proyección gráfica de estos documentos. Cuando difieran, manda el spec.

## Vocabulario fijo

- **Mundo**: un store de sldb con sus stores enlazados, sus modelos y sus predicados. Se declara en `store_index.yaml`.
- **Sustantivo**: una dirección `st.{Modelo+}.doc.campo.sub` más un predicado `--where`.
- **Verbo transitivo**: un `RelationTypeDoc` de kgdb. Su instancia, un `RelationDoc`, es una arista.
- **Verbo de acción**: una escritura de sldb: crear documento, cambiar campo, agregar a lista, refrescar.
- **Proyección**: la parte del mundo que una sesión puede nombrar.
- **Movimiento**: un turno completo: oración, direcciones, verbo, resultado.

## Reglas que no se negocian

1. pron no abre markdown. Lee y escribe por dirección; sldb es dueño del archivo.
2. pron no tiene cascada de resolución. Un sustantivo lo responde sldb con una dirección y un `--where`.
3. pron no declara verbos. Los declara kgdb; sldb los guarda; el ingest de kgdb los ensambla.
4. pron no escribe en kgdb. kgdb es derivado y de solo lectura; cambia cuando el proyector lo reconstruye.
5. Todo lo que pron sabe de su mundo está en documentos de su propio store. No hay conocimiento en código.
