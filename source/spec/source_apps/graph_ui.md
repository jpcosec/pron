# graph_ui

## Qué es
Editor visual de grafos agnóstico de dominio.
Fue pensado para renderizar y editar knowledge graphs en una interfaz reutilizable.

## Por qué importa para la nueva app
Si la nueva app tendrá un grafo de fuentes, samples, atoms, composiciones y relaciones, aquí puede haber patrones valiosos de UX y arquitectura visual.

## Qué deberíamos recuperar

### 1. Editor agnóstico de dominio
- nodos/edges sin acoplar a un solo dominio
- visualización reusable de knowledge graphs

### 2. Arquitectura por capas
El README menciona una refactorización hacia una arquitectura de 3 capas.
Conviene recuperar esa separación para no terminar con un componente monolítico.

### 3. Operaciones de inspección y edición
- inspección visual de nodos
- edición de relaciones
- navegación de estructuras complejas

### 4. Rol en la nueva app
Podría ser la superficie gráfica para:
- lineage fuente → sample → atom
- composiciones de atoms
- cobertura temática
- clusters conceptuales

## Qué no deberíamos heredar sin revisión
- deuda de integración de worktrees previos
- complejidad UI antes de fijar bien el modelo de datos

## Preguntas de extracción
- ¿Qué patrones UI son reutilizables?
- ¿Cómo representar provenance y composición en un grafo legible?
- ¿Qué parte del editor debería ser genérica vs específica del dominio KB?