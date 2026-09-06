# Multi-Source Anchoring

## Estado
Draft

## Propósito
Definir principios de anchoring para una base de conocimiento que debe trabajar con muchas clases de fuentes:

- PDFs
- webpages
- archivos de texto
- Markdown
- código fuente
- repos Git
- JSON/YAML
- notebooks
- exports estructurados
- otras superficies futuras

Este documento profundiza la idea de que el sistema no debe depender solo de texto plano.
Debe poder usar estructuras nativas o derivadas de cada fuente para anclar samples de manera más inteligente, estable y verificable.

---

## 1. Principio general

Una fuente no debe exponer solo:

- bytes
- texto plano

Debe exponer una o más **proyecciones direccionables**.

Estas proyecciones pueden ser:

- textuales
- estructurales
- posicionales
- contextuales
- semánticas

La estrategia de anchoring del sistema debe usar la mejor combinación disponible según el tipo de fuente.

---

## 2. Principio rector de anchoring

> Un sample debe anclarse de forma verificable contra la fuente o snapshot sobre
> el que realmente estamos trabajando, privilegiando la estructura direccionable
> más útil disponible y reteniendo evidencia textual suficiente para verificación
> independiente e inspección humana.

Esto implica:

- usar AST cuando existe una estructura AST útil
- usar DOM o estructura documental cuando existe
- usar layout o bloques de lectura cuando la fuente lo ofrece
- usar quote textual como verificación
- usar varios anchors coordinados solo cuando realmente agregan robustez

---

## 3. AST como categoría de primer nivel

En esta app, **AST debe ser una categoría de primer nivel dentro de la estructura documental**.

No debe tratarse como un detalle accidental de ciertos parsers.

## Qué significa eso

La app debe reconocer explícitamente que algunas fuentes tienen estructuras sintácticas o lógicas navegables, por ejemplo:

- código fuente
- Markdown
- HTML/XML
- JSON/YAML
- notebooks estructurados
- otros lenguajes parseables

En esos casos, la estructura del documento no es solo texto.
La estructura incluye nodos, relaciones, jerarquías, rutas y spans.

## Consecuencia arquitectónica

La estructura documental de la app debe contemplar como categorías de primer nivel, al menos:

- **texto**
- **AST / árbol sintáctico**
- **estructura documental**
- **layout / regiones / bloques**
- **metadata**

No todas las fuentes tendrán todas las categorías.
Pero la arquitectura debe soportarlas explícitamente.

---

## 4. Proyecciones de una fuente

Una fuente puede tener varias proyecciones simultáneas.
La metadata vive como superficie separada; no queda "embebida" conceptualmente
en las otras proyecciones aunque pueda derivarse de ellas.

## 4.1 Raw representation

La representación original recuperada:

- bytes
- archivo original
- snapshot bruto
- respuesta cruda de API

## 4.2 Text projection

Una proyección textual utilizable para quote matching, búsqueda e inspección humana.

Ejemplos:

- texto extraído de PDF
- texto plano de HTML
- contenido textual de archivo
- concatenación de nodos textuales

## 4.3 Structural projection

Representa organización interna navegable.

Ejemplos:

- AST de código
- mdast de Markdown
- DOM de webpage
- árbol de headings/secciones
- árbol de objetos JSON/YAML
- árbol de celdas en notebook
- árbol de páginas/bloques en PDF si se deriva

## 4.4 Positional projection

Representa localización dentro de una superficie.

Ejemplos:

- offsets de caracteres
- line/column
- page/block/coordinates
- índices de bloques

## 4.5 Contextual projection

Representa información vecina útil para reanclaje y validación.

Ejemplos:

- prefix/suffix
- título de sección
- parent node
- sibling nodes
- symbol owner

---

## 5. Tipos de source y estructuras esperables

## 5.1 Código fuente

Proyecciones valiosas:

- raw file
- text projection
- AST
- symbol table
- line/column map

Anchors recomendables:

- path + revision
- symbol anchor
- AST node path
- line range
- exact quote

## 5.2 Markdown

Proyecciones valiosas:

- raw markdown
- text projection
- mdast
- heading tree
- frontmatter model
- block structure

Anchors recomendables:

- heading path
- block path
- AST node path
- exact quote
- prefix/suffix

## 5.3 Webpages / HTML

Proyecciones valiosas:

- raw HTML
- rendered/plain text projection
- DOM tree
- semantic sections
- CSS/XPath addressability

Anchors recomendables:

- DOM selector
- DOM path
- text quote
- prefix/suffix
- section heading

## 5.4 PDF

Proyecciones valiosas:

- raw PDF
- extracted text
- page segmentation
- reading order blocks
- layout regions
- derived section structure when possible

Anchors recomendables:

- page range
- block id / region id
- exact quote
- prefix/suffix
- anchor text

## 5.5 JSON / YAML

Proyecciones valiosas:

- raw doc
- structured object tree
- schema path
- text projection

Anchors recomendables:

- object path
- field path
- textual quote when useful

## 5.6 Git repositories

Un repo suele ser una fuente contenedora.

Proyecciones valiosas:

- repo identity
- commit tree
- file/blob tree
- per-file structural projections

Anchors recomendables:

- repo + commit
- file path
- blob hash
- per-file AST/text anchors

---

## 6. Anchors como bundle, no como campo único

La app no debe pensar el anchor como un solo campo plano.

Debe pensarlo como un **bundle de selectors coordinados**.

