from __future__ import annotations

import math
from collections import Counter

from .chunker import tokenize
from .claims import confidence_for_score
from .models import EvidenceIndex, SearchResult


def search(index: EvidenceIndex, query: str, limit: int = 5) -> list[SearchResult]:
    query_terms = tokenize(query)
    if not query_terms:
        return []
    query_counts = Counter(query_terms)
    total_chunks = max(len(index.chunks), 1)
    document_frequency: Counter[str] = Counter()
    for chunk in index.chunks:
        document_frequency.update(set(chunk.tokens))

    results: list[SearchResult] = []
    for chunk in index.chunks:
        token_counts = Counter(chunk.tokens)
        matched = sorted(set(query_terms) & set(token_counts))
        if not matched:
            continue
        score = 0.0
        for term in matched:
            tf = token_counts[term]
            idf = math.log((1 + total_chunks) / (1 + document_frequency[term])) + 1
            score += query_counts[term] * tf * idf
        score = score / max(len(chunk.tokens), 1) * 100
        results.append(
            SearchResult(
                chunk=chunk,
                score=score,
                matched_terms=matched,
                confidence=confidence_for_score(score, len(matched), chunk.source_type),
            )
        )
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
