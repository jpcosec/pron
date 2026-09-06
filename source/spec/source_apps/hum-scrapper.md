# hum-scrapper

## Qué es
Sistema de automatización/browser workflow con una capa semántica persistente que acumula conocimiento a través de ejecuciones.

## Por qué importa para la nueva app
No es el núcleo de la KB, pero sí una referencia para adquisición/ingesta de conocimiento desde entornos externos.

## Qué deberíamos recuperar

### 1. Acumulación de conocimiento entre runs
- memoria semántica persistente
- no tratar cada ejecución como aislada

### 2. Pipeline de adquisición
- observar
- interpretar
- actuar
- registrar hallazgos estructurados

### 3. Ontología operacional de extracción
Puede inspirar cómo capturar conocimiento desde:
- web
- portales
- fuentes interactivas
- procesos semiautomatizados

### 4. Integración futura
La nueva KB podría necesitar ingestores que produzcan:
- fuentes registradas
- samples candidatos
- metadata de extracción

## Qué no deberíamos heredar sin revisión
- complejidad de automatización si el foco actual es modelado KB
- mezclar directamente agente navegador con núcleo documental

## Preguntas de extracción
- ¿Cómo modela memoria/semántica acumulada?
- ¿Qué salidas estructuradas produce?
- ¿Qué partes sirven para una futura capa de ingestión automatizada?