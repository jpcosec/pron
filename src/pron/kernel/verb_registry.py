"""The five plain action verbs by name (spec 11 §7). `create` and `assert` stay outside this
registry: their shapes (no export_id yet; a RelationDoc write) don't fit the same signature,
and `Kernel.undo` already inverts them together.
"""

from __future__ import annotations

from pron.kernel.add_verb import AddVerb
from pron.kernel.change_verb import ChangeVerb
from pron.kernel.clean_verb import CleanVerb
from pron.kernel.forget_verb import ForgetVerb
from pron.kernel.remove_verb import RemoveVerb
from pron.kernel.verb import Verb

VERBS: dict[str, Verb] = {
    v.name: v
    for v in (ChangeVerb(), AddVerb(), RemoveVerb(), CleanVerb(), ForgetVerb())
}
