from __future__ import annotations

import json
from pathlib import Path

from .models import EvidenceIndex, default_state_dir


def index_path(root: Path) -> Path:
    return default_state_dir(root) / "index.json"


def save_index(index: EvidenceIndex, root: Path) -> Path:
    path = index_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index.to_dict(), indent=2), encoding="utf-8")
    return path


def load_index(root: Path) -> EvidenceIndex:
    path = index_path(root)
    if not path.exists():
        raise FileNotFoundError(f"Missing evidence index. Run: codex-evidence scan --root {root}")
    return EvidenceIndex.from_dict(json.loads(path.read_text(encoding="utf-8")))
