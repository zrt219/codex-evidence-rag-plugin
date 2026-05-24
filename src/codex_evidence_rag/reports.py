from __future__ import annotations

from pathlib import Path

from .claims import claim_grade, make_resume_bullet
from .models import EvidenceIndex, SearchResult


def render_results(results: list[SearchResult]) -> str:
    if not results:
        return "- No matching evidence found.\n"
    lines: list[str] = []
    for idx, result in enumerate(results, start=1):
        chunk = result.chunk
        lines.extend(
            [
                f"### {idx}. `{chunk.source_path}:{chunk.line_start}`",
                f"- Confidence: `{result.confidence}`",
                f"- Source type: `{chunk.source_type}`",
                f"- Matched terms: {', '.join(result.matched_terms)}",
                f"- Public safe: `{chunk.public_safe}`",
                "",
                "```txt",
                chunk.snippet[:1600],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def evidence_packet(index: EvidenceIndex, claim: str, results: list[SearchResult]) -> str:
    grade = claim_grade(results)
    bullet = make_resume_bullet(claim, results)
    return "\n".join(
        [
            "# Codex Evidence Packet",
            "",
            f"- Claim: {claim}",
            f"- Grade: `{grade}`",
            f"- Files indexed: {index.files_indexed}",
            f"- Chunks indexed: {len(index.chunks)}",
            "",
            "## Resume-Safe Bullet",
            "",
            bullet,
            "",
            "## Retrieved Evidence",
            "",
            render_results(results),
        ]
    )


def context_pack(task: str, results: list[SearchResult]) -> str:
    return "\n".join(
        [
            "# Codex Context Pack",
            "",
            f"Task: {task}",
            "",
            "## Read These First",
            "",
            render_results(results),
            "## Operating Note",
            "",
            "Use the cited files as the local source of truth. Do not infer unsupported claims.",
            "",
        ]
    )


def write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
