"""Compare two local upstream checkouts without altering either or this skill."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ALIASES = {"lark-vc", "lark-vc-agent", "lark-note", "lark-minutes"}


def inventory(checkout: Path) -> dict[str, str]:
    skills = checkout / "skills"
    if not skills.is_dir():
        raise ValueError(f"Missing upstream skills directory: {skills}")
    result = {}
    for module in sorted(skills.glob("lark-*")):
        if not module.is_dir():
            continue
        for file in sorted(module.rglob("*")):
            if file.is_file():
                result[file.relative_to(skills).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    if not result:
        raise ValueError(f"No upstream lark-* files found in {skills}")
    return result


def destination(source: str) -> str:
    module, path = source.split("/", 1)
    domain = "meeting" if module in ALIASES else module.removeprefix("lark-")
    return f"references/{domain}/{'index.md' if path == 'SKILL.md' else path}"


def compare(baseline: Path, candidate: Path) -> list[dict]:
    before, after = inventory(baseline), inventory(candidate)
    changes = []
    for source in sorted(before.keys() | after.keys()):
        if before.get(source) == after.get(source):
            continue
        status = "added" if source not in before else "removed" if source not in after else "modified"
        changes.append({"status": status, "source": source, "local_path": destination(source), "alias_only": source.split("/", 1)[0] in ALIASES})
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        changes = compare(args.baseline.resolve(), args.candidate.resolve())
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "changes": changes, "changed_files": len(changes)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
