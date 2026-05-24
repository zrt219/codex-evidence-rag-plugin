from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .claims import claim_grade, make_resume_bullet
from .models import default_state_dir
from .reports import context_pack, evidence_packet, render_results, write_report
from .retrieval import search
from .scanner import scan
from .storage import load_index, save_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-evidence",
        description="Scan repositories, retrieve source-backed evidence, and grade resume claims.",
    )
    parser.add_argument("--root", default=".", help="Repository/workspace root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON for commands that support it.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_cmd = subparsers.add_parser("scan", help="Build a local evidence index.")
    scan_cmd.add_argument("--root", default=None, help="Root to scan. Overrides global --root.")
    scan_cmd.add_argument("--max-bytes", type=int, default=300_000, help="Max bytes per indexed file.")

    ask = subparsers.add_parser("ask", help="Ask whether local evidence supports a claim.")
    ask.add_argument("question")
    ask.add_argument("--limit", type=int, default=5)

    bullet = subparsers.add_parser("bullet", help="Generate a recruiter-safe bullet from a claim.")
    bullet.add_argument("claim")
    bullet.add_argument("--limit", type=int, default=5)

    packet = subparsers.add_parser("packet", help="Generate .codex-evidence/evidence_packet.md.")
    packet.add_argument("claim", nargs="?", default="Built a RAG evidence and claim-auditing system")
    packet.add_argument("--limit", type=int, default=5)

    pack = subparsers.add_parser("context-pack", help="Generate .codex-evidence/context_pack.md.")
    pack.add_argument("task")
    pack.add_argument("--limit", type=int, default=8)

    return parser


def resolve_root(args: argparse.Namespace) -> Path:
    root_value = getattr(args, "root", None) or "."
    return Path(root_value).resolve()


def command_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else resolve_root(args)
    index = scan(root, max_bytes=args.max_bytes)
    path = save_index(index, root)
    payload = {
        "index": str(path),
        "files_scanned": index.files_scanned,
        "files_indexed": index.files_indexed,
        "files_skipped": index.files_skipped,
        "chunks": len(index.chunks),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Indexed {payload['files_indexed']} files into {path}")
        print(f"Chunks: {payload['chunks']} | Skipped files: {payload['files_skipped']}")
    return 0


def command_ask(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    index = load_index(root)
    results = search(index, args.question, limit=args.limit)
    grade = claim_grade(results)
    if args.json:
        print(json.dumps({"grade": grade, "results": [item.to_dict() for item in results]}, indent=2))
    else:
        print(f"Claim grade: {grade}")
        print(render_results(results))
    return 0


def command_bullet(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    index = load_index(root)
    results = search(index, args.claim, limit=args.limit)
    print(make_resume_bullet(args.claim, results))
    return 0


def command_packet(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    index = load_index(root)
    results = search(index, args.claim, limit=args.limit)
    output = evidence_packet(index, args.claim, results)
    path = default_state_dir(root) / "evidence_packet.md"
    write_report(path, output)
    print(f"Wrote {path}")
    return 0


def command_context_pack(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    index = load_index(root)
    results = search(index, args.task, limit=args.limit)
    output = context_pack(args.task, results)
    path = default_state_dir(root) / "context_pack.md"
    write_report(path, output)
    print(f"Wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            return command_scan(args)
        if args.command == "ask":
            return command_ask(args)
        if args.command == "bullet":
            return command_bullet(args)
        if args.command == "packet":
            return command_packet(args)
        if args.command == "context-pack":
            return command_context_pack(args)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    parser.error(f"Unsupported command: {args.command}")
    return 2