## Categorías posibles dentro del bundle

### 6.1 Structural anchor

Ejemplos:

- AST node path
- DOM selector
- heading path
- object path
- symbol path
- page/block id

### 6.2 Text anchor

Ejemplos:

- exact quote
- normalized quote
- anchor text

### 6.3 Positional anchor

Ejemplos:

- line range
- character offset range
- page start/end
- coordinates

### 6.4 Context anchor

Ejemplos:

- prefix
- suffix
- parent heading
- surrounding nodes
- containing symbol

## Regla

No todas las biopsias necesitan todos los componentes.
Pero el sistema debe soportarlos como categorías explícitas.

Un solo anchor primario bien elegido puede ser suficiente.
Si existen anchors adicionales, deben ser complementarios, no contradictorios.
El sistema no debe asumir un modelo de "conflicto entre anchors" como caso normal.

---

## 7. Source adapters y structure extractors

Para soportar anchoring inteligente, la app debe ser modular.
Estos cuatro nombres describen componentes de código o responsabilidades de
runtime. Lo persistido en la KB son los anchors, bindings y resultados de
validación relevantes, no necesariamente cada componente como objeto documental.

## 7.1 Source adapter

Responsable de:

- identificar la fuente
- recuperarla
- ligar su versión exacta
- declarar qué proyecciones soporta
- proveer metadata común

## 7.2 Structure extractor

Responsable de producir estructuras direccionables.

Ejemplos:

- parser AST para código
- mdast parser para Markdown
- DOM parser para HTML
- layout extractor para PDF
- object-tree extractor para JSON/YAML

## 7.3 Anchor resolver

Responsable de:

- resolver un anchor contra una proyección
- devolver el nodo/span/segmento referenciado
- producir un excerpt recuperado

## 7.4 Anchor validator

Responsable de:

- comprobar binding a la fuente correcta
- verificar resolución estructural
- verificar quote exacta
- reportar fallos de forma determinista

---

## 8. Validación multicapa

La validación no debe ser solo “¿aparece esta frase?”.

Debe ser multicapa.
No todas las capas aplican con el mismo peso a todos los tipos de anchor, pero
la separación conceptual debe mantenerse.

## Nivel 1. Validación de identidad de fuente

Preguntas:

- ¿estamos mirando la fuente correcta?
- ¿la versión corresponde al binding esperado?
- ¿coincide el hash/commit/blob esperado?

## Nivel 2. Validación estructural

Preguntas:

- ¿el selector estructural resuelve?
- ¿el nodo esperado existe?
- ¿el tipo de nodo coincide?
- ¿la ruta o selector sigue siendo válido?

## Nivel 3. Validación textual

Preguntas:

- ¿la quote exacta aparece en el nodo/span resuelto?
- ¿la normalización usada es consistente?

## Nivel 4. Validación contextual

Preguntas:

- ¿prefix/suffix o vecinos siguen alineando?
- ¿la sección/contenedor esperado coincide?

---

## 9. Implicaciones para samples

Los samples deben poder guardar anchors más ricos que un simple:

- `source_path`
- `page_start`
- `page_end`
- `anchor_text`

La arquitectura conceptual del sample debería contemplar:

- referencia de fuente
- tipo de proyección usada
- bundle de anchors
- excerpt recuperado
- política o estado de validación

## Idea importante

El sample no es solo un texto copiado.
Es un **objeto de direccionamiento verificable** sobre una fuente versionada.

---

## 10. Implicaciones para la estructura documental de la app

La app debe tener una noción explícita de estructura documental multi-representación.

## Categorías de primer nivel recomendadas

### Texto
Para búsqueda, lectura y quote validation.

### AST
Para código, Markdown parseado, HTML parseado, JSON/YAML estructurado y otros lenguajes parseables.

### Estructura documental
Para headings, secciones, bloques, listas, tablas, celdas, capítulos.

### Layout
Para PDFs y otras fuentes con regiones, bloques o coordenadas.

### Metadata
Para hash, path, url, commit, mime, timestamps, parser version y demás facts
del artefacto o de la extracción. Esta metadata debe mantenerse como documento
o superficie separada, aunque se use para resolver anchors.

AST debe existir como categoría explícita y no solo como una subnota técnica del parser.

---

## 11. Estrategia de diseño recomendada

## Regla práctica principal

Siempre que una fuente tenga estructura rica, el sistema debe:

1. extraer esa estructura
2. usarla como anchor primario cuando tenga sentido
3. retener quote textual para verificación y lectura humana
4. usar posición como apoyo, no como única base salvo necesidad

## Estrategia resumida

- estructura para precisión
- texto para prueba
- contexto para robustez
- posición para apoyo

---

## 12. Qué evita esta estrategia

Evita depender exclusivamente de:

- quotes frágiles
- offsets que se rompen fácilmente
- páginas sin contexto estructural
- rutas demasiado pobres para fuentes complejas

También evita tratar por igual fuentes radicalmente distintas.

---

## 13. Síntesis final

La nueva app debe tratar cada fuente como un artefacto multi-representación.

Eso significa que una fuente puede exponer simultáneamente:

- raw artifact
- text projection
- AST
- document structure
- layout structure
- metadata

Y los samples deben apoyarse en la mejor combinación disponible para anclaje y validación.

En una frase:

> El sistema debe anclar contra estructura rica cuando exista, verificar con evidencia textual, y tratar AST como una categoría de primer nivel dentro de la estructura documental de la app.
