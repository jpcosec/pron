"""pron: a SHRDLU over an sldb world.

Nouns are sldb addresses, transitive verbs are kgdb relation models stored as sldb
documents, action verbs are sldb writes. pron never resolves, filters, declares verbs
or writes to kgdb; it turns sentences into addresses, edges and writes, keeps the
dialogue when a sentence is not enough, and records every move. See source/spec/.
"""

__version__ = "1.0.0.dev1"
