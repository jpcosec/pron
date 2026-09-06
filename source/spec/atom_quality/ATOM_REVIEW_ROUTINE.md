# Atom Review Routine

## Estado

Borrador operativo.

## Propósito

Definir una rutina de revisión periódica para mantener calidad homogénea en el corpus de átomos.

---

## 1. Tipos de revisión

### 1.1 Revisión al crear

Se aplica a todo átomo nuevo antes de considerarlo aceptado.

### 1.2 Revisión de refinamiento

Se aplica a átomos existentes con señales de debilidad:

- tags vacíos
- procedencia ausente
- answer demasiado delgado
- placeholder residue
- duplicación cercana

### 1.3 Revisión de lote

Se aplica a subconjuntos del corpus, por ejemplo:

- todos los átomos de anchoring
- todos los átomos de provenance
- todos los átomos bootstrap
- todos los átomos de una carpeta fuente

---

## 2. Rutina mínima por átomo

Cada revisión debería seguir esta secuencia.

1. leer título, `five_wh_one_plus` y answer
2. identificar la tesis principal
3. verificar si el answer realmente responde esa pregunta
4. revisar atomicidad
5. revisar tags
6. revisar procedencia
7. decidir si pasa o falla la checklist mínima
8. decidir: aceptar, refinar, dividir o fusionar

---

## 3. Preguntas de revisión obligatorias

### 3.1 Sobre la tesis

- ¿cuál es exactamente la afirmación nuclear?
- ¿podría otra persona explicarla sin contexto extra?
- ¿está bien delimitada?

### 3.2 Sobre atomicidad

- ¿hay una sola tesis o varias?
- ¿hay una sola pregunta dominante?
- ¿la explicación secundaria está subordinada a la principal?

### 3.3 Sobre calidad del answer

- ¿dice más que el título?
- ¿preserva una distinción valiosa?
- ¿sería útil citarlo después?
- ¿es demasiado genérico?

### 3.4 Sobre gobernanza

- ¿la procedencia es explícita?
- ¿los tags permiten recuperarlo?
- ¿el grounding implícito está siendo exagerado?

---

## 4. Acciones posibles de la revisión

### Aceptar

Cuando el átomo ya cumple el estándar mínimo.

### Refinar

Cuando la tesis es buena pero falta curación editorial o de metadata.

### Dividir

Cuando contiene dos ideas principales.

### Fusionar

Cuando dos átomos cercanos expresan casi la misma tesis.

### Rebajar a nota temporal

Cuando la idea todavía no alcanzó forma de átomo durable.

---

## 5. Señales que disparan revisión prioritaria

Revisar primero átomos con cualquiera de estas señales:

- `tags: []`
- falta de campo `provenance` en frontmatter
- placeholder text
- answers de una sola frase muy genérica
- títulos muy precisos con body muy vago
- clusters de átomos con posible solapamiento

---

## 6. Rutina semanal o por lote

Una rutina sana de mantenimiento podría ser:

1. listar átomos nuevos o modificados
2. detectar átomos con tags vacíos
3. detectar átomos sin procedencia
4. detectar answers demasiado cortos
5. escoger un tema o carpeta por lote
6. revisar consistencia entre átomos vecinos
7. registrar decisiones de aceptación o refinamiento

---

## 7. Indicadores prácticos de salud del corpus

Conviene mirar métricas simples como:

- porcentaje con tags no vacíos
- porcentaje con procedencia explícita
- porcentaje sin residuos de template
- porcentaje de answers con sustancia suficiente
- cantidad de átomos candidatos a división o fusión

---

## 8. Regla de severidad útil

No todo átomo necesita quedar perfecto antes de existir.
Pero sí debería evitarse aceptar como “cerrado” un átomo que siga teniendo defectos básicos de:

- atomicidad
- answer sustantivo
- procedencia
- tags mínimos
- claridad editorial

---

## 9. Resultado esperado de la rutina

La rutina de revisión debe producir un corpus donde:

- crear y evaluar átomos sea menos arbitrario
- los átomos débiles sean detectables rápido
- las decisiones de calidad sean más consistentes entre autores
- el corpus quede listo para migraciones, grafos y composiciones futuras
