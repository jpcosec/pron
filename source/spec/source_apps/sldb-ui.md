# sldb-ui

## Qué es
Superficie UI para inspeccionar, renderizar y editar documentos Marcado.
Aunque el path todavía se llama `sldb-ui`, la app se describe como `marcado-ui`.

## Por qué importa para la nueva app
Aporta referencias para la experiencia visual/operatoria sobre documentos marcados y estructurados.

## Qué deberíamos recuperar

### 1. Vistas duales
- rendered view
- source view
- inspección de markers

### 2. Edición asistida
- creación de markers desde selección
- save/load de drafts
- open/upload/save/download
- exploración de carpetas de Markdown

### 3. Integración runtime
- refrescar contra implementación Python real
- evitar que la UI sea un runtime semántico paralelo completo

### 4. Principio importante
La UI debe ser superficie de operador, no duplicado inconsistente del core semántico.

## Qué no deberíamos heredar sin revisión
- parsers frontend paralelos si degradan consistencia
- acoplamiento accidental a un nombre/proyecto transicional

## Preguntas de extracción
- ¿Qué UX ayuda más para revisar y editar samples marcados?
- ¿Cómo mostrar evidencia, markup y extracción estructurada simultáneamente?
- ¿Qué operaciones deben vivir en UI y cuáles en el runtime?