#!/usr/bin/env python3
"""Generate a collision-resistant Docker Compose project name and ownership labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def slug(value: str, fallback: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or fallback


def compose_name(root: Path, purpose: str, suffix: str, max_length: int) -> tuple[str, dict[str, str]]:
    resolved = root.expanduser().resolve()
    repo_root_raw = git_value(resolved, "rev-parse", "--show-toplevel")
    repo_root = Path(repo_root_raw).resolve() if repo_root_raw else resolved
    repo = slug(repo_root.name, "project")
    branch = slug(git_value(resolved, "branch", "--show-current") or "detached", "detached")
    purpose_slug = slug(purpose, "test")
    suffix_slug = slug(suffix, "run")[:16]
    worktree_hash = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:8]
    tail = f"-{worktree_hash}-{suffix_slug}"
    prefix_budget = max_length - len("ct-") - len(tail)
    if prefix_budget < 6:
        raise ValueError("max length is too small for a safe project identity")
    human = f"{repo}-{branch}-{purpose_slug}"[:prefix_budget].rstrip("-")
    name = f"ct-{human}{tail}"
    commit = git_value(resolved, "rev-parse", "HEAD") or "unknown"
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    labels = {
        "io.codex.tmp-test": "true",
        "io.codex.tmp-test.project": name,
        "io.codex.tmp-test.repo": repo,
        "io.codex.tmp-test.worktree": worktree_hash,
        "io.codex.tmp-test.commit": commit,
        "io.codex.tmp-test.created-at": created_at,
    }
    return name, labels


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository or worktree path")
    parser.add_argument("--purpose", default="test", help="Short purpose slug")
    parser.add_argument("--suffix", help="Explicit suffix for reproducible output")
    parser.add_argument("--max-length", type=int, default=63)
    parser.add_argument("--json", action="store_true", help="Emit project metadata as JSON")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        parser.error(f"root is not a directory: {root}")
    if args.max_length < 24 or args.max_length > 120:
        parser.error("--max-length must be between 24 and 120")

    suffix = args.suffix or secrets.token_hex(3)
    try:
        name, labels = compose_name(root, args.purpose, suffix, args.max_length)
    except ValueError as error:
        parser.error(str(error))

    if args.json:
        print(json.dumps({"project": name, "labels": labels}, indent=2, sort_keys=True))
    else:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
