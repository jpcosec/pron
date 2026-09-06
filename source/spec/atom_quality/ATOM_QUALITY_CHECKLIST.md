# Atom Quality Checklist

## Estado

Borrador operativo.

## Propósito

Definir una checklist concreta para evaluar la calidad de un átomo antes de considerarlo aceptable dentro del corpus.

---

## 1. Checklist mínima de aceptación

Un átomo aceptable debe cumplir **todas** las condiciones siguientes.

### 1.1 Identidad y forma

- [ ] Tiene `id` estable y legible.
- [ ] Tiene `title` claro, específico y coherente con el `id`.
- [ ] Tiene `five_wh_one_plus` explícito.
- [ ] Tiene sección `## Answer`.
- [ ] No conserva comentarios de template ni texto placeholder.

### 1.2 Atomicidad

- [ ] Expresa **una sola afirmación principal**.
- [ ] No mezcla varias preguntas 5WH1+ en el mismo answer.
- [ ] No intenta resolver un subtema entero cuando debería descomponerse.
- [ ] El título y el answer responden exactamente la misma unidad semántica.

### 1.3 Calidad semántica

- [ ] El answer no es solo una reformulación del título.
- [ ] El answer explica la afirmación con suficiente densidad conceptual.
- [ ] El answer preserva al menos una distinción importante.
- [ ] La afirmación parece reutilizable fuera del contexto inmediato de una task.
- [ ] La afirmación es lo bastante estable como para sobrevivir reorganizaciones futuras del sistema.

### 1.4 Calidad editorial

- [ ] El answer es compacto pero no telegráfico.
- [ ] El lenguaje evita ambigüedad innecesaria.
- [ ] No contiene relleno, narración de proceso ni meta-comentario irrelevante.
- [ ] No depende de contexto conversacional para entenderse.

### 1.5 Procedencia

- [ ] Tiene campo de frontmatter `provenance`.
- [ ] La procedencia nombra una o más fuentes concretas.
- [ ] Si el átomo es síntesis, eso queda explícito.
- [ ] La procedencia no finge validación más fuerte que la disponible.

### 1.6 Tags y recuperación

- [ ] Tiene tags no vacíos.
- [ ] Los tags ayudan a recuperación, no reemplazan la semántica del átomo.
- [ ] Incluye al menos `system:*` y `topic:*` o equivalentes claramente justificables.
- [ ] Los tags son coherentes con namespaces existentes.

---

## 2. Checklist de calidad fuerte

Un átomo fuerte, además de pasar la checklist mínima, debería cumplir la mayoría de estas condiciones.

### 2.1 Distinción conceptual

- [ ] Deja claro qué distingue esta idea de ideas cercanas.
- [ ] Evita colapsar entidades, capas o relaciones diferentes.
- [ ] Si introduce una relación, el rol de cada extremo queda legible.

### 2.2 Utilidad operacional

- [ ] Ayuda a decidir algo real en modelado, authoring, revisión o migración.
- [ ] Se puede citar como regla o criterio en discusiones futuras.
- [ ] Sirve para detectar errores, huecos o anti-patrones.

### 2.3 Compatibilidad futura

- [ ] Puede recomponerse en composiciones o grafos futuros.
- [ ] No depende de un contenedor transitorio como si fuera la verdad final.
- [ ] Su wording no bloquea evolución arquitectónica innecesariamente.

### 2.4 Buena gobernanza

- [ ] Permite estimar grounding, madurez o confianza de la afirmación.
- [ ] Hace explícito si es definición, constraint, relation, workflow rule o migration rule.
- [ ] Su procedencia ayuda a auditoría y backfill posterior.

---

## 3. Señales de mala calidad

Si aparece una o más de estas señales, el átomo debe revisarse.

- [ ] El answer podría aplicarse a diez títulos distintos sin cambiar casi nada.
- [ ] El answer solo dice “X porque Y” sin explicar suficiente distinción.
- [ ] El átomo depende de conocimiento implícito no escrito.
- [ ] El título promete una relación precisa pero el answer queda genérico.
- [ ] Los tags están vacíos o son demasiado pobres para encontrarlo luego.
- [ ] La procedencia falta o es vaga.
- [ ] El átomo parece una nota de trabajo, no una unidad durable.
- [ ] El átomo contiene varias ideas que deberían separarse.

---

## 4. Regla simple de aceptación

Un átomo no debería considerarse “terminado” si falla en cualquiera de estos puntos:

- atomicidad
- answer sustantivo
- procedencia explícita
- tags mínimos
- ausencia de placeholder/template residue
