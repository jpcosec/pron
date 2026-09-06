# deskops

## Qué es
Capa de workflow construida encima de SLDB.
En la práctica también ha servido como superficie operativa para gestionar átomos, pills, tasks, boards y rituales.

## Por qué importa para la nueva app
No es la infraestructura genérica de conocimiento, pero sí captura una experiencia CLI y una disciplina de trabajo que hoy sostienen parte del knowledge management real.

## Qué deberíamos recuperar

### 1. Disciplina de atomización
- átomo pequeño
- una sola pregunta 5WH1+
- respuesta curada y reusable
- tags namespaced

### 2. Experiencia CLI humana
Replicar o reinterpretar comandos del estilo:
- listar átomos
- mostrar átomo por id
- crear átomo guiado
- listar tasks
- ver board
- ver siguiente acción

Lo importante no es copiar comandos exactos, sino conservar la fluidez conversacional/operativa.

### 3. Acoplamiento entre trabajo y conocimiento
Deskops muestra valor en integrar:
- backlog de extracción
- cobertura temática pendiente
- refinamiento de conocimiento
- cierre operativo

La nueva app debería decidir si mantiene esta unión o la separa mejor.

### 4. Superficies operativas útiles
- board
- tasks
- rituals
- pills/context
- atoms como materialización durable

### 5. Convenciones de navegación
- ids estables
- árboles humanos legibles
- comandos directos en lenguaje de trabajo

## Qué no deberíamos heredar sin revisión
- que la KB viva dentro de `desk/`
- que la provenance quede fuera del modelo estructurado
- que atoms y operación compartan el mismo workspace por defecto

## Preguntas de extracción
- ¿Qué comandos CLI usa más la gente realmente?
- ¿Cómo se crean, listan y encuentran átomos?
- ¿Qué partes del workflow merecen entrar a una app de conocimiento y cuáles no?
- ¿Cómo desacoplar atoms del workspace operativo sin perder UX?