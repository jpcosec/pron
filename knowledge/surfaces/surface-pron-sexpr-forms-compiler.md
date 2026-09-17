---
id: surface-pron-sexpr-forms-compiler
system: pron
surface: sexpr.forms.compiler
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/forms/compiler.py
---

# sexpr.forms.compiler

## Purpose

Forms: the structured language of pron (spec 13). The surface turns a sentence into forms and
does nothing else; evaluating forms resolves every noun (addresses, predicates, proper names,
complements, referents of the dialogue), asks when a noun is ambiguous or a field is missing,
checks, writes, refreshes and records. A runtime that already has its documents writes the forms.

## How It Works

Nouns
    (doc "Model:name" ...)                 documents by export id
    (the Model clause ...)                 one document
    (a Model clause ...)                   any one
    (all Model clause ...)                 every document that matches (find is the same)
    (it "word" [Model])  (them "word" [Model])  (me "word")      referents of the dialogue
        clauses: (where "<sldb predicate>")  (named "proper name")  (of NOUN)  (of-name "word" ...)
                 (plural)  (asked)  (set field value)  (not-a-value Model field "text")

Moves
    (show NOUN)
    (targets relation [NOUN] [(of Model)] [(where "...")])   what NOUN relates to
    (sources relation [NOUN] [(of Model)] [(where "...")])   what relates to NOUN
    (assert relation SUBJECT OBJECT)
    (create Model [(as "doc-name")] (field value) ...)
    (change NOUN field value)  (add NOUN field value)  (remove NOUN field [value])
    (clean NOUN field)  (forget NOUN)
    (say alias NOUN)                                 an action alias
    (say alias SUBJECT OBJECT)                       a relation alias
    (say alias (slot "$referent:M" NOUN) (slot "$object:M" NOUN) [(as "doc-name")] (field value) ...)
    (undo)  (refresh)  (why [NOUN])
    (move FORM ...)                                  several parts, one move

Values are strings, numbers, true, false, nil, or (list value ...).

## Commands

Compiler
