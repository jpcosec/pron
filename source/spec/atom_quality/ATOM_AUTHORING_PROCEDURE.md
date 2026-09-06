# Atom Authoring Procedure

## Estado

Borrador operativo.

## Propósito

Definir un procedimiento repetible para crear o refinar átomos con menos improvisación.

---

## 1. Flujo general

El flujo recomendado es:

1. detectar una afirmación candidata
2. decidir si merece un átomo
3. elegir la pregunta 5WH1+
4. redactar título e `id`
5. escribir answer sustantivo
6. declarar procedencia
7. escribir `provenance` en frontmatter
8. asignar tags
9. revisar con checklist

---

## 2. Paso 1 — Detectar una afirmación candidata

Una buena candidata suele aparecer cuando encontramos:

- una distinción arquitectónica estable
- una regla de modelado reusable
- un constraint de gobernanza
- una relación importante entre entidades
- un anti-patrón que conviene fijar explícitamente

No toda frase interesante merece un átomo.

---

## 3. Paso 2 — Decidir si merece un átomo

Preguntas de decisión:

- ¿esto expresa una sola idea principal?
- ¿servirá otra vez fuera de esta tarea concreta?
- ¿es más que una observación pasajera?
- ¿conviene poder citarlo como regla o criterio?
- ¿sería costoso perderlo dentro de un texto largo?

Si la respuesta es mayormente no, quizá no merece un átomo todavía.

---

## 4. Paso 3 — Elegir la pregunta 5WH1+

Usar esta guía simple.

### `what`

Elegir cuando el átomo define, caracteriza o distingue qué es algo.

### `why`

Elegir cuando el núcleo es la razón de una decisión, separación o necesidad.

### `how`

Elegir cuando el núcleo es el mecanismo, la forma recomendada o el criterio operativo.

### `how_not`

Elegir cuando el átomo fija una prohibición, un límite o un anti-patrón.

### `when`, `where`, `for_whom`

Usar solo si realmente la dimensión temporal, situacional o de destinatario es la principal.

---

## 5. Paso 4 — Redactar título e `id`

### 5.1 Título

El título debe:

- expresar la tesis principal
- ser específico
- poder entenderse sin contexto conversacional

### 5.2 `id`

El `id` debe:

- ser estable
- seguir el título de forma legible
- evitar cambios cosméticos innecesarios

### 5.3 Regla práctica

Si el título necesita “y además…” o contiene varias cláusulas independientes, probablemente el átomo está demasiado cargado.

---

## 6. Paso 5 — Escribir el answer

Usar este mini-patrón:

1. afirmar
2. distinguir
3. implicar

### Ejemplo de patrón

- Afirmar: “X should be treated as Y.”
- Distinguir: “This separates it from Z.”
- Implicar: “That matters because…”

### Regla editorial

Antes de cerrar, verificar:

- ¿el answer dice más que el título?
- ¿explica por qué la afirmación importa?
- ¿preserva una distinción real?

---

## 7. Paso 6 — Declarar procedencia

Preguntar:

- ¿de qué spec o fuente sale esta idea?
- ¿es una inferencia desde una sola fuente o una síntesis?
- ¿tengo evidencia directa o solo derivación conceptual?

Declarar la respuesta en el campo de frontmatter `provenance`.

---

## 8. Paso 7 — Asignar tags

Asignar primero los tags mínimos:

- `system:...`
- `topic:...`

Luego agregar solo los tags semánticos que realmente ayuden a recuperar la afirmación:

- `layer:*`
- `entity:*`
- `graph:*`
- `domain:*`
- `cross:*`

No sobrecargar con tags irrelevantes.

La metadata de curación u origen del átomo, como `project:*`, `source:*`,
`source_kind:*`, `grounding:*`, `role:*` o `status:*`, pertenece al metadata
registry y no al tagset semántico del átomo.

---

## 9. Paso 8 — Revisar con checklist

Todo átomo nuevo o refinado debe pasar por la checklist de:

- atomicidad
- calidad del answer
- procedencia
- tags
- ausencia de placeholder

Si falla en cualquiera de esos ejes, todavía no está listo.

---

## 10. Procedimiento de refinamiento de átomos débiles

Cuando el átomo ya existe pero es débil, aplicar esta secuencia:

1. quitar residuos de template
2. identificar la tesis principal
3. confirmar o corregir `five_wh_one_plus`
4. reescribir answer con más sustancia
5. agregar `provenance` en frontmatter
6. completar tags mínimos
7. revisar duplicación con átomos vecinos

---

## 11. Criterio para dividir un átomo

Dividir el átomo si ocurre cualquiera de estos casos:

- responde claramente dos preguntas 5WH1+
- contiene dos tesis que podrían citarse por separado
- mezcla definición con workflow completo
- la mitad del answer existe solo para explicar una segunda idea

---

## 12. Criterio para no crear un átomo todavía

No crear el átomo todavía si:

- la afirmación sigue siendo demasiado borrosa
- solo existe como intuición sin wording claro
- depende enteramente de contexto temporal de una task
- todavía no se distingue bien de otra idea casi idéntica
