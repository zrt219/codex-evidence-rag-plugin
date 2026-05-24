from codex_evidence_rag.redaction import redact_text


def test_redacts_common_secrets():
    fake_key = "sk-" + "exampletokenvalue1234567890"
    text = f"OPENAI_API_KEY={fake_key} and password=example_password"
    redacted = redact_text(text)
    assert "sk-example" not in redacted
    assert "example_password" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_redacts_windows_private_paths():
    text = r"Proof lives at C:\Users\Example\Documents\private\file.md"
    assert "[REDACTED_PRIVATE_PATH]" in redact_text(text)
