from pathlib import Path

from codex_evidence_rag.redaction import redact_text
from codex_evidence_rag.scanner import DEFAULT_IGNORES, TEXT_SUFFIXES, scan


ROOT = Path(__file__).resolve().parents[1]


def test_generated_state_and_local_installs_are_ignored():
    required = {".codex-evidence", ".venv", "__pycache__", "node_modules", ".git"}
    assert required <= DEFAULT_IGNORES


def test_scanner_indexes_text_only_suffixes():
    assert ".py" in TEXT_SUFFIXES
    assert ".md" in TEXT_SUFFIXES
    assert ".pdf" not in TEXT_SUFFIXES
    assert ".png" not in TEXT_SUFFIXES


def test_redaction_blocks_private_paths_and_composed_tokens():
    fake_secret = "sk-" + "auditexampletokenvalue123456789"
    text = rf"token={fake_secret} path=C:\Users\Example\Documents\private.txt"
    redacted = redact_text(text)
    assert fake_secret not in redacted
    assert r"C:\Users\Example" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "[REDACTED_PRIVATE_PATH]" in redacted


def test_fixture_scan_does_not_index_generated_evidence_state():
    fixture = ROOT / "examples" / "fixture_repo"
    index = scan(fixture)
    assert index.files_indexed >= 3
    assert all(".codex-evidence" not in chunk.source_path for chunk in index.chunks)
