from src.rag_engine import grade_claim, retrieve_context


def test_retrieve_context_finds_rag_document():
    docs = ["RAG retrieval uses context packs.", "Unrelated frontend copy."]
    assert retrieve_context("RAG context retrieval", docs) == ["RAG retrieval uses context packs."]


def test_grade_claim_strength():
    assert grade_claim(3) == "STRONG"
    assert grade_claim(0) == "UNVERIFIED"
