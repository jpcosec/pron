"""Segmenting a sentence into tokens (spec 06 step 1).

A quoted run is one token, so is a word ending in ':' (the marker of a literal that
follows), a word, and each of the punctuation marks pron reads. What each token turns out
to be is the classifier's business; this is only where one token ends and the next begins.
"""

from __future__ import annotations

import re

TOKEN_RE = re.compile(r'"[^"]*"|[A-Za-zÀ-ÿ0-9_\'-]+:|[A-Za-zÀ-ÿ0-9_\'/-]+|[?,.:;!]')


def tokenize(sentence: str) -> list[str]:
    return TOKEN_RE.findall(sentence.strip())
