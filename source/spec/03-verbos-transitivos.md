# 03 · Verbos transitivos

## Qué es un verbo

Un verbo transitivo es un tipo de relación entre dos sustantivos. Lo declara sldb con su modelo `RelationTypeDoc`, en un documento cuyo nombre en el store es `rt-<name>` (`rt-booked_by`, `rt-implements`): en sldb el nombre de un documento es único en todo el store, no por modelo, y el prefijo evita que un tipo de relación choque con cualquier otro documento que se llame como él. El campo `name` va sin prefijo, y es el que dice el hablante:

| campo | significado gramatical |
|---|---|
| `name` | el verbo (`implements`, `grounded_by`, `flows_to`) |
| `source_types` | qué clases pueden ser sujeto |
| `target_types` | qué clases pueden ser objeto |
| `direction` | si la oración se puede leer al revés |
| `cardinality` | cuántos objetos admite un sujeto |
| eje del predicado | qué pregunta responde: HOW, WHY, WHAT, PROVENANCE, WHEN_WHERE |

Su instancia es un `RelationDoc`: `source_id`, `target_id`, `relation_type`, y opcionalmente una condición. Es una arista autorada, y es un documento más del store de sldb.

Los dos modelos son de sldb. pron los registra en su mundo para poder autorarlos; sldb los guarda y mantiene su propio índice de aristas a partir de ellos — un índice del store, no un sistema aparte. pron nunca escribe ese índice: lo compone sldb, del lado de abajo, cada vez que se lee.

## Leer un verbo

"what does X implement?" es:

1. resolver X a una dirección (02);
2. verificar que `implements` está en la proyección y que la clase de X está en `source_types`;
3. `edges_from(nodo(X), implements)`, contra el índice de aristas de sldb;
4. mostrar los targets con su nombre natural.

"who implements X?" es lo mismo con `edges_to`. "can X move to Y?" es si existe la arista `flows_to` de X a Y y, si trae condición, si la condición se cumple. El índice de aristas no sabe qué es una transición; solo tiene la arista.

## Condiciones

Una condición es un predicado `--where` de sldb. Se declara en el `RelationTypeDoc`, campo `condition`, y vale para todas las aristas de ese tipo; un `RelationDoc` puede traer la suya y entonces reemplaza a la del tipo. Se evalúa con sldb, nunca en pron, sobre el **sujeto de la oración en su estado actual**: la arista es legal para ese sujeto si `find <alcance del sujeto> --where <condición>` devuelve su dirección. Una condición puede nombrar campos del sujeto entre llaves, `capacity >= {party_size}`, y entonces se evalúa sobre el objeto con los valores del sujeto sustituidos antes de llamar a sldb. Una arista sin condición es legal siempre que exista.

Después de una escritura, pron reevalúa las condiciones de las aristas que salen del documento escrito **y de las que entran a él**: bajar la capacidad de una mesa afecta la `assigned_to` que apunta a esa mesa, aunque la condición la lea la reserva. El costo está acotado por las aristas del documento; el resultado es un aviso, nunca una acción (04).

Con varios stores en la proyección (01), las aristas se buscan en todos y un `RelationDoc` nuevo va al primero, el mismo donde la sesión crea documentos; sus extremos llevan el id con store (`A:Reserva:doc`). El índice de aristas de sldb ya federa: recorre los stores enlazados y califica sus ids (`A:Modelo:doc`), así que un `RelationDoc` local puede apuntar a un documento de otro store y `edges_from`/`edges_to` lo resuelven igual, sin distinguir de dónde viene cada extremo.

Una **transición** es el caso en que el verbo es "cambiar el campo de estado": la oración "confirm the reservation" es `fields update …/status "confirmed"`, permitida solo si existe una arista `transitions_to` desde el estado actual al nuevo y su condición se cumple sobre la reserva. Los estados son documentos de un modelo `State`, las transiciones son `RelationDoc` entre ellos, y el objeto que transiciona solo cambia un campo.

## Afirmar un verbo

"X implementa Y" es:

