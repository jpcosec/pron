"""The five plain action verbs by name (spec 11 §7). `create` and `assert` stay outside this
registry: their shapes (no export_id yet; a RelationDoc write) don't fit the same signature,
and `Kernel.undo` already inverts them together.
"""

from __future__ import annotations

from pron.kernel.actions.add_verb import AddVerb
from pron.kernel.actions.change_verb import ChangeVerb
from pron.kernel.actions.clean_verb import CleanVerb
from pron.kernel.actions.forget_verb import ForgetVerb
from pron.kernel.actions.remove_verb import RemoveVerb
from pron.kernel.actions.verb import Verb

VERBS: dict[str, Verb] = {
    v.name: v
    for v in (ChangeVerb(), AddVerb(), RemoveVerb(), CleanVerb(), ForgetVerb())
}
