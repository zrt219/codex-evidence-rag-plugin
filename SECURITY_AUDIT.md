# Security Audit - Codex Evidence RAG Plugin

Audit date: 2026-05-24

## Scope

Audited the local Python CLI package, fixture repo, static docs page, generated-state rules, and public sample outputs.

This audit covers:

- Local file scanning behavior.
- Secret and private-path redaction.
- Generated evidence state.
- Public repo hygiene.
- Browser-rendered documentation.

This audit does not claim production penetration testing, third-party review, or supply-chain certification.

## Threat Model

| Risk | Control | Status |
|---|---|---|
| Accidentally committing generated indexes | `.codex-evidence/` is gitignored. | PASS |
| Accidentally exposing `.venv`, caches, or egg-info | `.gitignore` excludes local install/build state. | PASS |
| Leaking API keys or tokens from snippets | Redaction patterns cover common keys, tokens, JWT-like strings, DB URLs, and private keys. | PASS |
| Leaking raw Windows user paths | Redaction replaces `C:\Users\...\...` paths with `[REDACTED_PRIVATE_PATH]`. | PASS |
| Network exfiltration | CLI uses local filesystem only and has no runtime dependencies. | PASS |
| Unsupported resume claims | Claim grades include `UNVERIFIED`; resume bullets warn when proof is missing. | PASS |
| Binary/private artifact scanning | Scanner only indexes known text/code/config suffixes and skips large files. | PASS |

## Tests Added

- `tests/test_redaction.py`
- `tests/test_security_audit.py`
- `tests/test_retrieval.py`
- `tests/test_reports.py`

## Verification Commands

```powershell
python -m compileall src tests
python -m pytest
python -m codex_evidence_rag --help
python -m codex_evidence_rag scan --root examples\fixture_repo
python -m codex_evidence_rag --root examples\fixture_repo ask "Can I claim RAG eval experience?"
python -m codex_evidence_rag --root examples\fixture_repo packet
python -m codex_evidence_rag --root examples\fixture_repo context-pack "Add tests for the claim grader"
```

## Result

PASS with documented limitations.

The project is safe to publish as a local-only demo tool. It does not require API keys, does not call model providers, and does not ship private workspace evidence.

## Remaining Risks

- Redaction is pattern-based and cannot guarantee removal of every possible secret format.
- Users should review generated evidence packets before publishing.
- Future embedding/provider adapters must add provider-specific secret handling and network tests before release.
