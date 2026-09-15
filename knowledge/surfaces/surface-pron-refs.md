---
id: surface-pron-refs
system: pron
surface: refs
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/refs.py
---

# refs

## Purpose

What a word names, as a form (spec 05, 13). Every word of the lexicon has one: a model is
(model M), a field (field M f), a value (value M f v), a relation (relation R), a verb of the
kernel (action verb). An alias writes its own:

## How It Works

(model Client)                                   a noun
    (field Client name)                              an attribute
    (where Table "capacity >= N")                    an adjective; N, X, Z and {field} are its slots
    (relation assigned_to)                           a transitive verb
    (change (it "it" Reservation) status "confirmed")   an action with a fixed field and value
    (doc "SurfaceDoc:surface-pron-infra-projector")  a proper name
    (move (create Reservation)                       a composed sentence: (created) is what the
          (assert booked_by (created) (it "her" Client))    create left, (it …) the referent of
          (assert assigned_to (created) (a Table)))         the sentence, (a M) its phrase of class M

The seven older string forms (model:M, field:M.f, predicate:M:<where>, relation:R,
action:<verb> M.f=v, doc:M:name, compose with steps) are read and turned into these.

## Commands

Ref
parse
of_form
models_and_relations
