"""The lexicon (spec 05): every word a session can say, derived from the world and cut by the
projection. Nothing in it is written in code except pron's function words; a word
of a world comes from a model, a field, an enum value, a relation type, or an alias.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from pron.embedder import Matcher, normalize
from pron.world import World

FUNCTION_WORDS = yaml.safe_load(
    (Path(__file__).parent / "surface" / "function_words.yaml").read_text(
        encoding="utf-8"
    )
)
INTERNAL_MODELS = {"RelationTypeDoc", "RelationDoc", "ProjectionDoc", "AnchorDoc"}
SLOT_RE = re.compile(r"\b(N|X|Z|DAY|TIME)\b")


@dataclass
class Word:
    form: str
    kind: str  # model | field | value | relation | action | alias
    ref: str  # model:M | field:M.f | value:M.f=v | relation:R | action:<verb> | predicate:… | doc:… | compose
    motive: str
    source: str  # where it comes from, for the trace
    model: str | None = None
    field_name: str | None = None
    relation: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def slots(self) -> list[str]:
        return SLOT_RE.findall(self.form)

    def describe(self) -> str:
        return f"{self.form!r} → {self.ref} · {self.motive}"


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
            Word(m.lower(), "model", f"model:{m}", motive, f"model {m}", model=m)
        )
        split = " ".join(re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", m)).lower()
        if (
            split and split != m.lower()
        ):  # "cli command doc": the identifier split into words, until an alias says better (spec 05)
            self.words.append(
                Word(
                    split,
                    "model",
                    f"model:{m}",
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
                    f"field:{m}.{fname}",
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
                        f"value:{m}.{fname}={v}",
                        f"{fname} = {v}",
                        f"enum {m}.{fname}",
                        model=m,
                        field_name=fname,
                        payload={"value": v},
                    )
                )

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
            for form in {name, name.replace("_", " ")}:
                self.words.append(
                    Word(
                        form,
                        "relation",
                        f"relation:{name}",
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
                        f"action:{verb}",
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
        ref = p["ref"]
        head = ref.split(":", 1)[0]
        payload = {"symbol": p["symbol"], "ref": ref, "steps": p.get("steps") or []}
        model, fname, rel = self._ref_targets(ref)
        if not self._alias_in_projection(model, rel, payload["steps"], ref):
            return  # its target is outside this projection: the word does not exist here (spec 01, 05)
        for form in p.get("forms") or [p["symbol"]]:
            self.words.append(
                Word(
                    form,
                    f"alias-{head}",
                    ref,
                    p.get("motive", ""),
                    f"AnchorDoc {d.name}",
                    model=model,
                    field_name=fname,
                    relation=rel,
                    payload=payload,
                )
            )

    def _alias_in_projection(
        self, model: str | None, rel: str | None, steps: list[Any], ref: str = ""
    ) -> bool:
        """An alias enters only if every model, relation and action verb it points at is in the projection."""

        def model_ok(m: str | None) -> bool:
            return (
                m is None
                or m in self.models
                or bool(set(self.world.family_of(m)) & set(self.models))
            )

        def rel_ok(r: str | None) -> bool:
            return r is None or r in self.relation_types

        if not model_ok(model) or not rel_ok(rel):
            return False
        if ref.startswith("action:") and ref[7:].split(" ", 1)[0] not in self.actions:
            return False
        for s in steps:
            if isinstance(s, dict) and (
                not model_ok(s.get("model"))
                or not rel_ok(s.get("relation"))
                or (s.get("do") in ("create", "change") and s["do"] not in self.actions)
            ):
                return False
        return True

    @staticmethod
    def _ref_targets(ref: str) -> tuple[str | None, str | None, str | None]:
        head, _, rest = ref.partition(":")
        if head == "model":
            return rest, None, None
        if head == "field" and "." in rest:
            m, f = rest.split(".", 1)
            return m, f, None
        if head == "predicate":
            return rest.split(":", 1)[0], None, None
        if head == "relation":
            return None, None, rest
        if head == "action":
            match = re.search(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)=", rest)
            return (
                (match.group(1), match.group(2), None) if match else (None, None, None)
            )
        if head == "doc":
            return rest.split(":", 1)[0], None, None
        return None, None, None

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
