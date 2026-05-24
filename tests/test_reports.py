from pathlib import Path

from codex_evidence_rag.reports import context_pack, evidence_packet
from codex_evidence_rag.retrieval import search
from codex_evidence_rag.scanner import scan


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixture_repo"


def test_reports_include_claim_and_task():
    index = scan(FIXTURE)
    results = search(index, "RAG retrieval context", limit=2)
    assert "# Codex Evidence Packet" in evidence_packet(index, "RAG retrieval context", results)
    assert "# Codex Context Pack" in context_pack("Add tests for RAG retrieval", results)
