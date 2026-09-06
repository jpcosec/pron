# Deskops for Knowledge Management

## Estado
Draft

## Propósito
Documentar cómo se está usando actualmente `deskops` en `/home/jp/Upla/tutor_apoe` como superficie de gestión de conocimiento, para poder replicar esa experiencia en una aplicación nueva más comprehensiva.

Este documento describe el **uso real actual** y la **lógica de interacción** observada en el repo.
No propone todavía el reemplazo.
Describe qué papel cumple hoy `deskops` dentro del flujo de conocimiento.

---

## 1. Resumen ejecutivo

En `tutor_apoe`, `deskops` no solo se usa para workflow operativo.
También se usa como **contenedor práctico de la base de conocimiento atómica actual**.

En la práctica actual:

- los átomos viven en `desk/atoms/`
- esos átomos siguen el modelo `deskops.models:AtomDoc`
- se listan, inspeccionan y crean con comandos `deskops`
- SLDB indexa esos documentos, pero el surface de autoría sigue siendo `deskops`

Por eso, aunque la arquitectura deseada del repo ya apunta a una KB más allá de `deskops`, el uso presente muestra que `deskops` cumple cuatro funciones de knowledge management:

1. **surface de almacenamiento humano**
2. **contrato mínimo del átomo**
3. **CLI de navegación y authoring**
4. **integración con el workflow de extracción**

---

## 2. Contexto del repo analizado

Repo observado:

- `/home/jp/Upla/tutor_apoe`

Evidencia relevante:

- `README.md`
- `docs/knowledge-architecture.md`
- `desk/atoms/`
- `.sldb/core/models/AtomDoc.yaml`
- `.sldb/core/documents/AtomDoc.yaml`
- `knowledge_models/docs.py`

---

## 3. Qué parte de la KB vive en Deskops hoy

La colección activa de conocimiento atómico está en:

- `desk/atoms/`

Ejemplos de rutas:

- `desk/atoms/apos/core-structures/action/...`
- `desk/atoms/apos/mechanisms/...`
- `desk/atoms/apos/pedagogy/...`
- `desk/atoms/apos/research/...`
- `desk/atoms/sources/...`

Esto significa que `deskops` hoy funciona como:

- repositorio visible de átomos
- árbol taxonómico navegable por carpetas
- surface principal de lectura humana del conocimiento destilado

Aunque el repo ya define una nueva capa `knowledge/`, la base material poblada sigue estando en `desk/atoms/`.

---

## 4. Modelo de conocimiento que Deskops está alojando

Los átomos actuales siguen el contrato de `AtomDoc` de Deskops:

Referencia:

- `/home/jp/proyectos/hum-ecosystem/tools/deskops/deskops/models/atom.py`

### Campos principales

- `id`
- `title`
- `five_wh_one_plus`
- `answer`
- `tags`

### Semántica del modelo

- un átomo responde una sola pregunta 5WH1+
- el cuerpo contiene una sola respuesta curada
- los tags sirven para agrupación y retrieval
- el átomo es una unidad pequeña y reusable

### Observación importante

En `tutor_apoe`, muchos átomos agregan además una sección libre:

- `## Procedencia`

Eso muestra que el proyecto está usando `AtomDoc` como base, pero extendiéndolo informalmente para expresar provenance.

Es decir:

- `deskops` provee el contrato mínimo
- el repo agrega manualmente información de origen que el modelo no estructura todavía

---

## 5. Qué experiencia CLI aporta Deskops hoy

La experiencia de knowledge management observable en el repo se apoya en comandos como:

### Listar átomos

```bash
deskops list atoms --root .
```

Uso implícito:
- discovery del corpus
- revisión rápida de qué conocimiento existe
- soporte para evitar duplicados

### Mostrar un átomo

```bash
deskops show atom <atom-id> --root .
```

Uso implícito:
- lectura focal de una unidad de conocimiento
- inspección de tags, pregunta y respuesta
- acceso rápido por identificador estable

### Crear un átomo

```bash
deskops add atom --root . \
  --title "..." \
  --five-wh-one-plus what \
  --answer "..."
```

Uso implícito:
- materializar conocimiento destilado sin editar todo el archivo manualmente
- mantener el contrato básico uniforme
- generar un archivo atómico con naming y shape consistentes

### Flujo más amplio

