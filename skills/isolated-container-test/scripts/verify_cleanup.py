#!/usr/bin/env python3
"""Verify that an exact temporary Compose project has no labeled Docker resources."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Iterable


SAFE_PROJECT = re.compile(r"^ct-[a-z0-9][a-z0-9_-]{2,116}[a-z0-9]$")


def docker_lines(docker_bin: str, args: list[str]) -> list[str]:
    result = subprocess.run(
        [docker_bin, *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def unique(lines: Iterable[str]) -> list[str]:
    return sorted(set(lines))


def resources_for_project(docker_bin: str, project: str) -> dict[str, list[str]]:
    compose_label = f"com.docker.compose.project={project}"
    owner_label = f"io.codex.tmp-test.project={project}"
    commands = {
        "containers": (
            ["ps", "-a", "--filter", "label=__LABEL__", "--format", "{{.ID}}\t{{.Names}}"],
        ),
        "networks": (
            ["network", "ls", "--filter", "label=__LABEL__", "--format", "{{.ID}}\t{{.Name}}"],
        ),
        "volumes": (
            ["volume", "ls", "--filter", "label=__LABEL__", "--format", "{{.Name}}"],
        ),
        "images": (
            ["image", "ls", "--filter", "label=__LABEL__", "--format", "{{.ID}}\t{{.Repository}}:{{.Tag}}"],
        ),
    }

    found: dict[str, list[str]] = {}
    for kind, command_group in commands.items():
        lines: list[str] = []
        for template in command_group:
            for label in (compose_label, owner_label):
                lines.extend(
                    docker_lines(
                        docker_bin,
                        [part.replace("__LABEL__", label) for part in template],
                    )
                )
        found[kind] = unique(lines)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Exact generated Compose project name")
    parser.add_argument("--docker-bin", default="docker")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if not SAFE_PROJECT.fullmatch(args.project):
        parser.error("refusing an unsafe project name; expected the generated ct-... form")

    try:
        resources = resources_for_project(args.docker_bin, args.project)
    except FileNotFoundError:
        print(json.dumps({"clean": False, "error": f"Docker binary not found: {args.docker_bin}"}))
        return 2
    except subprocess.TimeoutExpired:
        print(json.dumps({"clean": False, "error": "Docker resource inspection timed out"}))
        return 2
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip() or "Docker inspection failed"
        print(json.dumps({"clean": False, "error": message}))
        return 2

    clean = all(not values for values in resources.values())
    payload = {
        "project": args.project,
        "clean": clean,
        "counts": {kind: len(values) for kind, values in resources.items()},
        "resources": resources,
    }
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
