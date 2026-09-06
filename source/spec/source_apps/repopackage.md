# repopackage

## Qué es
Sistema de composición recursiva de repositorios basada en contratos tipados.
No es una herramienta de knowledge management directa, pero trabaja con grafos, contratos e integración trazable.

## Por qué importa para la nueva app
Puede aportar ideas sobre:
- contratos entre componentes
- composición recursiva
- integración trazable
- inspección sin checkout completo

## Qué deberíamos recuperar

### 1. Diseño por contratos
- surfaces tipadas
- compatibilidad explícita
- validación de integraciones

### 2. Trazabilidad entre componentes
- quién usa qué
- qué exporta cada parte
- cómo se conectan módulos independientes

### 3. Valor para la KB
Podría inspirar:
- plugins o packages de modelos
- repositorios de conocimiento federados
- integración entre stores o espacios de conocimiento

## Qué no deberíamos heredar sin revisión
- complejidad de package management si la app nueva no la necesita aún
- abstraer demasiado temprano la composición federada

## Preguntas de extracción
- ¿Qué ideas de contratos sirven para modelos/ingestores/vistas de la KB?
- ¿Cómo pensar composición/federación de repos de conocimiento?
- ¿Qué parte de su trazabilidad es transferible al dominio KB?