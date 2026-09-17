"""What the reader of pron's structured language raises (spec 06, 13): a text that is not
a well made s-expression.
"""

from __future__ import annotations


class SexpError(ValueError):
    pass
