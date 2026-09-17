"""The lexicon (spec 05): every word a session can say, derived from the world and cut by the
projection. Nothing in it is written in code except pron's function words; a word
of a world comes from a model, a field, an enum value, a relation type, or an alias.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import yaml

from pron.kernel.sexp.read_write import Sym, write
from pron.kernel.parts.word import Word
from pron.sexpr.forms.refs import models_and_relations, parse as parse_ref
from pron.world.matching.difflib_matcher import normalize
from pron.world.matching.matcher import Matcher
from pron.world.world import World

FUNCTION_WORDS = yaml.safe_load(
    (Path(__file__).parent.parent / "surface" / "function_words.yaml").read_text(
        encoding="utf-8"
    )
)
INTERNAL_MODELS = {"RelationTypeDoc", "RelationDoc", "ProjectionDoc", "AnchorDoc"}
# never a source of values to offer or promote: pron's and kgdb's own bookkeeping, and the
# ledger, whose values are this very conversation's past sentences
UNSUGGESTED_MODELS = INTERNAL_MODELS | {"MoveDoc"}


class Lexicon:
    def __init__(
        self, world: World, projection: dict[str, Any], matcher: Matcher | None = None
    ):
        self.world = world
        self.projection = projection
        self.matcher = matcher or Matcher()
        self.words: list[Word] = []
        self._by_form: dict[str, list[Word]] = {}
        self.models: list[str] = []
        self.relation_types: dict[str, dict] = {}
        self.actions: list[str] = list(projection.get("actions") or [])
        self.stores: list[str] = list(
            projection.get("stores") or ["local"]
        )  # where the nouns live; the first is where the session writes
        self._build()

    # -- building -----------------------------------------------------------------

    def _build(self) -> None:
        wanted = projection_models(self.world, self.projection)
        self.models = wanted
        for m in wanted:
            self._model_words(m)
        self._relation_words()
        self._kernel_words()
        self._alias_words()
        for w in self.words:
            self._by_form.setdefault(normalize(w.form), []).append(w)

    def _model_words(self, m: str) -> None:
        try:
            model_type = self.world.model_type(m, self.stores)
        except Exception:  # noqa: BLE001 - an unresolvable model has no words
            return
        doc = (model_type.__doc__ or "").strip().splitlines()
        motive = doc[0] if doc else f"a {m}"
        self.words.append(
            Word(m.lower(), "model", _ref("model", m), motive, f"model {m}", model=m)
        )
        split = " ".join(re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", m)).lower()
        if (
            split and split != m.lower()
        ):  # "cli command doc": the identifier split into words, until an alias says better (spec 05)
            self.words.append(
                Word(
                    split,
                    "model",
                    _ref("model", m),
                    motive,
                    f"model {m} (identifier split into words)",
                    model=m,
                )
            )
        for f in self.world.schema(m, self.stores):
            fname = f["name"]
            self.words.append(
                Word(
                    fname.replace("_", " "),
                    "field",
                    _ref("field", m, fname),
                    f["description"] or fname,
                    f"field {m}.{fname}",
                    model=m,
                    field_name=fname,
                    payload=f,
                )
            )
            for v in f.get("enum") or []:
                self.words.append(
                    Word(
                        str(v),
                        "value",
                        write([Sym("value"), Sym(m), Sym(fname), v]),
                        f"{fname} = {v}",
                        f"enum {m}.{fname}",
                        model=m,
                        field_name=fname,
                        payload={"value": v},
                    )
                )
            if (
                fname in ("system", "tags")
                and f["kind"] in ("string", "stringlist")
                and m not in UNSUGGESTED_MODELS
            ):
                # spec 05 / PLAN 11 P3: values already used in a "system" or "tags" field
                # are lexicon too, unlike other free text (never entered otherwise).
                for v in self._used_values(m, fname, f["kind"]):
                    self.words.append(
                        Word(
                            v,
                            "value",
                            write([Sym("value"), Sym(m), Sym(fname), v]),
                            f"{fname} = {v}",
                            "used value",
                            model=m,
                            field_name=fname,
                            payload={"value": v},
                        )
                    )

    def _used_values(self, model: str, field_name: str, kind: str) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for s in self.stores:
            try:
                docs = self.world.store.docs_of(model, s)
            except Exception:  # noqa: BLE001 - a model missing from a store has no docs there
                continue
            for d in docs:
                raw = d.payload.get(field_name)
                values = raw if kind == "stringlist" else ([raw] if raw else [])
                for v in values or []:
                    if isinstance(v, str) and v and v not in seen:
                        seen.add(v)
                        out.append(v)
        return out

    def _relation_words(self) -> None:
        allowed = {
            r["name"]: r.get("mode", "read")
            for r in self.projection.get("relations") or []
        }
        for name, rt in self.world.relation_types(self.stores).items():
            if allowed and name not in allowed:
                continue
            mode = allowed.get(name, "read and assert")
            payload = {**rt, "mode": mode}
            for form in dict.fromkeys((name, name.replace("_", " "))):
                self.words.append(
                    Word(
                        form,
                        "relation",
                        _ref("relation", name),
                        rt.get("description", name),
                        f"RelationTypeDoc {rt.get('doc', name)}",
                        relation=name,
                        payload=payload,
                    )
                )
            self.relation_types[name] = payload

    def _kernel_words(self) -> None:
        for verb, spec in FUNCTION_WORDS["kernel"].items():
            if (
                verb not in self.actions
            ):  # an empty actions list means no action verbs at all
                continue
            for form in spec["forms"]:
                self.words.append(
                    Word(
                        form,
                        "action",
                        _ref("action", verb),
                        spec["motive"],
                        "kernel",
                        payload={"verb": verb},
                    )
                )

    def _alias_words(self) -> None:
        wanted = self.projection.get("aliases") or ["all"]
        seen: set[str] = set()
        for s in self.stores:
            if "AnchorDoc" not in self.world.model_names(s):
                continue
            for d in self.world.store.docs_of("AnchorDoc", s):
                if d.name in seen:
                    continue
                seen.add(d.name)
                self._alias_word(d, wanted)

    def _alias_word(self, d: Any, wanted: list[str]) -> None:
        p = d.payload
        if "all" not in wanted and p["symbol"] not in wanted:
            return
        try:
            ref = parse_ref(p["ref"], p.get("steps") or [])
        except ValueError:
            return  # a ref that is not a form names nothing; the lint reports it
        if not self._alias_in_projection(ref):
            return  # its target is outside this projection: the word does not exist here (spec 01, 05)
        payload = {
            "symbol": p["symbol"],
            "ref": ref.text,
            "steps": ref.steps,
            "where": ref.where,
            "verb": ref.verb,
            "value": ref.value,
        }
        for form in p.get("forms") or [p["symbol"]]:
            self.words.append(
                Word(
                    form,
                    f"alias-{ref.kind}",
                    ref.text,
                    p.get("motive", ""),
                    f"AnchorDoc {d.name}",
                    model=ref.model,
                    field_name=ref.field_name,
                    relation=ref.relation,
                    payload=payload,
                )
            )

    def _alias_in_projection(self, ref: Any) -> bool:
        """An alias enters only if every model, relation and action verb it points at is in the projection."""
        models, relations = models_and_relations(ref)
        for m in models:
            if m not in self.models and not set(self.world.family_of(m)) & set(
                self.models
            ):
                return False
        if any(r not in self.relation_types for r in relations):
            return False
        if ref.kind == "action" and ref.verb not in self.actions:
            return False
        return not any(
            s.get("do") in ("create", "change") and s["do"] not in self.actions
            for s in ref.steps
        )

    # -- reading ----------------------------------------------------------------------

    def lookup(self, form: str) -> list[Word]:
        return list(self._by_form.get(normalize(form), []))

    def forms(self) -> list[str]:
        return sorted(self._by_form)

    def of_kind(self, *kinds: str) -> list[Word]:
        return [w for w in self.words if w.kind in kinds]

    def fields_of(self, model: str) -> list[Word]:
        family = self.world.family_of(model)
        return [w for w in self.words if w.kind == "field" and w.model in family]

    def values_of(self, model: str, field_name: str) -> list[Word]:
        return [
            w
            for w in self.words
            if w.kind == "value" and w.model == model and w.field_name == field_name
        ]

    def distinct_values(self, model: str, field_name: str) -> list[str]:
        """The distinct values a string field actually holds across this projection's stores
        and the model's family, read straight from the documents (spec 05 §Calce aproximado,
        PLAN 11 P1/P2). Free text never becomes a lexicon word (P3 only does that for
        `system`/`tags`); this is what a value suggestion ranks against."""
        family = set(self.world.family_of(model))
        seen: set[str] = set()
        out: list[str] = []
        for s in self.stores:
            for fam_model in family:
                try:
                    docs = self.world.store.docs_of(fam_model, s)
                except Exception:  # noqa: BLE001 - a model missing from a store has no docs there
                    continue
                for d in docs:
                    v = d.payload.get(field_name)
                    if isinstance(v, str) and v and v not in seen:
                        seen.add(v)
                        out.append(v)
        return out

    def model_form(self, model: str) -> str:
        """The lexicon's preferred spoken form of a model: its own word (an alias if one
        exists, else the identifier lowered — 05 §Anchors)."""
        return next(
            (w.form for w in self.words if w.kind == "model" and w.model == model),
            model.lower(),
        )

    def field_form(self, model: str, field_name: str) -> str:
        """The lexicon's preferred spoken form of a field: an alias over the field's own
        identifier form (05 §Anchors)."""
        return next(
            (
                w.form
                for w in self.words
                if w.kind == "alias-field"
                and w.model == model
                and w.field_name == field_name
            ),
            next(
                (
                    w.form
                    for w in self.words
                    if w.kind == "field"
                    and w.model == model
                    and w.field_name == field_name
                ),
                field_name.replace("_", " "),
            ),
        )

    def examples(self, k: int = 6) -> list[str]:
        """PLAN 11 P4 (spec 05): a few sentences this projection can actually resolve, built
        from its own words — never written by a world. Used so 'what can I say?' offers
        something real instead of the restaurant's own hint text."""
        if not self.models:
            return []
        model = self.models[0]
        singular = self.model_form(model)
        plural = next(
            (
                w.form
                for w in self.words
                if w.kind == "model" and w.model == model and w.form != singular
            ),
            None,
        )
        value_word = next(
            (w for w in self.words if w.kind == "value" and w.model == model), None
        )
        out: list[str] = [f"the {plural or singular}"]
        if value_word is not None:
            term = self.field_form(model, value_word.field_name or "")
            out.append(f"the {singular} {term} {value_word.form}")
        if "create" in self.actions:
            out.append(f"create a {singular}")
        return out[:k]

    def verbs_for(self, model: str) -> list[Word]:
        """Every verb a class can take, derived: relation types naming it or an ancestor
        as source or target, action aliases on its fields, compose aliases that create it,
        and the kernel verbs the projection allows."""
        family = set(self.world.family_of(model))
        out: list[Word] = []
        seen: set[tuple[str, str, str]] = set()
        for w in self.words:
            key = (w.kind, w.ref, w.form)
            if key in seen:
                continue
            hit = False
            if w.kind == "relation":
                hit = (
                    bool(family & set(w.payload.get("source_types") or []))
                    or bool(family & set(w.payload.get("target_types") or []))
                    or (
                        not w.payload.get("source_types")
                        and not w.payload.get("target_types")
                    )
                )
            elif w.kind in ("alias-action", "alias-relation", "alias-predicate"):
                hit = w.model in family or (
                    w.relation is not None
                    and self._relation_touches(w.relation, family)
                )
            elif w.kind == "alias-compose":
                first = next(
                    (s for s in w.payload.get("steps", []) if isinstance(s, dict)), {}
                )
                hit = first.get("model") in family
            elif w.kind == "action":
                hit = True
            if hit:
                seen.add(key)
                out.append(w)
        return out

    def _relation_touches(self, rel: str, family: set[str]) -> bool:
        rt = self.relation_types.get(rel, {})
        return bool(family & set(rt.get("source_types") or [])) or bool(
            family & set(rt.get("target_types") or [])
        )

    def near(
        self, query: str, kinds: Iterable[str] | None = None, k: int | None = None
    ) -> list[tuple[Word, float]]:
        """Neighbors of an unknown word among the lexicon's forms and motives. Never executed, only offered."""
        matching = self.projection.get("matching") or {}
        k = k or int(matching.get("neighbors", 3))
        threshold = float(matching.get("threshold", 0.55))
        pool = [w for w in self.words if kinds is None or w.kind in kinds]
        candidates = [(str(i), f"{w.form} {w.motive}") for i, w in enumerate(pool)]
        return [
            (pool[int(key)], round(score, 3))
            for key, score in self.matcher.rank(
                query, candidates, k=k, threshold=threshold
            )
        ]

    def table(self, model: str | None = None) -> list[dict[str, str]]:
        words = self.verbs_for(model) + self.fields_of(model) if model else self.words
        return [
            {
                "form": w.form,
                "kind": w.kind,
                "ref": w.ref,
                "motive": w.motive,
                "source": w.source,
            }
            for w in words
        ]


def projection_models(world: World, projection: dict[str, Any]) -> list[str]:
    """The models a projection can name: its list, or every model of its stores but pron's own."""
    stores = list(projection.get("stores") or ["local"])
    known: list[str] = []
    for s in stores:
        for m in world.model_names(s):
            if m not in known:
                known.append(m)
    wanted = projection.get("models") or []
    if wanted:
        return [m for m in wanted if m in known]
    return [m for m in known if m not in INTERNAL_MODELS]


def _ref(head: str, *names: str) -> str:
    return write([Sym(head), *[Sym(n) for n in names]])
