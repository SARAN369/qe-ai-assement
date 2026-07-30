"""Dependency-free keyword-overlap retriever. Deliberately not TF-IDF/
embeddings — the corpus here is a handful of docx sections and Gherkin
scenarios (dozens of chunks, not thousands), so a simple scored overlap is
easier to reason about and needs no extra ML dependency on top of the local
Ollama model.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .doc_loader import Chunk

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "for", "of",
    "to", "in", "on", "and", "or", "what", "which", "how", "do", "does",
    "generate", "code", "test", "cases", "case", "please", "me", "with",
    "that", "this", "it", "as", "from", "by",
}


def _tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower()) if w not in _STOPWORDS]


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: int


# Empirically, a chunk that's actually about the query (not just mentioning
# a query word in passing within an unrelated sentence) scores >= 4 here;
# passing mentions land at 1-3. Small local LLMs are unreliable at making
# this "is this actually relevant" judgment themselves even when explicitly
# instructed to, so relevance filtering happens here in code instead of
# being left to the model.
MIN_RELEVANCE_SCORE = 4


def retrieve(corpus: list[Chunk], query: str, top_k: int = 5, min_score: int = MIN_RELEVANCE_SCORE) -> list[ScoredChunk]:
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scored: list[ScoredChunk] = []
    for chunk in corpus:
        haystack = _tokenize(f"{chunk.title} {chunk.text}")
        if not haystack:
            continue
        overlap = sum(haystack.count(term) for term in set(query_terms))
        # Title matches count extra: a query mentioning "search" should rank
        # a scenario titled "...search..." above one that merely uses the
        # word once in its steps.
        title_terms = _tokenize(chunk.title)
        overlap += 2 * sum(1 for term in query_terms if term in title_terms)
        if overlap >= min_score:
            scored.append(ScoredChunk(chunk=chunk, score=overlap))

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:top_k]