Los comandos de task/workflow también participan indirectamente:

```bash
deskops show board Board --root .
deskops list tasks --root .
deskops show task <task-id> --root .
deskops advance task <task-id> --root .
deskops next <task-id> --root .
```

Estos no gestionan contenido atómico directamente, pero sí gestionan el **trabajo de extracción y refinamiento** del conocimiento.

---

## 6. Cómo Deskops está siendo usado para knowledge management

## 6.1 Como surface de authoring de átomos

`deskops` permite crear rápidamente una unidad atómica curada.

En el uso actual, esto significa:

- declarar un título
- escoger la pregunta 5WH1+
- escribir una respuesta compacta
- luego complementar con tags y procedencia

El CLI reduce fricción para materializar conocimiento pequeño y estable.

## 6.2 Como surface de browsing

`deskops list atoms` y `deskops show atom` convierten el corpus en algo navegable sin abrir manualmente cada archivo.

Esto aporta:

- acceso rápido
- lookup por id
- revisión de cobertura
- soporte para curación incremental

## 6.3 Como normalizador del estilo atómico

El modelo `AtomDoc` obliga a un shape base:

- una pregunta seleccionada
- una respuesta
- tags

Eso disciplina la escritura y evita que los documentos se conviertan en notas largas o mezcladas.

## 6.4 Como acoplamiento entre workflow y conocimiento

En el repo, el trabajo activo usa `deskops` tasks/board/rituals.

Eso hace que la producción de conocimiento ocurra dentro del mismo ecosistema operacional:

- una task puede pedir extracción de átomos de un capítulo
- el scope puede apuntar a subárboles de `desk/atoms/`
- el resultado esperado es la creación/refinamiento de átomos

Así, `deskops` no solo guarda conocimiento: también encuadra el proceso de producirlo.

---

## 7. Qué valor de knowledge management aporta Deskops

### 7.1 Unidad pequeña y reusable

Su modelo de átomo favorece:

- una idea por documento
- una pregunta por documento
- composabilidad
- retrieval granular

### 7.2 Taxonomía física sencilla

El árbol de carpetas en `desk/atoms/` funciona como una clasificación humana legible.

Ejemplos de ejes visibles:

- foundations
- core-structures
- mechanisms
- pedagogy
- research
- applications
- mathematical-domains
- synthesis
- sources

Esto permite una navegación mixta:

- por CLI
- por filesystem
- por convención conceptual

### 7.3 Consistencia mínima del documento

El modelo deskops evita formatos arbitrarios.

Incluso cuando la provenance está libre, los átomos comparten:

- nombre estable
- pregunta explícita
- respuesta explícita
- tags namespaced

### 7.4 Interoperabilidad con SLDB

Aunque `deskops` es el surface de authoring de esos átomos, SLDB puede indexarlos.

En el store actual:

- `AtomDoc` está registrado
- los documentos de `desk/atoms/` están trackeados
- los tags aparecen en el índice semántico

Esto significa que `deskops` aporta el surface humano y SLDB aporta:

- tracking
- store
- búsqueda
- indexación

---

## 8. Dependencias concretas de la KB respecto a Deskops

## 8.1 Dependencia de ubicación

La base de conocimiento atómica actual está físicamente en:

- `desk/atoms/`

Eso hace que la KB dependa del workspace `desk/` como contenedor.

## 8.2 Dependencia de modelo

La colección activa sigue:

- `deskops.models:AtomDoc`

Por eso hereda:

- `five_wh_one_plus`
- `answer`
- `tags`
- semántica `workspace.desk.atoms`

## 8.3 Dependencia de CLI

El acceso operativo a los átomos usa:

- `deskops list atoms`
- `deskops show atom`
- `deskops add atom`

## 8.4 Dependencia de workflow

La extracción de conocimiento está integrada con:

- board
- tasks
- rituals
- next actions

Esto hace que la producción de conocimiento esté embebida en el flujo deskops.

---

## 9. Qué NO depende esencialmente de Deskops

Hay una diferencia importante entre:

- lo que hoy depende de deskops por implementación
- y lo que depende de deskops por metodología

## No dependen esencialmente de Deskops

- la disciplina 5WH1+
- la idea del átomo pequeño
- el uso de tags namespaced
- la organización taxonómica
- la composición de átomos
- la destilación de claims desde fuentes

