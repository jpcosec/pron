---
id: surface-pron-forms
system: pron
surface: forms
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/forms.py
---

# forms

## Purpose

Forms: the structured moves pron evaluates (spec 13). A sentence becomes forms after the surface
resolves every phrase (spec 06), and a runtime that already knows its documents writes the forms
directly. Both go through the same evaluation: permissions, pre-validation, writes, refresh,
MoveDoc and undo.

## How It Works

Nouns
    (doc "Model:name" ...)                     documents by export id
    (the Model clause ...)                     exactly one document; more than one is ambiguous
    (find Model clause ...)                    every document that matches
        clauses: (where "<sldb predicate>") (named "proper name")

Moves
    (show NOUN)
    (targets relation NOUN [(of Model)] [(where "...")])   what NOUN relates to
    (sources relation NOUN [(of Model)] [(where "...")])   what relates to NOUN
    (assert relation SUBJECT OBJECT)
    (create Model [(as "doc-name")] (field value) ...)   (as …) names it when the projection has no rule
    (change NOUN field value)  (add NOUN field value)  (remove NOUN field [value])
    (clean NOUN field)  (forget NOUN)
    (say alias NOUN)                           an action alias on NOUN
    (say alias (slot "$referent:M" NOUN) (slot "$object:M" NOUN [(alternatives id ...)]) [(as "doc-name")] (field value) ...)
    (undo)  (refresh)  (why [NOUN])
    (move FORM ...)                            several parts, one move

Values are strings, numbers, true, false, nil, or (list value ...).

## Commands

FormError
of_move
of_part
Compiler
