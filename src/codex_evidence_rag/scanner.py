from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .chunker import chunk_file
from .models import EvidenceIndex

DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".codex-evidence",
}

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".html",
    ".css",
    ".sol",
    ".sql",
}


@dataclass
class ScanStats:
    scanned: int = 0
    indexed: int = 0
    skipped: int = 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def should_skip(path: Path, root: Path, max_bytes: int) -> bool:
    parts = set(path.relative_to(root).parts)
    if parts & DEFAULT_IGNORES:
        return True
    if path.is_dir():
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return True
    try:
        return path.stat().st_size > max_bytes
    except OSError:
        return True


def iter_files(root: Path, max_bytes: int) -> tuple[list[Path], ScanStats]:
    stats = ScanStats()
    files: list[Path] = []
    for path in root.rglob("*"):
        if should_skip(path, root, max_bytes):
            if path.is_file():
                stats.skipped += 1
            continue
        if path.is_file():
            stats.scanned += 1
            files.append(path)
    return files, stats


def scan(root: Path, max_bytes: int = 300_000) -> EvidenceIndex:
    root = root.resolve()
    files, stats = iter_files(root, max_bytes)
    chunks = []
    for path in sorted(files):
        try:
            file_hash = sha256_file(path)
            file_chunks = chunk_file(path, root, file_hash)
        except OSError:
            stats.skipped += 1
            continue
        chunks.extend(file_chunks)
        stats.indexed += 1
    return EvidenceIndex(
        root=str(root),
        generated_at=datetime.now(timezone.utc).isoformat(),
        chunks=chunks,
        files_scanned=stats.scanned,
        files_indexed=stats.indexed,
        files_skipped=stats.skipped,
    )
