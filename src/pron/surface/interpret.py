"""From a sentence to an Interpretation (spec 06): the six steps, with the world
consulted only at steps 2 (lexicon), 4 (addresses) and 5 (types).

The constructions are fixed and listed in patterns.yaml; a world never adds one, it
adds words. A sentence coordinated with "and" is one move with several parts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from pron.lexicon import Lexicon, Word
from pron.surface.nouns import NounPhrase, field_is_string, find_noun_phrases, value_run
from pron.surface.tokens import Classifier, Item

PATTERNS = yaml.safe_load((Path(__file__).parent / "patterns.yaml").read_text(encoding="utf-8"))["constructions"]


@dataclass
class Part:
    kind: str                                  # nominal | read | assert | action | compose | why | undo | refresh
    subject: NounPhrase | None = None
    object: NounPhrase | None = None
    verb: Word | None = None                   # relation word, action word or alias
    field_name: str | None = None
    value: Any = None
    payload: dict[str, Any] = field(default_factory=dict)   # for create / compose $literals
    items: list[Item] = field(default_factory=list)
    leftovers: list[Item] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def describe(self) -> str:
        bits = [self.kind]
        if self.verb: bits.append(self.verb.ref)
        if self.subject: bits.append("subject=" + self.subject.describe())
        if self.object: bits.append("object=" + self.object.describe())
        if self.field_name: bits.append(f"{self.field_name}={self.value!r}")
        if self.payload: bits.append(f"payload={self.payload}")
        return " · ".join(bits)


@dataclass
class Interpretation:
    sentence: str
    items: list[Item]
    parts: list[Part]
    unknown: list[Item] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def forma(self) -> str:
        return "+".join(p.kind for p in self.parts) if self.parts else "none"

    def to_record(self) -> dict[str, Any]:
        return {"forma": self.forma, "items": [repr(i) for i in self.items], "parts": [p.describe() for p in self.parts],
                "unknown": [i.text for i in self.unknown], "notes": self.notes}


def examples() -> list[str]:
    return [c["example"] for c in PATTERNS]


class Interpreter:
    def __init__(self, lexicon: Lexicon, now: Any = None):
        self.lex = lexicon
        self.clf = Classifier(lexicon, now=now)

    def interpret(self, sentence: str) -> Interpretation:
        items = self.clf.classify(sentence)
        parts: list[Part] = []
        notes: list[str] = []
        for chunk in _split_on_and(items):
            part = self._part(chunk)
            if part is None:
                notes.append("no construction matches: " + " ".join(i.text for i in chunk))
                parts.append(Part("none", items=chunk))
            else:
                parts.append(part)
        unknown = [i for i in items if i.kind == "unknown" and not _used(i, parts)]
        return Interpretation(sentence, items, parts, unknown=unknown, notes=notes)

    # -- constructions, tried in patterns.yaml order --------------------------------------

    def _part(self, items: list[Item]) -> Part | None:
        for c in PATTERNS:
            fn = getattr(self, f"_c_{c['name']}", None)
            part = fn(items) if fn else None
            if part is not None:
                part.items = items
                return part
        return None

    def _c_undo(self, items):
        w = _kernel(items, "undo")
        return Part("undo", verb=w) if w and len([i for i in items if i.kind != "punct"]) == 1 else None

    def _c_refresh(self, items):
        w = _kernel(items, "refresh")
        return Part("refresh", verb=w) if w and len([i for i in items if i.kind != "punct"]) == 1 else None

    def _c_why(self, items):
        if items and items[0].kind == "wh" and items[0].meta.get("question") == "why":
            return Part("why", leftovers=[i for i in items[1:] if i.kind not in ("punct", "wh", "referent")])
        return None

    def _c_compose(self, items):
        w = _first(items, "alias-compose")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        part = Part("compose", verb=w, payload=self._literals(items, nps))
        part.notes = [f"steps: {len(w.payload.get('steps', []))}"]
        part.leftovers = _unattached(items, nps)
        part.payload["_nps"] = nps
        return part

    def _c_action_alias(self, items):
        w = _first(items, "alias-action")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        subject = nps[0] if nps else None
        rest = w.ref.split(":", 1)[1]
        verb, _, assign = rest.partition(" ")
        fld, value = assign.split("=", 1)
        return Part("action", subject=subject, verb=w, field_name=fld.split(".", 1)[1], value=value, payload={"verb": verb, "alias": True})

    def _c_create(self, items):
        w = _kernel(items, "create")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        if not nps or nps[0].model is None:
            return None
        subject = nps[0]
        payload = self._literals(items, nps, model=subject.model)
        return Part("action", subject=subject, verb=w, payload={"verb": "create", "fields": payload})

    def _c_change_to(self, items):
        w = _kernel(items, "change")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        if not nps:
            return None
        subject = nps[0]
        fld, value = self._field_and_value(items, subject)
        if fld is None:
            return None
        return Part("action", subject=subject, verb=w, field_name=fld, value=value, payload={"verb": "change"})

    def _c_set_field(self, items):
        # "add a note saying: birthday" / "set the notes to X": a field alias plus a literal, subject by referent or phrase
        fld_item = next((i for i in items if i.kind == "word" and any(w.kind in ("field", "alias-field") for w in i.words)), None)
        lit = next((i for i in items if i.kind == "literal"), None)
        if fld_item is None or lit is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        w = next(w for w in fld_item.words if w.kind in ("field", "alias-field"))
        subject = next((n for n in nps if n.referent is not None or n.model), None) or _implicit_it()
        verb = _kernel(items, "change") or _kernel(items, "add") or w
        return Part("action", subject=subject, verb=verb, field_name=w.field_name, value=lit.meta.get("value", lit.text), payload={"verb": "change", "model": w.model})

    def _c_list_op(self, items):
        for verb in ("add", "remove", "clean"):
            w = _kernel(items, verb)
            if w is None:
                continue
            nps = find_noun_phrases(items, self.lex)
            subject = next((n for n in nps if n.referent is not None), None) or (nps[-1] if nps else None)
            fld_item = next((i for i in items if i.kind == "word" and any(x.kind in ("field", "alias-field") for x in i.words)), None)
            value_item = next((i for i in items if i.kind in ("unknown", "literal", "number") and not _in_np(i, nps)), None)
            if fld_item is None:
                return None
            fw = next(x for x in fld_item.words if x.kind in ("field", "alias-field"))
            subject = subject or _implicit_it()
            value = value_item.meta.get("value", value_item.text) if value_item else None
            return Part("action", subject=subject, verb=w, field_name=fw.field_name, value=value, payload={"verb": verb, "model": fw.model})
        return None

    def _c_forget(self, items):
        w = _kernel(items, "forget")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        return Part("action", subject=nps[0] if nps else None, verb=w, payload={"verb": "forget"})

    def _c_assert_relation(self, items):
        if any(i.kind == "wh" for i in items):
            return None
        w = _first(items, "relation", "alias-relation")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        if len(nps) < 2:
            return None
        return Part("assert", subject=nps[0], object=nps[1], verb=w, leftovers=_unattached(items, nps))

    def _c_read_relation(self, items):
        w = _first(items, "relation", "alias-relation")
        if w is None:
            return None
        nps = find_noun_phrases(items, self.lex)
        rt = self.lex.relation_types.get(w.relation or "", {})
        interrogated = next((n for n in nps if n.interrogated), None)
        named = [i for i in items if i.kind == "unknown" and not _in_np(i, nps)]
        part = Part("read", verb=w, leftovers=_unattached(items, nps))
        # which side is asked: the interrogated phrase's model decides; a bare proper name takes the other side
        src_types, tgt_types = set(rt.get("source_types") or []), set(rt.get("target_types") or [])
        if interrogated is not None:
            fam = set(self.lex.world.family_of(interrogated.model))
            if fam & src_types:
                part.subject = interrogated
                part.object = _proper_phrase(named, tgt_types, nps)
            else:
                part.object = interrogated
                part.subject = _proper_phrase(named, src_types, nps)
            part.payload["asked"] = "subject" if fam & src_types else "object"
        else:
            others = [n for n in nps if not n.interrogated]
            if others:
                fam = set(self.lex.world.family_of(others[0].model)) if others[0].model else set()
                if fam & src_types or others[0].referent is not None:
                    part.subject = others[0]; part.payload["asked"] = "object"
                else:
                    part.object = others[0]; part.payload["asked"] = "subject"
        part.leftovers = [i for i in part.leftovers if not _in_np(i, [n for n in (part.subject, part.object) if n])]
        return part

    def _c_nominal(self, items):
        nps = find_noun_phrases(items, self.lex)
        if not nps or nps[0].model is None:
            return None
        return Part("nominal", subject=nps[0], leftovers=_unattached(items, nps))

    # -- helpers ------------------------------------------------------------------

    def _literals(self, items: list[Item], nps: list[NounPhrase], model: str | None = None) -> dict[str, Any]:
        """Field literals anywhere in the sentence: field word + literal/number, alias forms with slots, literals with markers."""
        out: dict[str, Any] = {}
        for np in nps:
            out.update(np.captures)
        for k, it in enumerate(items):
            if it.kind != "word":
                continue
            for w in it.words:
                if w.kind not in ("field", "alias-field"):
                    continue
                if model and w.model and w.model != model and model not in self.lex.world.family_of(w.model):
                    continue
                if it.slots:
                    out[w.field_name] = _slot_value(it)
                elif k + 1 < len(items) and items[k + 1].kind in ("literal", "number", "unknown"):
                    out[w.field_name], _ = value_run(items[k + 1:], string_field=field_is_string(self.lex, w.model, w.field_name))
                break
        return out

    def _field_and_value(self, items: list[Item], subject: NounPhrase) -> tuple[str | None, Any]:
        family = set(self.lex.world.family_of(subject.model)) if subject.model else set()
        for k, it in enumerate(items):
            if it.kind != "word" or it in subject.items:
                continue
            for w in it.words:
                if w.kind in ("field", "alias-field") and (not family or w.model in family or subject.model is None):
                    if it.slots:
                        return w.field_name, _slot_value(it)
                    if k + 1 < len(items) and items[k + 1].kind in ("literal", "number", "unknown"):
                        return w.field_name, items[k + 1].meta.get("value", items[k + 1].text)
                if w.kind == "value" and (not family or w.model in family):
                    return w.field_name, w.payload["value"]
        return None, None


def _split_on_and(items: list[Item]) -> list[list[Item]]:
    chunks, cur = [], []
    for it in items:
        if it.kind == "conj":
            if cur: chunks.append(cur)
            cur = []
        else:
            cur.append(it)
    if cur: chunks.append(cur)
    return chunks or [[]]


def _kernel(items: list[Item], verb: str) -> Word | None:
    for it in items:
        for w in it.words:
            if w.kind == "action" and w.payload.get("verb") == verb:
                return w
    return None


def _first(items: list[Item], *kinds: str) -> Word | None:
    for it in items:
        for w in it.words:
            if w.kind in kinds:
                return w
    return None


def _in_np(it: Item, nps: list[NounPhrase]) -> bool:
    return any(it is x for n in nps for x in n.items)


def _unattached(items: list[Item], nps: list[NounPhrase]) -> list[Item]:
    return [i for i in items if not _in_np(i, nps) and i.kind not in ("punct", "det", "conj", "of")]


def _used(it: Item, parts: list[Part]) -> bool:
    for p in parts:
        for n in (p.subject, p.object):
            if n and any(it is x for x in n.items):
                return True
        if any(it is x for x in p.leftovers) and p.kind == "read":
            return True
    return False


def _proper_phrase(named: list[Item], types: set[str], nps: list[NounPhrase]) -> NounPhrase | None:
    """A bare proper name on the other side of a relation takes that side's model."""
    other = next((n for n in nps if n.referent is not None), None)
    if other is not None:
        return other
    if not named or not types:
        return None
    model = sorted(types)[0]
    return NounPhrase(model, "the", "singular", proper=[named[0].text], items=[named[0]])


def _implicit_it() -> NounPhrase:
    return NounPhrase(None, None, "singular", referent=Item("referent", "it", number="singular", meta={"who": "singular", "implicit": True}))


def _slot_value(it: Item) -> Any:
    for key in ("N", "DAY", "TIME", "Z", "X"):
        if key in it.slots:
            return it.slots[key]
    return it.text
