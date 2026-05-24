from __future__ import annotations

import re
from pathlib import Path

from .models import EvidenceChunk
from .redaction import is_public_safe, public_path, redact_text

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+-]{1,}")
STOPWORDS = {
    "and",
    "are",
    "can",
    "for",
    "from",
    "how",
    "the",
    "this",
    "that",
    "with",
    "you",
}


def tokenize(text: str) -> list[str]:
    return [token for match in TOKEN_RE.finditer(text) if (token := match.group(0).lower()) not in STOPWORDS]


def source_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".rst", ".txt"}:
        return "doc"
    if suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".sol"}:
        return "code"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml"}:
        return "config"
    if "test" in path.name.lower() or path.parent.name.lower() == "tests":
        return "test"
    return "text"


def chunk_file(path: Path, root: Path, sha256: str, max_lines: int = 36) -> list[EvidenceChunk]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    chunks: list[EvidenceChunk] = []
    for start in range(0, len(lines), max_lines):
        block = lines[start : start + max_lines]
        snippet = redact_text("\n".join(block)).strip()
        if not snippet:
            continue
        chunks.append(
            EvidenceChunk(
                source_path=public_path(path, root),
                source_alias="WORKSPACE",
                source_type=source_type_for(path),
                line_start=start + 1,
                line_end=start + len(block),
                sha256=sha256,
                snippet=snippet,
                tokens=tokenize(snippet),
                public_safe=is_public_safe("\n".join(block)),
            )
        )
    return chunks
