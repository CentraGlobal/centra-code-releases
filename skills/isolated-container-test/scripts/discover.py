#!/usr/bin/env python3
"""Discover container and toolchain candidates without reading secret values."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
MAX_SCAN_DEPTH = 4
MAX_RESULTS_PER_KIND = 200

MANIFEST_NAMES = {
    "package.json": "node",
    "go.mod": "go",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "poetry.lock": "python",
    "uv.lock": "python",
    "Cargo.toml": "rust",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "java",
    "Gemfile": "ruby",
    "composer.json": "php",
}

LOCKFILE_NAMES = {
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "go.sum",
    "Cargo.lock",
    "poetry.lock",
    "uv.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "composer.lock",
}

TOOLCHAIN_FILES = {
    ".nvmrc",
    ".node-version",
    ".python-version",
    ".java-version",
    ".ruby-version",
    ".tool-versions",
    "rust-toolchain",
    "rust-toolchain.toml",
}


def run_git(path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def find_repo_root(start: Path) -> Path:
    discovered = run_git(start, "rev-parse", "--show-toplevel")
    return Path(discovered).resolve() if discovered else start.resolve()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def walk_files(root: Path) -> Iterable[Path]:
    root_depth = len(root.parts)
    yielded = 0
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_depth
        dirs[:] = sorted(
            directory
            for directory in dirs
            if directory not in EXCLUDED_DIRS and depth < MAX_SCAN_DEPTH
        )
        for filename in sorted(files):
            yield current_path / filename
            yielded += 1
            if yielded >= 20_000:
                return


def is_compose_file(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() not in {".yaml", ".yml"}:
        return False
    return bool(
        re.fullmatch(r"compose(?:\.[a-z0-9_-]+)?\.ya?ml", name)
        or re.fullmatch(r"docker-compose(?:\.[a-z0-9_-]+)?\.ya?ml", name)
    )


def compose_rank(path: Path, root: Path) -> tuple[int, int, str]:
    rel = relative(path, root).lower()
    if "/generated/" in f"/{rel}/" or rel.startswith("generated/"):
        group = 5
    elif "test" in path.name.lower():
        group = 0
    elif "dev" in path.name.lower() or rel.startswith(".devcontainer/"):
        group = 1
    elif path.parent == root:
        group = 2
    else:
        group = 3
    return (group, rel.count("/"), rel)


def read_small_text(path: Path, limit: int = 300) -> str | None:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")[:limit].strip()
    except OSError:
        return None
    return raw or None


def package_metadata(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"path": str(path), "parse_error": True}

    scripts = payload.get("scripts") if isinstance(payload.get("scripts"), dict) else {}
    engines = payload.get("engines") if isinstance(payload.get("engines"), dict) else {}
    return {
        "path": str(path),
        "package_manager": payload.get("packageManager"),
        "node_engine": engines.get("node"),
        "scripts": sorted(str(name) for name in scripts.keys()),
        "workspaces": bool(payload.get("workspaces")),
    }


def toolchain_metadata(root: Path, files: list[Path]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    by_name: dict[str, list[Path]] = {}
    for path in files:
        by_name.setdefault(path.name, []).append(path)

    for name in sorted(TOOLCHAIN_FILES):
        candidates = sorted(by_name.get(name, []), key=lambda item: relative(item, root))
        if candidates:
            value = read_small_text(candidates[0])
            result[name] = {"path": relative(candidates[0], root), "value": value}

    go_mod = sorted(by_name.get("go.mod", []), key=lambda item: relative(item, root))
    if go_mod:
        text = read_small_text(go_mod[0], 2_000) or ""
        go_version = re.search(r"^go\s+([^\s]+)", text, re.MULTILINE)
        toolchain = re.search(r"^toolchain\s+([^\s]+)", text, re.MULTILINE)
        result["go"] = {
            "path": relative(go_mod[0], root),
            "version": go_version.group(1) if go_version else None,
            "toolchain": toolchain.group(1) if toolchain else None,
        }

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project path to inspect")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    requested = Path(args.root).expanduser().resolve()
    if not requested.exists() or not requested.is_dir():
        parser.error(f"project root is not a directory: {requested}")

    project_root = requested
    repository_root = find_repo_root(requested)
    files = list(walk_files(project_root))

    compose_files = sorted(
        (path for path in files if is_compose_file(path)),
        key=lambda path: compose_rank(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    devcontainer_files = sorted(
        (
            path
            for path in files
            if path.name == "devcontainer.json" and ".devcontainer" in path.parts
        ),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    dockerfiles = sorted(
        (path for path in files if path.name == "Dockerfile" or path.name.startswith("Dockerfile.")),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    manifests = sorted(
        (path for path in files if path.name in MANIFEST_NAMES),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    lockfiles = sorted(
        (path for path in files if path.name in LOCKFILE_NAMES),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    instructions = sorted(
        (
            path
            for path in files
            if path.name in {"AGENTS.md", "CONTRIBUTING.md", "README.md", "README.rst"}
        ),
        key=lambda path: (
            relative(path, project_root).count("/"),
            relative(path, project_root),
        ),
    )[:MAX_RESULTS_PER_KIND]
    task_files = sorted(
        (
            path
            for path in files
            if path.name
            in {
                "Makefile",
                "Justfile",
                "Taskfile.yml",
                "Taskfile.yaml",
                "mise.toml",
            }
        ),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]
    env_files = sorted(
        (
            path
            for path in files
            if path.name == ".env" or path.name.startswith(".env.")
        ),
        key=lambda path: relative(path, project_root),
    )[:MAX_RESULTS_PER_KIND]

    if devcontainer_files and compose_files:
        strategy = "devcontainer_compose"
    elif compose_files:
        strategy = "compose"
    elif dockerfiles:
        strategy = "dockerfile"
    elif manifests:
        strategy = "manifest_runner"
    else:
        strategy = "undetermined"

    branch = run_git(repository_root, "branch", "--show-current")
    commit = run_git(repository_root, "rev-parse", "HEAD")
    status = run_git(repository_root, "status", "--porcelain")

    package_files = [path for path in manifests if path.name == "package.json"]
    payload = {
        "requested_root": str(requested),
        "project_root": str(project_root),
        "repository_root": str(repository_root),
        "git": {
            "branch": branch,
            "commit": commit,
            "dirty": bool(status),
        },
        "candidate_strategy": strategy,
        "instructions": [relative(path, project_root) for path in instructions],
        "container": {
            "devcontainer": [relative(path, project_root) for path in devcontainer_files],
            "compose": [relative(path, project_root) for path in compose_files],
            "dockerfiles": [relative(path, project_root) for path in dockerfiles],
        },
        "manifests": [
            {
                "path": relative(path, project_root),
                "ecosystem": MANIFEST_NAMES[path.name],
            }
            for path in manifests
        ],
        "lockfiles": [relative(path, project_root) for path in lockfiles],
        "task_files": [relative(path, project_root) for path in task_files],
        "package_metadata": [
            {**package_metadata(path), "path": relative(path, project_root)}
            for path in package_files
        ],
        "toolchains": toolchain_metadata(project_root, files),
        "potential_environment_files": [
            relative(path, project_root) for path in env_files
        ],
        "warnings": [
            "Environment files were detected; inspect variable names only and do not load them blindly."
        ]
        if env_files
        else [],
    }

    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
