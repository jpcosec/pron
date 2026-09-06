# KB System Clarifications

## Estado
Clarificaciones sobre `KB_SYSTEM_SPEC.md`

## Propósito
Este documento explicita decisiones de diseño que en el spec principal estaban implícitas o podían leerse de forma ambigua.

No reemplaza el spec principal.
Lo complementa.

---

## 1. Sobre el propósito del hash

El hash importante en este sistema es el **hash de la fuente**.

### `source_hash_sha256`

Su propósito no es probar integridad del sample como documento editable.

Su propósito es:

- ligar la biopsia a una **versión exacta** del documento fuente
- conservar una prueba fuerte aunque el sample:
  - se renombre
  - se mueva
  - se regenere
  - se pierda como archivo local
- permitir validación contra el artefacto original correcto

### Consecuencia

La prueba principal del sistema está anclada en:

- el artefacto fuente
- su hash
- los datos de anchor
- el texto exacto recuperable

No está anclada en la persistencia material del archivo sample.

## 2. El sample no es la prueba última

El sample es una **superficie derivada de trabajo**.

Sirve para:

- fijar un corte trazable
- facilitar inspección humana
- permitir anotación
- servir de puente hacia el átomo

Pero la garantía fuerte del sistema no depende de que el archivo sample permanezca intacto o siquiera presente.

La garantía fuerte depende de poder decir:

- de qué fuente exacta salió
- con qué hash
- con qué anchor
- qué texto exacto fue recortado
- cómo volver a encontrarlo

---

## 3. Sobre la validación del anchor

La validez del anchor no es solo descriptiva.

Debe existir una **prueba determinista de validación**.

## Invariante

Una biopsia válida debe permitir que el texto sampleado sea recuperado **exactamente** desde el documento fuente identificado por `source_hash_sha256`.

Esto implica que:

- el anchor no es solo metadata narrativa
- el anchor debe ser suficiente para reubicar el fragmento
- la validación debe fallar si el fragmento no puede recuperarse exactamente

## Qué debe validar el sistema

Dado:

- `source_path` o localizador equivalente
- `source_hash_sha256`
- método(s) de anchor
- `exact_quote`
- y datos auxiliares como `prefix`, `suffix`, `page_start`, `page_end`, `chapter`, `section`, `anchor_text`

el sistema debe poder comprobar de forma determinista que:

1. la fuente usada corresponde al hash declarado
2. el texto exacto declarado realmente existe en esa fuente
3. los datos de anchor alcanzan para volver a localizar ese fragmento

## Rol del anchor híbrido

El anchor híbrido existe para combinar:

- validación exacta
- reanclaje robusto
- navegación humana

No es una colección ornamental de campos.
Es un paquete de direccionamiento y verificación.

---

## 4. Sobre `sample_text_hash_sha256`

`sample_text_hash_sha256` no es el hash central del sistema.

Si se conserva, debe entenderse como metadata auxiliar del corte textual, no como la base de la prueba principal.

### Puede servir para

- registrar el texto extraído en un momento dado
- detectar cambios en una representación derivada del sample
- comparar regeneraciones del mismo corte

### No debe confundirse con

- la identidad de la fuente
- la prueba principal de provenance
- la validación de la versión correcta del PDF

La unión fuerte sigue siendo:

- fuente exacta
- hash de fuente
- anchor
- quote exacta recuperable

---

## 5. Sobre granularidad de los samples

La granularidad del sample **no debe normalizarse rígidamente**.

No hay valor central en imponer un tamaño uniforme a las biopsias.

## Lo que sí importa

Lo importante es:

- direccionabilidad
- grounding
- trazabilidad del átomo
- recuperabilidad exacta del fragmento

Un sample puede ser más corto o más largo según lo requiera el caso, siempre que:

- el fragmento quede bien anclado
- la recuperación exacta siga siendo posible
- el sample sostenga correctamente el átomo derivado

## Criterio práctico

No optimizar por uniformidad de tamaño.
Optimizar por calidad de anclaje y utilidad de grounding.

---

## 6. Sobre el modelo de átomo

El modelo de átomo de esta KB no debe entenderse como una entidad abstracta sin forma previa.

Está alineado con la disciplina de átomos ya usada en `deskops`, y extendido con provenance estructurado.

Referencias actuales:

- `/home/jp/proyectos/hum-ecosystem/tools/deskops/deskops/models/atom.py`
- `/home/jp/Upla/tutor_apoe/knowledge_models/docs.py`

