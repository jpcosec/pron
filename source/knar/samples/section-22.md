# 22. Representación declarativa

Idealmente un nodo debería poder ser casi enteramente data:

```clojure
{:id :research/source-scraper

 :self
 {:purpose "Acquire source documents"}

 :inputs
 [{:name :source
   :type :source/reference}]

 :outputs
 [{:name :document
   :type :source/document}]

 :knowledge
 {:read [:source-config]
  :write [:source-document]}

 :capabilities
 [:source/fetch
  :source/normalize]

 :runtime
 {:type :http-scraper}

 :state-machine
 [:idle
  :fetching
  :parsing
  :validating
  :completed]

 :completion-tests
 [:document-valid
  :document-persisted]}
```

El código implementa principalmente runtimes y primitives.

**Los agentes deberían ser mayoritariamente datos.**

---

