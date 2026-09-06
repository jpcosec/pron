# spec2viz

## Qué es
Renderer de especificaciones semánticas hacia diagramas y charts.
Compila specs estructurados a una IR agnóstica del renderer y produce Mermaid, PlantUML, Vega, etc.

## Por qué importa para la nueva app
Aporta ideas para materializar conocimiento estructurado en vistas derivadas legibles por humanos.

## Qué deberíamos recuperar

### 1. Separación semántica vs render
- la semántica vive upstream
- los diagramas son proyecciones/materializaciones

### 2. IR intermedia
- compilar a una representación intermedia antes de renderizar
- no acoplar directamente modelo fuente y salida visual

### 3. Renderers múltiples
- diferentes vistas desde la misma base semántica
- diagramas, matrices, charts

### 4. Valor para la KB
Podría servir para:
- vistas de coverage
- mapas conceptuales
- timelines de fuentes
- relaciones entre atoms/samples

## Qué no deberíamos heredar sin revisión
- complejidad de renderers si la app aún no necesita tantas salidas
- convertir visualización en fuente de verdad

## Preguntas de extracción
- ¿Qué proyecciones visuales necesita la nueva KB?
- ¿Conviene una IR propia para vistas?
- ¿Cómo mantener clara la frontera entre conocimiento canónico y visualizaciones?