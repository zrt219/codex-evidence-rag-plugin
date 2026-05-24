from __future__ import annotations

from .models import Confidence, SearchResult

STRONG_SOURCE_TYPES = {"code", "test", "config"}


def confidence_for_score(score: float, matched_terms: int, source_type: str) -> Confidence:
    if matched_terms >= 3 and score >= 2.2 and source_type in STRONG_SOURCE_TYPES:
        return "STRONG"
    if matched_terms >= 2 and score >= 1.1:
        return "MEDIUM"
    if matched_terms >= 1:
        return "WEAK"
    return "UNVERIFIED"


def claim_grade(results: list[SearchResult]) -> Confidence:
    ranks = {"UNVERIFIED": 0, "WEAK": 1, "MEDIUM": 2, "STRONG": 3}
    if not results:
        return "UNVERIFIED"
    best = max(results, key=lambda item: ranks[item.confidence]).confidence
    return best


def make_resume_bullet(claim: str, results: list[SearchResult]) -> str:
    grade = claim_grade(results)
    if grade == "UNVERIFIED":
        return f"UNVERIFIED - do not use on a resume yet: {claim}"
    evidence = results[0].chunk.source_path if results else "no cited source"
    prefix = "Built" if not claim.lower().startswith(("built", "implemented", "improved")) else ""
    normalized = claim.strip().rstrip(".")
    if prefix:
        normalized = f"{prefix} {normalized[0].lower()}{normalized[1:]}"
    qualifier = "" if grade == "STRONG" else " with supporting local evidence"
    return f"{normalized}{qualifier}, backed by `{evidence}`."
