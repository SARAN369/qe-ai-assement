"""Dependency-free keyword-overlap matcher, generalized from
ai-testing-assistant's retriever. Used by Phase 1 (RTM) and Phase 3 (manual
test case traceability) to cross-reference requirement text against the
project's *actual* Gherkin scenarios, instead of asking the LLM to invent
a mapping (which, per Phase 7's README, small local models are unreliable
at judging).
"""
from __future__ import annotations

import re

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "for", "of",
    "to", "in", "on", "and", "or", "with", "that", "this", "it", "as",
    "from", "by", "should", "verify", "user", "all",
}


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower()) if w not in _STOPWORDS]


def overlap_score(query_text: str, candidate_text: str) -> int:
    query_terms = set(tokenize(query_text))
    haystack = tokenize(candidate_text)
    return sum(haystack.count(term) for term in query_terms)


def best_matches(query_text: str, candidates: list, text_fn, min_score: int = 2, top_k: int = 5):
    """candidates: list of arbitrary objects; text_fn(candidate) -> str to score against."""
    scored = [(overlap_score(query_text, text_fn(c)), c) for c in candidates]
    scored = [(s, c) for s, c in scored if s >= min_score]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]