## Idea central

Un átomo responde **una sola pregunta 5WH1+**.

Ejemplos:

- `what`
- `why`
- `how`
- `how_not`
- `when`
- `where`
- `for_whom`

## Consecuencia

La atomicidad no se define por longitud arbitraria.
Se define por la unidad epistemológica:

> un átomo = una respuesta estable a una sola pregunta 5WH1+

Eso permite:

- reuse
- composición
- indexación limpia
- menor mezcla de ideas

---

## 7. Sobre el tamaño del átomo

El átomo debe ser pequeño porque su utilidad depende de su composabilidad.

Si el átomo crece demasiado:

- mezcla varias preguntas
- se vuelve menos reusable
- se vuelve más difícil de enlazar
- pierde nitidez semántica

## Regla práctica

Si un contenido responde varias preguntas 5WH1+, probablemente no es un solo átomo.
Debe separarse en varios átomos relacionados.

## Profundidad sin inflación

La profundidad no se obtiene haciendo átomos más grandes.
La profundidad se obtiene por:

- composición de átomos
- relaciones entre átomos
- tags
- vistas derivadas
- lectura conjunta de provenance

---

## 8. Sobre composición

El frontmatter y las referencias entre documentos permiten construir conocimiento compuesto sin romper la atomicidad.

Esto significa que:

- los átomos pueden permanecer pequeños
- las síntesis más grandes pueden construirse encima
- la riqueza conceptual no depende de inflar cada átomo

La composición es la salida correcta para insight más profundo.
No la expansión excesiva del átomo individual.

---

## 9. Sobre `marcado`

La anotación sobre samples no debe reinventarse dentro de este spec.

Para eso existe `marcado`.

Referencia:

- `/home/jp/proyectos/hum-ecosystem/tools/marcado`

## Rol de `marcado` en esta arquitectura

`marcado` opera sobre el **sample**, no sobre la fuente PDF.

Eso mantiene la separación:

- fuente: artefacto inmutable
- sample: superficie de anotación
- átomo: superficie de conocimiento destilado

## Consecuencia

Este spec no necesita redefinir el sistema de marcado inline.
Debe solamente asumir que:

- la anotación del sample ocurre con `marcado`
- el sample es la superficie donde esa anotación vive
- el PDF no se edita ni se marca directamente

---

## 10. Relación correcta entre fuente, sample y átomo

La cadena correcta sigue siendo:

> fuente → biopsia/sample → átomo

Pero con esta aclaración importante:

- la **prueba fuerte** vive en la relación entre sample y fuente exacta
- el **trabajo de anotación** vive en el sample
- la **destilación reusable** vive en el átomo

## Lectura operacional

- la fuente fija el referente original
- la biopsia fija un corte recuperable y anotable
- el átomo fija una respuesta reusable y composable

---

## 11. Sobre las capas del sistema

Las capas `source -> sample -> atom -> composición/superficie` son
distinciones funcionales, no castas ontológicas rígidas.

Sirven para separar responsabilidades:

- la fuente conserva el artefacto o snapshot de referencia
- el sample conserva el corte verificable y anotable
- el átomo conserva la tesis reusable
- la composición conserva la recombinación o materialización para lectura o trabajo

Un mismo artefacto puede participar en más de una cadena de trabajo, pero esa
flexibilidad no elimina la necesidad de distinguir qué rol está cumpliendo en
cada momento.

---

## 12. Qué debe reforzarse en el spec principal

Estas aclaraciones sugieren reforzar explícitamente en `KB_SYSTEM_SPEC.md` que:

1. `source_hash_sha256` es la unión criptográfica principal con la fuente
2. la validación del anchor es determinista y exacta
3. el sample no necesita normalización rígida de tamaño
4. la atomicidad del átomo está dada por una sola pregunta 5WH1+
5. la profundidad se logra por composición, no por inflar átomos
6. `marcado` es la capa de anotación sobre samples

---

## 13. Resumen corto

### Hash
El hash clave es el de la fuente, no el del sample como superficie editable.

### Anchor
El anchor debe permitir recuperar exactamente el texto desde la fuente correcta.

### Sample
Lo importante no es su tamaño uniforme sino su direccionabilidad y grounding.

### Atom
Un átomo responde una sola pregunta 5WH1+ y se mantiene pequeño para poder componerse.

### Marking
La anotación inline del sample pertenece a `marcado`, no al PDF ni a una reinvención local.
