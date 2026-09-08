"""pron's lints (spec 08): run over a world and fail the build on any violation."""

from __future__ import annotations

from typing import Any

from pron.lexicon import Lexicon
from pron.world import World


def run_lints(world: World) -> list[str]:
    problems: list[str] = []
    store = world.store
    models = world.model_names()
    lex = Lexicon(world, world.projection("all"))

    # every word of the lexicon has a motive and a source in the store
    for w in lex.words:
        if not w.motive.strip():
            problems.append(f"lexicon: '{w.form}' ({w.ref}) has no motive")

    # no reference to deskops in the store
    for m in store.store_index().models:
        if "deskops" in m.model_ref:
            problems.append(f"store: model {m.name} is registered from deskops ({m.model_ref})")

    # every atom impl:here has an implements edge; every registered content model has an atom that mentions it
    if "Atom" in models:
        atoms = store.docs_of("Atom")
        rel_docs = store.docs_of("RelationDoc") if "RelationDoc" in models else []
        implemented = {d.payload["source_id"] for d in rel_docs if d.payload.get("relation_type") == "implements"}
        for a in atoms:
            if "impl:here" in (a.payload.get("tags") or []) and f"Atom:{a.name}" not in implemented:
                problems.append(f"atom {a.name} is impl:here but has no implements edge")
        internal = {"RelationTypeDoc", "RelationDoc", "AnchorDoc", "ProjectionDoc", "MoveDoc", "Atom", "CliCommandDoc", "SurfaceDoc"}
        text_of = [(a.name, (a.payload.get("title", "") + " " + a.payload.get("answer", "")).lower()) for a in atoms]
        for m in models:
            if m in internal:
                continue
            if not any(m.lower() in t for _, t in text_of):
                problems.append(f"model {m} is registered but no atom mentions it")

    # every RelationDoc has both endpoints (kgdb reports it; here it is an error)
    if "RelationDoc" in models:
        ids = {f"{d.model_name}:{d.name}" for d in store.docs()}
        for d in store.docs_of("RelationDoc"):
            for side in ("source_id", "target_id"):
                if d.payload.get(side) not in ids:
                    problems.append(f"relation {d.name}: {side} {d.payload.get(side)} does not exist")

    # every move has hash_mundo before and after
    if "MoveDoc" in models:
        for d in store.docs_of("MoveDoc"):
            if not d.payload.get("hash_before") or not d.payload.get("hash_after"):
                problems.append(f"move {d.name} lacks hash_mundo before/after")

    # command docs without drift, when they exist
    if "CliCommandDoc" in models:
        from pron.docs import synchronize_docs
        for change in synchronize_docs(world, check=True):
            problems.append(f"docs drift: {change}")
    return problems
