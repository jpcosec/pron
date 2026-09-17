"""pron's lints (spec 08): run over a world and fail the build on any violation."""

from __future__ import annotations

from pron.world.lexicon import Lexicon
from pron.world.world import World


def run_lints(world: World) -> list[str]:
    return Lints(world)()


class Lints:
    """Every lint over one world, in order; each returns its problems."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.store = world.store
        self.models = world.model_names()

    def __call__(self) -> list[str]:
        lex = Lexicon(self.world, self.world.projection("all"))
        problems = self._aliases()
        # every word of the lexicon has a motive
        problems += [f"lexicon: '{w.form}' ({w.ref}) has no motive" for w in lex.words if not w.motive.strip()]
        problems += self._store_integrity() + self._deskops_models()
        problems += self._relation_endpoints() + self._move_hashes() + self._own_docs()
        return problems

    def _aliases(self) -> list[str]:
        """Every alias names something as a form (spec 05, 13)."""
        if "AnchorDoc" not in self.models:
            return []
        from pron.sexpr.forms.refs import parse as parse_ref

        problems = []
        for d in self.store.docs_of("AnchorDoc"):
            try:
                parse_ref(d.payload.get("ref", ""), d.payload.get("steps") or [])
            except ValueError as e:
                problems.append(f"alias {d.name}: ref is not a form: {e}")
        return problems

    def _store_integrity(self) -> list[str]:
        """The store's own integrity: every tracked document matches its index (sldb stores check)."""
        from sldb.cli.model_utils import resolve_model_ref
        from sldb.store.diagnostics import diagnose_store

        store = self.store
        if diagnose_store(
            store.sp, resolve_model_ref, store.project_root, pythonpath=store.pythonpath
        ).is_valid:
            return []
        return ["store: integrity FAIL (sldb stores check); run `pron refresh`"]

    def _deskops_models(self) -> list[str]:
        """No model registered from deskops."""
        return [
            f"store: model {m.name} is registered from deskops ({m.model_ref})"
            for m in self.store.store_index().models
            if "deskops" in m.model_ref
        ]

    def _relation_endpoints(self) -> list[str]:
        """Every RelationDoc has both endpoints."""
        if "RelationDoc" not in self.models:
            return []
        ids = {f"{d.model_name}:{d.name}" for d in self.store.docs()}
        return [
            f"relation {d.name}: {side} {d.payload.get(side)} does not exist"
            for d in self.store.docs_of("RelationDoc")
            for side in ("source_id", "target_id")
            if d.payload.get(side) not in ids
        ]

    def _move_hashes(self) -> list[str]:
        """Every move carries hash_mundo before and after."""
        if "MoveDoc" not in self.models:
            return []
        return [
            f"move {d.name} lacks hash_mundo before/after"
            for d in self.store.docs_of("MoveDoc")
            if not d.payload.get("hash_before") or not d.payload.get("hash_after")
        ]

    def _own_docs(self) -> list[str]:
        """pron's own knowledge base: docs without drift, every module implements a chapter."""
        if "SpecDoc" not in self.models or "SurfaceDoc" not in self.models:
            return []
        from pron.docs import synchronize_docs

        problems = [f"docs drift: {change}" for change in synchronize_docs(self.world, check=True)]
        implemented = {
            d.payload["source_id"]
            for d in self.store.docs_of("RelationDoc")
            if d.payload.get("relation_type") == "implements"
        }
        problems += [
            f"module {d.payload.get('surface')} cites no spec chapter in its docstring"
            for d in self.store.docs_of("SurfaceDoc")
            if f"SurfaceDoc:{d.name}" not in implemented
        ]
        return problems
