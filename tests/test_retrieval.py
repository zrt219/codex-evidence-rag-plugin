from pathlib import Path

from codex_evidence_rag.claims import claim_grade, make_resume_bullet
from codex_evidence_rag.retrieval import search
from codex_evidence_rag.scanner import scan


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixture_repo"


def test_scan_and_search_fixture_repo():
    index = scan(FIXTURE)
    results = search(index, "RAG retrieval context eval", limit=3)
    assert index.files_indexed >= 3
    assert results
    assert results[0].matched_terms
    assert claim_grade(results) in {"STRONG", "MEDIUM", "WEAK"}


def test_resume_bullet_cites_source_path():
    index = scan(FIXTURE)
    results = search(index, "RAG retrieval context", limit=3)
    bullet = make_resume_bullet("RAG retrieval context system", results)
    assert "backed by `" in bullet
    assert "UNVERIFIED" not in bullet
