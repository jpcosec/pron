# 5. Puertos tipados

Los nodos no deberían comunicarse principalmente mediante texto libre.

Cada nodo expone:

```text
InputPort<T>
OutputPort<T>
```

Ejemplo:

```clojure
{:inputs
 [{:name :source
   :type SourceReference}]

 :outputs
 [{:name :document
   :type SourceDocument}]}
```

El orquestador puede entonces comprobar:

```text
Output<A> ──compatible──> Input<A>
```

antes de ejecutar el pipeline.

Esto convierte la arquitectura en una especie de **Lego semántico**.

---

