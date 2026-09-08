# 03 · Verbos transitivos

## Qué es un verbo

Un verbo transitivo es un tipo de relación entre dos sustantivos. Lo declara kgdb con su modelo `RelationTypeDoc`:

| campo | significado gramatical |
|---|---|
| `name` | el verbo (`implements`, `grounded_by`, `flows_to`) |
| `source_types` | qué clases pueden ser sujeto |
| `target_types` | qué clases pueden ser objeto |
| `direction` | si la oración se puede leer al revés |
| `cardinality` | cuántos objetos admite un sujeto |
| eje del predicado | qué pregunta responde: HOW, WHY, WHAT, PROVENANCE, WHEN_WHERE |

Su instancia es un `RelationDoc`: `source_id`, `target_id`, `relation_type`, y opcionalmente una condición. Es una arista autorada, y es un documento más del store de sldb.

Los dos modelos son de kgdb. pron los registra en su mundo para poder autorarlos; sldb los guarda; el ingest de kgdb los ensambla en el grafo. pron no toca kgdb para escribir.

## Leer un verbo

"¿Qué implementa X?" es:

1. resolver X a una dirección (02);
2. verificar que `implements` está en la proyección y que la clase de X está en `source_types`;
3. `edges_from(nodo(X), implements)` en kgdb;
4. mostrar los targets con su nombre natural.

"¿Quién implementa X?" es lo mismo con `edges_to`. "¿Puede X pasar a Y?" es si existe la arista `flows_to` de X a Y y, si trae condición, si la condición se cumple. kgdb no sabe qué es una transición; solo tiene la arista.

## Condiciones

Una condición es un predicado `--where` de sldb guardado en el campo `condition` del `RelationDoc`. Se evalúa con sldb, nunca en pron, sobre el **sujeto de la oración en su estado actual**: la arista es legal para ese sujeto si `find <alcance del sujeto> --where <condición>` devuelve su dirección. Una condición puede nombrar campos del sujeto entre llaves, `capacidad >= {personas}`, y entonces se evalúa sobre el objeto con los valores del sujeto sustituidos antes de llamar a sldb. Una arista sin condición es legal siempre que exista.

Una **transición** es el caso en que el verbo es "cambiar el campo de estado": la oración "confirma la reserva" es `fields update …/estado "confirmada"`, permitida solo si existe una arista `pasa_a` desde el estado actual al nuevo y su condición se cumple sobre la reserva. Los estados son documentos de un modelo `Estado`, las transiciones son `RelationDoc` entre ellos, y el objeto que transiciona solo cambia un campo.

## Afirmar un verbo

"X implementa Y" es:

1. resolver X e Y;
2. verificar contra el `RelationTypeDoc`: la clase de X en `source_types`, la de Y en `target_types`, la cardinalidad no violada;
3. `docs create --model RelationDoc` con `source_id`, `target_id`, `relation_type`;
4. refresh (04). La arista aparece cuando el ingest de kgdb vuelve a correr.

Si el sujeto no existe todavía y la oración trae sus campos ("reservale una mesa a Ana": la reserva no existe), el verbo transitivo se lee como *crear el sujeto y afirmar el verbo* en el mismo movimiento. Exige los dos permisos de la proyección: `crear` en `actions` y `afirmar` en la relación.

Negar un verbo, "X ya no implementa Y", es `docs untrack` del `RelationDoc` correspondiente y refresh. Si la arista no viene de un `RelationDoc` sino de un link en prosa (abajo), pron no la niega: responde dónde está escrita, documento y sección, y que hay que editar ese texto.

## Los verbos que ya existen sin declararse

Los links con predicado dentro del texto, `[implements:: [[x]]]`, son aristas autoradas en línea. sldb los recupera con `docs recover` y les da el eje del predicado registrado. pron los trata como verbos transitivos leídos, no escritos: para afirmar uno se escribe un `RelationDoc`, no se edita prosa. Cada arista leída dice de dónde viene, `RelationDoc` o link, y eso decide si se puede negar por oración.

## Leer y afirmar son dos permisos

La proyección (01) lista cada tipo de relación con un modo: `leer` o `leer y afirmar`. Con `leer`, "¿qué implementa X?" funciona y "X implementa Y" responde "en esta sesión puedo decirte qué implementa, no afirmarlo". Ocultar los verbos de acción no es lo mismo: afirmar un verbo transitivo es una escritura propia, con su propio permiso.

## El eje es lo que contesta las preguntas

Un verbo con eje WHY o PROVENANCE responde "¿por qué?"; uno con eje HOW responde "¿cómo?"; uno WHAT, "¿qué es?". La superficie usa el eje para elegir qué aristas leer ante una pregunta de ese tipo (07).

## Invariantes

- Ninguna arista de dominio existe en kgdb sin un `RelationDoc` o un link con predicado que la origine.
- pron nunca ensambla aristas. Si el grafo no tiene la arista, la respuesta es "no está registrado", y la traza dice cuándo fue el último refresh.
- Un verbo no verificado contra `source_types` y `target_types` no se escribe.
