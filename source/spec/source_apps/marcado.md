# marcado

## Qué es
Núcleo de Semantic Markdown con markers, anchors, validación y exportación canónica.
Opera sobre documentos Markdown como superficie anotable y direccionable.

## Por qué importa para la nueva app
Para la arquitectura `fuente → sample → átomo`, Marcado es altamente relevante como capa de anotación y marcado sobre samples.

## Qué deberíamos recuperar

### 1. Modelo de marcado inline
- comment markers / milestone markers
- namespaces de marcado
- representación estructurada del marcado

### 2. Anchors y direccionabilidad
- lookup estable de anchors
- validación de rangos
- exportación a JSON canónico
- soporte para recuperar segmentos marcados

### 3. Separación entre texto y semántica añadida
- overlay semántico sobre Markdown
- no confundir marcado con fuente original

### 4. Flujo de validación
- parse
- normalize
- validate
- export

### 5. Rol en la arquitectura
Marcado debería informar cómo anotar samples sin tocar el PDF/fuente original.

## Qué no deberíamos heredar sin revisión
- cualquier restricción demasiado específica del MVP si la nueva app necesita semántica más rica
- depender de una sola representación si hace falta interoperabilidad con samples estructurados

## Preguntas de extracción
- ¿Cómo modela anchors y rangos?
- ¿Cómo conserva reversibilidad?
- ¿Cómo distinguir evidencia textual vs anotación marcada?
- ¿Cómo integrar Marcado con validación exacta de samples?