1. resolver X e Y;
2. verificar contra el `RelationTypeDoc`: la clase de X en `source_types`, la de Y en `target_types`, la cardinalidad no violada;
3. `docs create --model RelationDoc` con `source_id`, `target_id`, `relation_type`;
4. refresh (04) — el `docs create` ya deja el shard de aristas del `RelationDoc` al día en la misma operación; la arista es visible sin esperar nada más. El refresh del turno sigue corriendo igual, pero no tiene trabajo salvo que algo haya tocado el store por fuera de sldb.

Crear el sujeto y afirmar el verbo en un mismo movimiento ("book Ana a table") no es un comportamiento implícito del verbo: lo declara un alias compuesto, un `(move …)` con sus pasos y huecos (05). Cada paso exige su permiso: `create` en `actions`, `assert` en la relación.

Negar un verbo, "X ya no implementa Y", es `docs untrack` del `RelationDoc` correspondiente y refresh. Si la arista no viene de un `RelationDoc` sino de un link en prosa (abajo), pron no la niega: responde dónde está escrita, documento y sección, y que hay que editar ese texto.

## Qué se verifica dónde

Las relaciones autoradas son documentos: su verdad está en sldb, y el índice de aristas es una vista derivada de esos mismos documentos — no un segundo sistema con su propio ciclo de vida.

| pregunta | dónde | cómo |
|---|---|---|
| ¿aplica el verbo a estas clases? | sldb | `get st.{RelationTypeDoc}.<verbo>` · `source_types`, `target_types` |
| ¿existe ya esta arista? | sldb | `find st.{RelationDoc} --where 'source_id = "…"'` ∩ `--where 'relation_type = "…"'` ∩ target |
| ¿la cardinalidad lo permite? | sldb | la misma consulta, contando |
| ¿es legal la transición? | sldb | la arista `transitions_to` como `RelationDoc` desde el estado actual, y su condición sobre el sujeto |
| ¿se cumple la condición? | sldb | `find <alcance> --where <condición>` |
| ¿qué implementa X? ¿quién? | sldb | `edges_from`, `edges_to` sobre el índice de aristas |
| aristas de links en prosa, recorridos por tags o alcance | sldb | lo mismo: el índice ya las incluye |

Cada escritura de sldb (`create`, `save payload`, `untrack`, `stores update`) deja al día el shard de aristas del documento que tocó, en la misma operación: leer una arista nunca dispara una reconstrucción ni cae a una segunda puerta. Una edición de un documento por **fuera** de sldb (un archivo tocado a mano) no se refleja en el índice hasta el próximo refresh — `edges_from`/`edges_to` pueden devolver la arista vieja durante esa ventana; el índice lo sabe (`stale`, 04) pero no lo esconde en la lectura. Es el mismo riesgo que ya existe para cualquier otro campo de un documento editado por fuera de sldb (07 §5), no uno nuevo de las aristas. Ninguna escritura queda bloqueada por eso, porque ninguna escritura depende de que el índice esté al día.

## Los verbos que ya existen sin declararse

Los links con predicado dentro del texto, `[implements:: [[x]]]`, son aristas autoradas en línea. sldb los recupera con `docs recover` y les da el eje del predicado registrado. pron los trata como verbos transitivos leídos, no escritos: para afirmar uno se escribe un `RelationDoc`, no se edita prosa. Cada arista leída dice de dónde viene, `RelationDoc` o link, y eso decide si se puede negar por oración.

## Leer y afirmar son dos permisos

La proyección (01) lista cada tipo de relación con un modo: `read` o `read and assert`. Con `read`, "what does X implement?" funciona y "X implements Y" responde "in this session I can tell you what it implements, not assert it". Ocultar los verbos de acción no es lo mismo: afirmar un verbo transitivo es una escritura propia, con su propio permiso.

## El eje es lo que contesta las preguntas

Un verbo con eje WHY o PROVENANCE responde "why?"; uno con eje HOW responde "how?"; uno WHAT, "what is it?". La superficie usa el eje para elegir qué aristas leer ante una pregunta de ese tipo (07).

## Invariantes

- Ninguna arista de dominio existe en el índice de sldb sin un `RelationDoc` o un link con predicado que la origine.
- pron nunca ensambla aristas: las compone sldb. Si el índice está viejo (un documento tocado por fuera de sldb), la lectura puede devolver una arista desactualizada hasta el próximo refresh, y `stale` (04) lo dice.
- Un verbo no verificado contra `source_types` y `target_types` no se escribe.