Estas ideas podrían migrarse a una app nueva sin conservar `deskops` como sistema.

## Sí dependen hoy de Deskops

- la localización `desk/atoms/`
- el comando `deskops add atom`
- el comando `deskops list atoms`
- el comando `deskops show atom`
- el modelo `AtomDoc`
- la integración directa con tasks y board

---

## 10. Limitaciones del uso actual de Deskops para KB

El uso actual de `deskops` funciona bien para átomos simples, pero muestra límites claros.

## 10.1 Provenance no estructurada

La sección `## Procedencia` está en texto libre.

Eso dificulta:

- validación determinista
- query estructurada por evidencia
- reuse formal de anchors
- transición a samples verificables

## 10.2 El modelo no fue hecho para evidencia fuerte

`AtomDoc` sirve para:

- pregunta
- respuesta
- tags

Pero no expresa de forma nativa:

- provenance estructurado
- anchors exactos
- sample ids
- binding criptográfico a la fuente

## 10.3 Mezcla parcial entre operación y conocimiento

Tener la KB activa dentro de `desk/` aproxima demasiado:

- trabajo operativo
- conocimiento durable

Eso fue útil para bootstrapping, pero crea tensión arquitectónica si la KB crece.

## 10.4 Workspace semántico acotado

El store actual entiende esos átomos como:

- `workspace.desk.atoms`

No como una capa de conocimiento separada y autónoma.

---

## 11. Lectura arquitectónica correcta

La forma más precisa de entender el uso actual es:

> `deskops` está funcionando como la superficie práctica de la KB atómica heredada, aunque la arquitectura objetivo del repo ya busca mover la base de conocimiento hacia modelos locales de SLDB fuera de `desk/`.

O más corto:

> Deskops es hoy el contenedor activo de los átomos, pero no la arquitectura final deseada para la KB.

---

## 12. Requisitos implícitos para replicar su CLI en una app nueva

Si se quiere replicar la experiencia que hoy da `deskops` para knowledge management, la nueva app debería al menos cubrir estas capacidades.

## 12.1 Gestión básica de átomos

Capacidades equivalentes a:

- listar átomos
- mostrar un átomo por id
- crear un átomo guiado
- editar un átomo manteniendo contrato

## 12.2 Contrato atómico mínimo

La app debe soportar como mínimo:

- `id`
- `title`
- pregunta 5WH1+
- `answer`
- `tags`

## 12.3 Navegación taxonómica

Debe permitir navegar el corpus por:

- árbol conceptual
- tags
- ids
- búsqueda textual

## 12.4 Integración con provenance más fuerte

Si la nueva app va a superar a `deskops`, debería además soportar lo que hoy falta:

- provenance estructurado
- vínculo a sample/biopsia
- validación contra fuente
- anchors verificables
- binding a `source_hash_sha256`

## 12.5 Integración con flujo de trabajo

Si se quiere replicar también el valor operativo actual, la app debería considerar:

- tareas de extracción
- cobertura temática pendiente
- seguimiento de backlog de knowledge capture
- coordinación entre lectura, sampleo y atomización

---

## 13. Modelo operacional observado

El patrón real actual puede resumirse así:

1. usar `deskops` para gestionar trabajo de extracción
2. leer la fuente
3. destilar un conocimiento pequeño
4. crear/refinar un átomo en `desk/atoms/`
5. etiquetarlo
6. agregar procedencia en texto
7. reindexar con SLDB
8. consultar por CLI o búsqueda semántica

Ese es el uso de `deskops` como infraestructura práctica de knowledge management en este repo.

---

## 14. Conclusión

En `tutor_apoe`, `deskops` está siendo usado para knowledge management principalmente como:

- **contenedor del corpus de átomos**
- **contrato mínimo de atomización**
- **CLI de authoring y browsing**
- **puente entre workflow y destilación de conocimiento**

Su principal fortaleza es que hace fácil producir y consultar átomos pequeños, consistentes y composables.

Su principal limitación es que la provenance queda fuera del contrato estructurado y la KB sigue alojada en una superficie pensada originalmente para operación.

Por eso, para una app nueva comprehensiva, lo correcto no sería copiar literalmente `deskops`, sino:

- preservar su disciplina atómica y su experiencia CLI útil
- desacoplar la KB del workspace `desk/`
- incorporar provenance estructurado y validable como parte nativa del modelo
