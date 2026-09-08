"""pron's lints (spec 08): run over a world and fail the build on any violation."""

from __future__ import annotations

from pron.lexicon import Lexicon
from pron.world import World


def run_lints(world: World) -> list[str]:
    problems: list[str] = []
    store = world.store
    models = world.model_names()
    lex = Lexicon(world, world.projection("all"))

    # every word of the lexicon has a motive
    for w in lex.words:
        if not w.motive.strip():
            problems.append(f"lexicon: '{w.form}' ({w.ref}) has no motive")

    # no model registered from deskops
    for m in store.store_index().models:
        if "deskops" in m.model_ref:
            problems.append(f"store: model {m.name} is registered from deskops ({m.model_ref})")

    # every RelationDoc has both endpoints
    if "RelationDoc" in models:
        ids = {f"{d.model_name}:{d.name}" for d in store.docs()}
        for d in store.docs_of("RelationDoc"):
            for side in ("source_id", "target_id"):
                if d.payload.get(side) not in ids:
                    problems.append(f"relation {d.name}: {side} {d.payload.get(side)} does not exist")

    # every move carries hash_mundo before and after
    if "MoveDoc" in models:
        for d in store.docs_of("MoveDoc"):
            if not d.payload.get("hash_before") or not d.payload.get("hash_after"):
                problems.append(f"move {d.name} lacks hash_mundo before/after")

    # pron's own knowledge base: docs without drift, every module implements a chapter
    if "SpecDoc" in models and "SurfaceDoc" in models:
        from pron.docs import synchronize_docs
        for change in synchronize_docs(world, check=True):
            problems.append(f"docs drift: {change}")
        implemented = {d.payload["source_id"] for d in store.docs_of("RelationDoc") if d.payload.get("relation_type") == "implements"}
        for d in store.docs_of("SurfaceDoc"):
            if f"SurfaceDoc:{d.name}" not in implemented:
                problems.append(f"module {d.payload.get('surface')} cites no spec chapter in its docstring")
    return problems
