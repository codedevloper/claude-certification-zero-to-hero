"""A small Okapi BM25 implementation with no dependencies.

BM25 is a lexical ranking function: it scores a chunk higher when it contains the query's terms,
especially rare terms, and normalises for chunk length. It needs no embedding model, it is easy to
explain to auditors, and it handles exact identifiers (policy names, form titles, product codes)
better than many embedding models. Its weakness is synonyms: "laptop" will not match "notebook".
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

STOPWORDS = frozenset(
    """a an and are as at be by can do does for from has have how i if in is it its many may me my of on or
    our should so that the their them then there these they this to was we what when where which who why
    will with you your much long often quickly""".split()
)
_TOKEN = re.compile(r"[a-z0-9]+")


def _stem(token: str) -> str:
    """Very light stemming so 'laptops' matches 'laptop' and 'policies' matches 'policy'."""
    if len(token) <= 3:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("sses", "xes", "zes", "ches", "shes")):
        return token[:-2]
    if token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]


@dataclass
class BM25Index:
    k1: float = 1.5
    b: float = 0.75

    def __post_init__(self) -> None:
        self.doc_tokens: list[list[str]] = []
        self.term_freqs: list[Counter[str]] = []
        self.doc_freq: Counter[str] = Counter()
        self.avg_len = 0.0

    def fit(self, documents: list[str]) -> "BM25Index":
        self.doc_tokens = [tokenize(d) for d in documents]
        self.term_freqs = [Counter(toks) for toks in self.doc_tokens]
        self.doc_freq = Counter()
        for tf in self.term_freqs:
            self.doc_freq.update(tf.keys())
        self.avg_len = sum(len(t) for t in self.doc_tokens) / max(1, len(self.doc_tokens))
        return self

    def idf(self, term: str) -> float:
        n = len(self.doc_tokens)
        df = self.doc_freq.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def score(self, query: str, index: int) -> float:
        tf = self.term_freqs[index]
        length = len(self.doc_tokens[index])
        total = 0.0
        for term in set(tokenize(query)):
            f = tf.get(term, 0)
            if f:
                denom = f + self.k1 * (1 - self.b + self.b * length / (self.avg_len or 1))
                total += self.idf(term) * f * (self.k1 + 1) / denom
        return total

    def search(self, query: str, k: int = 5) -> list[tuple[int, float]]:
        scored = [(i, self.score(query, i)) for i in range(len(self.doc_tokens))]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda s: (-s[1], s[0]))
        return scored[:k]
