from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

Confidence = Literal["STRONG", "MEDIUM", "WEAK", "UNVERIFIED"]


@dataclass
class EvidenceChunk:
    source_path: str
    source_alias: str
    source_type: str
    line_start: int
    line_end: int
    sha256: str
    snippet: str
    tokens: list[str] = field(default_factory=list)
    public_safe: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("tokens", None)
        return data


@dataclass
class SearchResult:
    chunk: EvidenceChunk
    score: float
    matched_terms: list[str]
    confidence: Confidence

    def to_dict(self) -> dict[str, Any]:
        data = self.chunk.to_dict()
        data.update(
            {
                "score": round(self.score, 4),
                "matched_terms": self.matched_terms,
                "confidence": self.confidence,
            }
        )
        return data


@dataclass
class EvidenceIndex:
    root: str
    generated_at: str
    chunks: list[EvidenceChunk]
    files_scanned: int
    files_indexed: int
    files_skipped: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceIndex":
        from .chunker import tokenize

        chunks: list[EvidenceChunk] = []
        for item in data.get("chunks", []):
            item = dict(item)
            item["tokens"] = tokenize(str(item.get("snippet", "")))
            chunks.append(EvidenceChunk(**item))
        return cls(
            root=str(data["root"]),
            generated_at=str(data["generated_at"]),
            chunks=chunks,
            files_scanned=int(data.get("files_scanned", 0)),
            files_indexed=int(data.get("files_indexed", 0)),
            files_skipped=int(data.get("files_skipped", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "generated_at": self.generated_at,
            "files_scanned": self.files_scanned,
            "files_indexed": self.files_indexed,
            "files_skipped": self.files_skipped,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }


def default_state_dir(root: Path) -> Path:
    return root / ".codex-evidence"
