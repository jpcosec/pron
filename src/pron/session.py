"""A session: one world, one projection, one speaker, and the turn loop (spec 06, 07, 11).

turn(sentence): read hash_mundo → interpret → resolve → verify → decide → execute →
refresh if written → write the MoveDoc → answer. Everything the turn did is in the
trace; every trace line is a real call.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pron.dialogue import Dialogue, Pending
from pron.display import Display
from pron.embedder import Embedder, Matcher
from pron.ids import address_of, doc_of, is_local, join_id, model_of, scope as _scope
from pron.kernel import Kernel
from pron.ledger import Ledger
from pron.lexicon import Lexicon
from pron.resolve import Resolution, address_to_export_id, resolve
from pron.response import Response  # noqa: F401 - re-exported: session.Response is the public name
from pron.store import StoreError
from pron.surface.interpret import Interpretation, Interpreter, Part, examples
from pron.surface.nouns import NounPhrase
from pron.verbs import Verbs
from pron.world import World


class Session:
    def __init__(
        self,
        world: World,
        projection: str = "all",
        speaker: str = "",
        speaker_address: str | None = None,
        now: str | datetime | None = None,
        embedder: Embedder | None = None,
        read_only: bool = False,
        home: str | None = None,
    ):
        """read_only: the projection's actions are dropped and every relation is in mode read, so
        nothing said in this session writes; the application decides that per session (spec 05).
        home: the linked store this session's world is (spec 01 §Un mundo en varios stores): its
        projections are read from there, its 'local' is that store, and that is where the session
        writes; None is the world's own store."""
        self.world = world
        self.projection_name = projection
        self.read_only = read_only
        self.home = None if is_local(home) else home
        self.now = now
        self.dialogue = Dialogue(speaker=speaker, speaker_address=speaker_address)
        self.matcher = Matcher(embedder)
        self.hash = world.hash_mundo()
        self._load()
        self.ledger = Ledger(world, self.write_store)

    def _load(self) -> None:
        self.projection = self.world.projection(self.projection_name, self.home)
        stores = list(self.projection.get("stores") or ["local"])
        self.write_store: str | None = None if is_local(stores[0]) else stores[0]
        if self.read_only:
            names = [r["name"] for r in self.projection.get("relations") or []] or list(
                self.world.relation_types(stores)
            )
            self.projection = dict(
                self.projection,
                actions=[],
                relations=[{"name": n, "mode": "read"} for n in names],
            )
        if self.matcher.embedder is not None:
            self.matcher.bind_cache(
                self.world.root
                / ".pron"
                / f"lexicon.{self.hash}.{self.home or 'local'}.{self.projection_name}.{self.matcher.id()}.json"
            )
        self.lex = Lexicon(self.world, self.projection, self.matcher)
        self.interpreter = Interpreter(self.lex, now=self.now)
        self.verbs = Verbs(self.lex)
        self.kernel = Kernel(self.verbs, self.projection)
        self.display = Display(self.world, self.projection, self.verbs)

    # -- the turn ---------------------------------------------------------------------------

    def turn(self, sentence: str) -> Response:
        at = datetime.now(timezone.utc).replace(microsecond=0)
        move_id = self.ledger.new_id(at)
        state_before = self.dialogue.state
        trace: list[str] = []
        record: dict[str, Any] = {"queries": [], "writes": [], "edges": []}
        hash_before = self._sync(trace)
        refers_to = ""
        try:
            if self.dialogue.pending is not None:
                resp, refers_to = self._continue(sentence, trace, record)
            else:
                corrected = self._correction(sentence)
                hole = self.dialogue.last_missing
                self.dialogue.last_missing = None
                if corrected is not None:
                    assert hole is not None
                    refers_to = hole.get("move_id", "")
                    record["corrects"] = {
                        "move": refers_to,
                        "fragment": sentence,
                        "sentence": corrected,
                    }
                    trace.append(f"correction of the last missing turn: {corrected!r}")
                    resp = self._new_sentence(corrected, trace, record)
                else:
                    resp = self._new_sentence(sentence, trace, record)
        except StoreError as e:
            resp = Response(f"Could not do that: {e}", "error")
            record["error"] = str(e)
        if resp.outcome == "missing" and self.dialogue.last_missing is not None:
            self.dialogue.last_missing["move_id"] = move_id
        hash_after = self.world.hash_mundo() if record["writes"] else hash_before
        if record["writes"]:
            self.kernel.warnings = []
        record["interpretation"] = record.get("interpretation", {})
        record["trace"] = list(trace)
        self.ledger.write(
            move_id=move_id,
            at=at,
            speaker=self.dialogue.speaker,
            sentence=sentence,
            outcome=resp.outcome,
            state_before=state_before,
            state_after=self.dialogue.state,
            hash_before=hash_before,
            hash_after=hash_after,
            refers_to=refers_to,
            record=record,
        )
        self.hash = hash_after
        resp.trace = trace
        resp.move_id = move_id
        resp.record = record
        return resp

    def _sync(self, trace: list[str]) -> str:
        current = self.world.hash_mundo()
        if current != self.hash:
            trace.append(
                "the world changed outside pron: lexicon and projection reloaded"
            )
            self.hash = current
            self._load()
        return current

    # -- new sentence ------------------------------------------------------------------------

    def _new_sentence(
        self,
        sentence: str,
        trace: list[str],
        record: dict[str, Any],
        retry: bool = False,
    ) -> Response:
        self._sentence = sentence
        interp = self.interpreter.interpret(sentence)
        record["interpretation"] = interp.to_record()
        trace.append("interpretation: " + interp.forma)
        if interp.unknown and all(p.kind in ("none", "nominal") for p in interp.parts):
            return self._missing_words(interp, trace, record)
        if any(p.kind == "none" for p in interp.parts):
            return Response(
                "I can understand: " + " · ".join(examples()[:6]) + " …", "missing"
            )
        # resolve every phrase of every part before executing anything
        plans = []
        for part in interp.parts:
            plan = self._plan(part, trace, record)
            if isinstance(plan, Response):
                return plan
            plans.append(plan)
        # every write of the move validated before the first one (spec 11 §7)
        self._prevalidate(interp.parts, plans, trace, record)
        # hash_mundo read again just before executing (spec 11 §5)
        current = self.world.hash_mundo()
        if current != self.hash:
            if retry:
                return Response(
                    "The world is changing under us; say it again.", "error"
                )
            trace.append(
                "the world changed while understanding: lexicon and projection reloaded, understanding again"
            )
            self.hash = current
            self._load()
            return self._new_sentence(sentence, trace, record, retry=True)
        # execute in order, one refresh at the end
        texts = []
        wrote = False
        for part, plan in zip(interp.parts, plans):
            text, did_write = self._execute(part, plan, trace, record)
            texts.append(text)
            wrote = wrote or did_write
        if wrote:
            self._refresh(trace)
        warnings = list(dict.fromkeys(self.kernel.warnings))
        self.kernel.warnings = []
        text = " ".join(t for t in texts if t)
        if warnings:
            text += " Heads up: " + "; ".join(warnings) + "."
        return Response(text, "unico")

    def _missing_words(
        self, interp: Interpretation, trace: list[str], record: dict[str, Any]
    ) -> Response:
        word = interp.unknown[0].text
        near = self.lex.near(word)
        names = [f"*{w.form}*" for w, _ in near]
        record["missing"] = {
            "word": word,
            "near": [w.form for w, _ in near],
            "matcher": self.matcher.id(),
        }
        trace.append(
            f"'{word}' is not in the projection · near ({self.matcher.id()}): {', '.join(names) or 'nothing'}"
        )
        return Response(
            f'I don\'t have "{word}".'
            + (
                f" Did you mean {' or '.join(names)}?"
                if names
                else " I can understand: " + " · ".join(examples()[:4]) + " …"
            ),
            "missing",
        )

    # -- planning: resolve the phrases of a part -----------------------------------------------

    def _plan(
        self, part: Part, trace: list[str], record: dict[str, Any]
    ) -> dict[str, Any] | Response:
        plan: dict[str, Any] = {}
        if part.kind in ("undo", "refresh", "why"):
            return plan
        if part.kind == "compose":
            return self._plan_compose(part, trace, record)
        for role in ("subject", "object"):
            np = getattr(part, role)
            if np is None or (
                role == "subject"
                and part.kind == "action"
                and part.payload.get("verb") == "create"
            ):
                continue  # a create's subject does not exist yet: nothing to resolve
            need_model = self._needed_model(part, role)
            res = self._resolve_phrase(np, need_model, trace, record)
            if res.outcome == "ambiguo":
                return self._ask(part, role, res, record)
            if res.outcome == "missing":
                return self._missing(res, trace, record)
            plan[role] = res
        if part.kind == "action" and part.payload.get("verb") == "create":
            assert part.subject is not None and part.subject.model is not None
            missing = self.kernel.required_missing(
                part.subject.model, part.payload["fields"]
            )
            if missing:
                return self._ask_data(part, missing[0], record)
        return plan

    def _needed_model(self, part: Part, role: str) -> str | None:
        if (
            part.kind in ("read", "assert")
            and part.verb is not None
            and part.verb.relation
        ):
            rt = self.lex.relation_types.get(part.verb.relation, {})
            types = (
                rt.get("source_types" if role == "subject" else "target_types") or []
            )
            return types[0] if types else None
        if part.kind == "action":
            return part.payload.get("model") or (part.verb.model if part.verb else None)
        return None

    def _resolve_phrase(
        self,
        np: NounPhrase,
        need_model: str | None,
        trace: list[str],
        record: dict[str, Any],
    ) -> Resolution:
        if np.referent is not None:
            who = np.referent.meta.get("who")
            if who == "speaker":
                found = self.dialogue.speaker_referent()
                if not found:
                    return Resolution(
                        np, [], "missing", note="I don't know who you are in this world"
                    )
            else:
                family = self.world.family_of(need_model) if need_model else None
                found = self.dialogue.referent(np.number, need_model, family)
            if not found:
                return Resolution(
                    np,
                    [],
                    "missing",
                    note=f"'{np.referent.text}' has no antecedent"
                    + (f" of class {need_model}" if need_model else ""),
                )
            if np.number == "singular" and len(found) > 1:
                return Resolution(np, [], "ambiguo", candidates=found)
            trace.append(f"'{np.referent.text}' → {', '.join(found)}")
            np.model = np.model or model_of(address_to_export_id(found[0]))
            return Resolution(np, found, "unico", note="referent")
        res = resolve(np, self.lex)
        trace.extend(res.queries)
        record["queries"].extend(res.queries)
        if res.note:
            trace.append(res.note)
        self._note_reads(res.addresses + res.also_read, record)
        return res

    def _note_reads(self, addresses: list[str], record: dict[str, Any]) -> None:
        """Spec 07: every document a turn resolved, with the hash_c it had when read."""
        reads = record.setdefault("reads", [])
        seen = {r["address"] for r in reads}
        for a in addresses:
            eid = address_to_export_id(a)
            if eid in seen or ":" not in eid:
                continue
            try:
                reads.append({"address": eid, "hash_c": self.world.store.hash_of(eid)})
            except StoreError:
                continue

    def _plan_compose(
        self, part: Part, trace: list[str], record: dict[str, Any]
    ) -> dict[str, Any] | Response:
        assert part.verb is not None
        np: NounPhrase | None
        plan: dict[str, Any] = {"steps": []}
        nps: list[NounPhrase] = part.payload.get("_nps", [])
        for step in part.verb.payload.get("steps", []):
            resolved = {}
            for slot_key in ("source", "target"):
                slot = step.get(slot_key)
                if (
                    not isinstance(slot, str)
                    or not slot.startswith("$")
                    or slot == "$created"
                ):
                    continue
                kind, _, model = slot[1:].partition(":")
                if kind == "referent":
                    np = next(
                        (n for n in nps if n.referent is not None), None
                    ) or NounPhrase(
                        None, None, "singular", referent=_pronoun_item(part)
                    )
                    res = self._resolve_phrase(np, model, trace, record)
                elif kind == "object":
                    np = next(
                        (
                            n
                            for n in nps
                            if n.model and model in self.world.family_of(n.model)
                        ),
                        None,
                    )
                    if np is None:
                        return Response(
                            f"I need a {model.lower()} in that sentence.", "missing"
                        )
                    res = self._resolve_phrase(np, model, trace, record)
                else:
                    continue
                if res.outcome == "ambiguo":
                    return self._ask(part, slot_key, res, record)
                if res.outcome == "missing":
                    return self._missing(res, trace, record)
                resolved[slot_key] = res
            plan["steps"].append(resolved)
        steps = part.verb.payload.get("steps", [])
        if not self.kernel.allowed("create") and any(
            s.get("do") == "create" for s in steps
        ):
            return Response("In this session I cannot create.", "missing")
        if not self.kernel.allowed("change") and any(
            s.get("do") == "change" for s in steps
        ):
            return Response("In this session I cannot change.", "missing")
        for s in steps:
            if s.get("do") == "assert" and "assert" not in self.lex.relation_types.get(
                s.get("relation"), {}
            ).get("mode", "read"):
                return Response(
                    f"In this session I can tell you about {s.get('relation')}, not assert it.",
                    "missing",
                )
        return plan

    # -- pending ----------------------------------------------------------------------------------

    def _ask(
        self, part: Part, role: str, res: Resolution, record: dict[str, Any]
    ) -> Response:
        labels = self.display.names(res.candidates)
        self.dialogue.open(
            Pending(
                "choice",
                "",
                part.items and " ".join(i.text for i in part.items) or "",
                candidates=list(res.candidates),
                labels=labels,
                slot=role,
                state={"part": part},
            )
        )
        record["candidates"] = list(res.candidates)
        listing = " · ".join(f"({i + 1}) {label}" for i, label in enumerate(labels))
        return Response(f"Which one? {listing}", "ambiguo")

    def _ask_data(
        self, part: Part, field_name: str, record: dict[str, Any]
    ) -> Response:
        assert part.subject is not None
        self.dialogue.open(
            Pending(
                "data",
                "",
                " ".join(i.text for i in part.items),
                field_name=field_name,
                model=part.subject.model,
                state={"part": part},
            )
        )
        record["missing_field"] = field_name
        return Response(f"{field_name.replace('_', ' ').capitalize()}?", "ambiguo")

    def _missing(
        self, res: Resolution, trace: list[str], record: dict[str, Any]
    ) -> Response:
        record["missing"] = {"note": res.note, "candidates": res.candidates}
        if res.phrase.unknown_values:
            model, fld, text = res.phrase.unknown_values[0]
            self.dialogue.last_missing = {
                "sentence": self._sentence,
                "model": model,
                "field": fld,
                "text": text,
            }
        if res.candidates and res.phrase.unknown_values:
            names = " or ".join(f"*{c}*" for c in res.candidates)
            return Response(f"{res.note}. Did you mean {names}?", "missing")
        if res.candidates:
            names = " or ".join(self.display.names(res.candidates))
            return Response(f"{res.note}. Did you mean {names}?", "missing")
        return Response(res.note + ".", "missing")

    def _correction(self, sentence: str) -> str | None:
        """Spec 06: a verbless fragment that fits the hole of the last missing turn ("on the
        terrace" after a missing in `zone`) is a correction; the previous sentence is said again
        whole, with the hole filled. Not a pending: that turn ended and was recorded."""
        hole = self.dialogue.last_missing
        if not hole or not hole.get("field"):
            return None
        interp = self.interpreter.interpret(sentence)
        if any(p.kind not in ("none", "nominal") for p in interp.parts):
            return None
        known = {w.form for w in self.lex.values_of(hole["model"], hole["field"])}
        values: set[str] = set()
        for it in interp.items:
            for w in it.words:
                if (
                    w.kind == "value"
                    and w.model == hole["model"]
                    and w.field_name == hole["field"]
                ):
                    values.add(w.form)
                elif (
                    w.kind == "alias-predicate" and w.model == hole["model"]
                ):  # "on the Z" with Z a value of the field
                    values |= {str(v) for v in it.slots.values() if str(v) in known}
        if len(values) != 1:
            return None
        return hole["sentence"].replace(hole["text"], values.pop())

    def _prevalidate(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        trace: list[str],
        record: dict[str, Any],
    ) -> None:
        """Spec 11 §7: before the first write of a move, every write is computed and checked (coercion,
        transition, relation type, cardinality, condition, sldb roundtrip) over the payloads the
        earlier writes of the same move would leave. Raises StoreError; nothing was touched."""
        overlay: dict[str, dict[str, Any]] = {}
        try:
            self._dry_parts(parts, plans, overlay)
        finally:
            if self.kernel.notes:
                trace.extend("pre-validation: " + n for n in self.kernel.notes)
                record["queries"].extend(self.kernel.notes)
                self.kernel.notes = []

    def _dry_parts(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        for part, plan in zip(parts, plans):
            if part.kind == "action":
                verb = part.payload.get(
                    "verb", part.verb.payload.get("verb") if part.verb else None
                )
                if not self.kernel.allowed(verb):
                    raise StoreError(f"in this session I cannot {verb}")
                if verb == "create":
                    assert part.subject is not None and part.subject.model is not None
                    self.kernel.dry_create(
                        part.subject.model, part.payload["fields"], overlay
                    )
                else:
                    for e in plan["subject"].export_ids():
                        self.kernel.dry_run(
                            verb, e, part.field_name, part.value, overlay
                        )
            elif part.kind == "assert":
                assert part.verb is not None and part.verb.relation is not None
                self._dry_assert(
                    part.verb.relation,
                    plan["subject"].export_ids(),
                    plan["object"].export_ids(),
                    overlay,
                )
            elif part.kind == "compose":
                assert part.verb is not None
                created_model: str | None = None
                literals = {
                    k: v for k, v in part.payload.items() if not k.startswith("_")
                }
                for step, resolved in zip(
                    part.verb.payload.get("steps", []), plan["steps"]
                ):
                    do = step.get("do")
                    if (
                        "$created" in (step.get("source"), step.get("target"))
                        and created_model is None
                    ):
                        raise StoreError(
                            "composition references $created before create"
                        )
                    created_id = (
                        join_id(self.write_store, created_model, "$created")
                        if created_model is not None
                        else None
                    )
                    if do == "create":
                        created_model = step["model"]
                        if created_model is None:
                            raise StoreError("create requires a model")
                        fields = {
                            k: v
                            for k, v in literals.items()
                            if any(
                                f["name"] == k
                                for f in self.kernel.schema(created_model)
                            )
                        }
                        self.kernel.dry_create(created_model, fields, overlay)
                    elif do == "assert":
                        created_ids = [created_id] if created_id is not None else []
                        src = (
                            created_ids
                            if step.get("source") == "$created"
                            else resolved["source"].export_ids()
                        )
                        tgt = (
                            created_ids
                            if step.get("target") == "$created"
                            else resolved["target"].export_ids()
                        )
                        self._dry_assert(step["relation"], src, tgt, overlay)
                    elif do == "change":
                        tgt = (
                            created_id
                            if step.get("target") == "$created"
                            else resolved["target"].export_ids()[0]
                        )
                        if tgt is None:
                            raise StoreError(
                                "composition references $created before create"
                            )
                        if not tgt.endswith(":$created"):
                            self.kernel.dry_run(
                                "change", tgt, step["field"], step["value"], overlay
                            )
            elif part.kind == "undo" and not self.kernel.allowed("undo"):
                raise StoreError("in this session I cannot undo")

    def _dry_assert(
        self,
        rel: str,
        sources: list[str],
        targets: list[str],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        rt = self.verbs.relation_type(rel)
        if "assert" not in self.lex.relation_types.get(rel, {}).get("mode", "read"):
            raise StoreError(
                f"in this session I can tell you about {rel}, not assert it"
            )
        for s in sources:
            for t in targets:
                ok, why = self.verbs.applies(rel, model_of(s), model_of(t))
                if not ok:
                    raise StoreError(why)
                if not s.endswith(":$created") and not t.endswith(":$created"):
                    ok, why = self.verbs.cardinality_ok(rel, s, t)
                    if not ok:
                        raise StoreError(why)
                if rt.get("condition"):
                    holds, query = self.verbs.condition_holds(
                        rt["condition"], s, over=t, overlay=overlay
                    )
                    self.kernel.notes.append(query)
                    if not holds:
                        raise StoreError(
                            f"condition '{rt['condition']}' does not hold for {s} → {t} ({query})"
                        )

    def _continue(
        self, sentence: str, trace: list[str], record: dict[str, Any]
    ) -> tuple[Response, str]:
        pending = self.dialogue.pending
        assert pending is not None
        interp = self.interpreter.interpret(sentence)
        kinds = [w.kind for i in interp.items for w in i.words]
        what = self.dialogue.classify_reply(sentence, kinds)
        if what == "order":
            trace.append("pending dropped: a new order")
            self.dialogue.close()
            record["dropped_pending"] = pending.sentence
            return self._new_sentence(sentence, trace, record), pending.move_id
        if sentence.strip().lower().rstrip("?.! ") in ("none", "neither", "no"):
            self.dialogue.close()
            return Response("Cancelled.", "unico"), pending.move_id
        part: Part = pending.state["part"]
        if pending.kind == "data":
            value = sentence.strip()
            part.payload["fields"][pending.field_name] = value
            self.dialogue.close()
            trace.append(
                f"{pending.field_name} = {value!r} (answer to the pending question)"
            )
            return self._resume(part, trace, record), pending.move_id
        picks = self.dialogue.pick(sentence, self.matcher)
        if len(picks) != 1:
            listing = " · ".join(
                f"({i + 1}) {label}" for i, label in enumerate(pending.labels)
            )
            return Response(
                f"Still pending. Which one? {listing}", "ambiguo"
            ), pending.move_id
        chosen = pending.candidates[picks[0]]
        trace.append(
            f"'{sentence.strip()}' → {chosen} (answer to the pending question)"
        )
        np = getattr(part, pending.slot, None)
        self.dialogue.close()
        if np is not None:
            np.proper = []
            np.predicates = [f'doc ~ "^{doc_of(address_to_export_id(chosen))}$"']
        return self._resume(part, trace, record), pending.move_id

    def _resume(self, part: Part, trace: list[str], record: dict[str, Any]) -> Response:
        interp = Interpretation(
            part.items and " ".join(i.text for i in part.items) or "", [], [part]
        )
        record["interpretation"] = interp.to_record()
        plan = self._plan(part, trace, record)
        if isinstance(plan, Response):
            return plan
        self._prevalidate([part], [plan], trace, record)
        text, wrote = self._execute(part, plan, trace, record)
        if wrote:
            self._refresh(trace)
        warnings = list(dict.fromkeys(self.kernel.warnings))
        self.kernel.warnings = []
        return Response(
            text + (" Heads up: " + "; ".join(warnings) + "." if warnings else ""),
            "unico",
        )

    # -- execution --------------------------------------------------------------------------

    def _execute(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> tuple[str, bool]:
        if part.kind == "nominal":
            return self._answer_nominal(plan["subject"]), False
        if part.kind == "read":
            return self._read(part, plan, trace, record), False
        if part.kind == "assert":
            return self._assert(part, plan, trace, record), True
        if part.kind == "action":
            return self._action(part, plan, trace, record)
        if part.kind == "compose":
            return self._compose(part, plan, trace, record), True
        if part.kind == "refresh":
            self._refresh(trace)
            return "Refreshed.", False
        if part.kind == "undo":
            return self._undo(trace, record), True
        if part.kind == "why":
            return self._why(part, trace, record), False
        return "", False

    def _answer_nominal(self, res: Resolution) -> str:
        self.dialogue.remember(res.addresses, res.phrase.model)
        if not res.addresses:
            return "None."
        names = self.display.names(res.addresses)
        if len(names) == 1:
            return names[0] + "."
        return f"{len(names)}: " + "; ".join(names) + "."

    def _read(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> str:
        assert part.verb is not None and part.verb.relation is not None
        rel = part.verb.relation
        asked = part.payload.get("asked", "object")
        if asked == "object" and "subject" in plan:
            reads = [
                self.verbs.edges_from(e, rel) for e in plan["subject"].export_ids()
            ]
            found = [e["target"] for r in reads for e in r.edges]
        elif "object" in plan:
            reads = [self.verbs.edges_to(e, rel) for e in plan["object"].export_ids()]
            found = [e["source"] for r in reads for e in r.edges]
        else:
            return "I need to know whose."
        for r in reads:
            trace.extend(r.queries)
            record["queries"].extend(r.queries)
            record["edges"].extend(r.edges)
            if r.source == "sldb":
                trace.append(
                    "edges read from the RelationDocs in sldb: the graph is not fresh"
                )
        # extra modifiers on the asked side ("for Friday") become predicates intersected with the found set
        asked_np = part.subject if asked == "subject" else part.object
        if asked_np is not None and part.leftovers:
            found = self._filter_by_leftovers(
                found, asked_np, part.leftovers, trace, record
            )
        addresses = [address_of(e) for e in dict.fromkeys(found)]
        self._note_reads(addresses, record)
        model = asked_np.model if asked_np else None
        self.dialogue.remember(addresses, model)
        if not addresses:
            return "None."
        names = self.display.names(addresses)
        return (
            names[0] if len(names) == 1 else f"{len(names)}: " + "; ".join(names)
        ) + "."

    def _filter_by_leftovers(
        self, found: list[str], np: NounPhrase, leftovers, trace, record
    ) -> list[str]:
        from pron.surface.nouns import _word_modifier

        assert np.model is not None
        for it in leftovers:
            if it.kind == "literal" and it.meta.get("kind") == "date":
                fld = next(
                    (
                        f["name"]
                        for f in self.world.schema(np.model, self.lex.stores)
                        if f["name"] == "date"
                    ),
                    None,
                )
                if fld:
                    np.predicates.append(f'{fld} = "{it.meta["value"]}"')
            elif it.kind == "word":
                _word_modifier(it, None, np, self.lex)
        if not np.predicates:
            return found
        keep: set[str] | None = None
        for where in np.predicates:
            hits: set[str] = set()
            for sc in (_scope(s, np.model) for s in self.lex.stores):
                got = {
                    address_to_export_id(a) for a in self.world.store.find(sc, where)
                }
                q = f"find '{sc}' --where '{where}' → {len(got)}"
                trace.append(q)
                record["queries"].append(q)
                hits |= got
            keep = hits if keep is None else keep & hits
        return [e for e in found if e in (keep or set())]

    def _assert(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> str:
        assert part.verb is not None and part.verb.relation is not None
        rel = part.verb.relation
        mode = self.lex.relation_types.get(rel, {}).get("mode", "read")
        if "assert" not in mode:
            raise StoreError(
                f"in this session I can tell you about {rel}, not assert it"
            )
        texts = []
        for s in plan["subject"].export_ids():
            for t in plan["object"].export_ids():
                doc_name, _ = self.verbs.assert_edge(
                    rel, s, t, (self.projection.get("naming") or {}).get("RelationDoc")
                )
                trace.append(f"docs create --model RelationDoc {doc_name}")
                record["writes"].append(
                    {
                        "verb": "assert",
                        "address": join_id(self.write_store, "RelationDoc", doc_name),
                        "after": {"source_id": s, "target_id": t, "relation_type": rel},
                        "done": True,
                    }
                )
                texts.append(
                    f"{self.display.name(s)} {rel.replace('_', ' ')} {self.display.name(t)}"
                )
        self.dialogue.remember(plan["subject"].addresses, plan["subject"].phrase.model)
        return "Done: " + "; ".join(texts) + "."

    def _action(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> tuple[str, bool]:
        verb = part.payload.get(
            "verb", part.verb.payload.get("verb") if part.verb else None
        )
        if not self.kernel.allowed(verb):
            raise StoreError(f"in this session I cannot {verb}")
        if verb == "create":
            assert part.subject is not None and part.subject.model is not None
            model = part.subject.model
            w = self.kernel.create(model, part.payload["fields"])
            trace.append(f"docs create --model {model} {w.address} {w.after}")
            record["writes"].append(w.record())
            addr = address_of(w.address)
            self.dialogue.remember([addr], model)
            self.dialogue.last_written = w.address
            return f"Created {model.lower()} {self.display.name(addr)}.", True
        targets = plan["subject"].export_ids()
        writes = []
        for e in targets:
            self.kernel.expect(e)
        # pre-validate the whole batch before the first write
        for e in targets:
            if verb == "change":
                if part.field_name is None:
                    raise StoreError("change requires a field")
                self.kernel.coerce(model_of(e), part.field_name, part.value)
        for e in targets:
            if verb in ("change", "add", "remove", "clean") and part.field_name is None:
                raise StoreError(f"{verb} requires a field")
            if verb == "change":
                assert part.field_name is not None
                w = self.kernel.change(e, part.field_name, part.value)
            elif verb == "add":
                assert part.field_name is not None
                w = self.kernel.add(e, part.field_name, part.value)
            elif verb == "remove":
                assert part.field_name is not None
                w = self.kernel.remove(e, part.field_name, part.value)
            elif verb == "clean":
                assert part.field_name is not None
                w = self.kernel.clean(e, part.field_name)
            elif verb == "forget":
                w = self.kernel.forget(e)
            else:
                raise StoreError(f"unknown verb {verb}")
            writes.append(w)
            trace.extend(self.kernel.notes)
            record["queries"].extend(self.kernel.notes)
            self.kernel.notes = []
            trace.append(
                f"{w.verb} {w.address}"
                + (
                    f".{w.field_name}: {w.before!r} → {w.after!r}"
                    if w.field_name
                    else ""
                )
                + ("" if w.done else f" (not done: {w.note})")
            )
            record["writes"].append(w.record())
        self.dialogue.remember(plan["subject"].addresses, plan["subject"].phrase.model)
        self.dialogue.last_written = targets[0] if targets else None
        done = [w for w in writes if w.done]
        skipped = [w for w in writes if not w.done]
        if verb == "forget":
            text = f"Forgot {len(done)}."
        elif len(targets) == 1:
            text = "Done." if done else f"Nothing to do ({skipped[0].note})."
        else:
            text = (
                f"Done on {len(done)}"
                + (f"; {len(skipped)} already like that" if skipped else "")
                + "."
            )
        return text, bool(done)

    def _compose(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> str:
        assert part.verb is not None
        created: str | None = None
        texts = []
        steps = part.verb.payload.get("steps", [])
        literals = {k: v for k, v in part.payload.items() if not k.startswith("_")}
        for step, resolved in zip(steps, plan["steps"]):
            do = step.get("do")
            if do == "create":
                model = step["model"]
                fields = {
                    k: v
                    for k, v in literals.items()
                    if any(f["name"] == k for f in self.kernel.schema(model))
                }
                related = {}
                for later, later_res in zip(steps, plan["steps"]):
                    if (
                        later.get("do") == "assert"
                        and later.get("source") == "$created"
                        and "target" in later_res
                    ):
                        tid = later_res["target"].export_ids()[0]
                        related[later["relation"]] = self.world.store.payload_of(tid)
                missing = self.kernel.required_missing(model, fields)
                if missing:
                    raise StoreError(f"{model} needs {', '.join(missing)}")
                w = self.kernel.create(model, fields, related)
                created = w.address
                trace.append(f"docs create --model {model} {created} {w.after}")
                record["writes"].append(w.record())
                texts.append(
                    model.lower()
                )  # named at the end, once its relations exist
            elif do == "assert":
                src = (
                    created
                    if step.get("source") == "$created"
                    else resolved["source"].export_ids()[0]
                )
                tgt = (
                    created
                    if step.get("target") == "$created"
                    else resolved["target"].export_ids()[0]
                )
                if src is None or tgt is None:
                    raise StoreError("composition references $created before create")
                doc_name, _ = self.verbs.assert_edge(
                    step["relation"],
                    src,
                    tgt,
                    (self.projection.get("naming") or {}).get("RelationDoc"),
                )
                trace.append(f"docs create --model RelationDoc {doc_name}")
                record["writes"].append(
                    {
                        "verb": "assert",
                        "address": join_id(self.write_store, "RelationDoc", doc_name),
                        "after": {
                            "source_id": src,
                            "target_id": tgt,
                            "relation_type": step["relation"],
                        },
                        "done": True,
                    }
                )
                texts.append(
                    f"{step['relation'].replace('_', ' ')} {self.display.name(tgt)}"
                )
            elif do == "change":
                tgt = (
                    created
                    if step.get("target") == "$created"
                    else resolved["target"].export_ids()[0]
                )
                if tgt is None:
                    raise StoreError("composition references $created before create")
                w = self.kernel.change(tgt, step["field"], step["value"])
                record["writes"].append(w.record())
        if created:
            model, addr = model_of(created), address_of(created)
            texts[0] = f"{model.lower()} {self.display.name(addr)}"
            self.dialogue.remember([addr], model)
            self.dialogue.last_written = created
            alt = [
                r
                for r in plan["steps"]
                for k, r in r.items()
                if k == "target" and r.candidates and r.note.startswith("any")
            ]
            note = (
                f" {self.display.names(alt[0].candidates)[0].capitalize()} would also work."
                if alt
                else ""
            )
            return (
                f"Created {texts[0]}"
                + (", " + ", ".join(texts[1:]) if len(texts) > 1 else "")
                + "."
                + note
            )
        return "Done: " + "; ".join(texts) + "."

    def _undo(self, trace: list[str], record: dict[str, Any]) -> str:
        if not self.kernel.allowed("undo"):
            raise StoreError("in this session I cannot undo")
        move = self.ledger.last_with_write(self.dialogue.speaker or None)
        if move is None:
            return "Nothing to undo."
        writes = self.kernel.undo(move)
        for w in writes:
            trace.append(
                f"undo {w.address}"
                + (f".{w.field_name}" if w.field_name else "")
                + f": {w.before!r} → {w.after!r}"
                + ("" if w.done else f" ({w.note})")
            )
            record["writes"].append(w.record())
        record["undoes"] = move["id"]
        skipped = [w.note for w in writes if not w.done]
        return (
            f"Undid {move['id']} ({len([w for w in writes if w.done])} write(s))."
            + (" Not touched: " + "; ".join(skipped) + "." if skipped else "")
        )

    def _why(self, part: Part, trace: list[str], record: dict[str, Any]) -> str:
        target = (
            self.dialogue.last_written
            or self.dialogue.last_singular
            and address_to_export_id(self.dialogue.last_singular)
        )
        if not target:
            return "Why what? Say something first."
        moves = self.ledger.about(target)
        bits = []
        if moves:
            m = moves[-1]
            w = [x for x in m["record"].get("writes", []) if x.get("address") == target]
            what = ", ".join(
                f"{x.get('field') or x['verb']}: {x.get('before')!r} → {x.get('after')!r}"
                for x in w
            )
            bits.append(
                f'Because of "{m["sentence"]}" ({m["speaker"] or "someone"}, {m["at"]}): {what}'
            )
            trace.append(f"ledger: {m['id']}")
            for line in m["record"].get("trace", []):
                if "transition" in line or "condition" in line or "legal" in line:
                    bits.append(line)
        why_edges = [
            e
            for e in self.verbs.edges_from(target).edges
            if e["metadata"].get("axis") in ("WHY", "PROVENANCE")
        ]
        if why_edges:
            bits.append(
                "grounded by "
                + ", ".join(
                    self.display.name(address_of(e["target"])) for e in why_edges
                )
            )
        record["edges"].extend(why_edges)
        return (" · ".join(bits) or f"No record explains {target}.") + "."

    def _refresh(self, trace: list[str]) -> None:
        report = self.world.refresh(stores=self.lex.stores)
        trace.append(f"refresh: {report['nodes']} nodes, {report['edges']} edges")
        self.hash = self.world.hash_mundo()


def _pronoun_item(part: Part):
    from pron.surface.tokens import Item

    last = part.items[0].text.split()[-1] if part.items else "it"
    return Item(
        "referent", last, number="singular", meta={"who": "singular", "implicit": True}
    )
