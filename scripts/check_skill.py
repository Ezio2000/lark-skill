"""Offline structural validation; this does not evaluate agent behavior or live APIs."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote, urlsplit

import yaml

IGNORED = {".git", ".venv", "__pycache__"}
RESOURCE_SUFFIXES = {".md", ".py", ".json", ".xml", ".html", ".jsx", ".js", ".yaml", ".toml", ".png", ".svg"}
LINK = re.compile(r"\]\((<?[^\s)]+>?)(?:\s+\"[^\"\n]*\")?\)")


def bundle_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and not set(p.relative_to(root).parts) & IGNORED)


def prose_lines(text: str):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"\s*(?:>\s*)?(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                fence = None
            continue
        if fence is None:
            # Examples of Markdown syntax inside inline code are not file references.
            yield number, re.sub(r"(`+).*?\1", "", line)


def check_links(file: Path, root: Path) -> tuple[int, list[str]]:
    count, errors = 0, []
    for number, line in prose_lines(file.read_text(encoding="utf-8")):
        for match in LINK.finditer(line):
            target = match.group(1).strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            raw = unquote(parsed.path)
            if any(char in raw for char in "<>${}") or raw.startswith("@"):
                continue
            path = (file.parent / raw).resolve()
            if path.suffix not in RESOURCE_SUFFIXES and raw not in {"LICENSE", "README.md", "SOURCES.md"}:
                continue
            try:
                path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{file.relative_to(root)}:{number}: external local path {raw}")
                continue
            if not path.is_file():
                errors.append(f"{file.relative_to(root)}:{number}: missing {raw}")
            else:
                count += 1
    return count, errors


def check_scenarios(scenarios: object, modules: list[str]) -> list[str]:
    errors = []
    if not isinstance(scenarios, list) or not scenarios:
        return ["Behavior scenarios must be a nonempty array"]
    identifiers = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            errors.append("Behavior scenario must be an object")
            continue
        identifier = scenario.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append("Behavior scenario needs a nonempty string ID")
            continue
        if identifier in identifiers:
            errors.append(f"Duplicate behavior scenario: {identifier}")
        identifiers.add(identifier)
        if not isinstance(scenario.get("request"), str) or not scenario["request"].strip():
            errors.append(f"Missing request in scenario {identifier}")
        expected = scenario.get("expected")
        if not isinstance(expected, dict) or not isinstance(expected.get("modules"), list):
            errors.append(f"Invalid expectations in scenario {identifier}")
            continue
        if not isinstance(expected.get("behavior"), str) or not expected["behavior"].strip():
            errors.append(f"Missing expected behavior in scenario {identifier}")
        for module in expected["modules"]:
            if not isinstance(module, str) or module not in modules:
                errors.append(f"Unknown module in scenario {identifier}: {module}")
    return errors


def validate(root: Path) -> dict:
    errors = []
    files = bundle_files(root)
    entry = root / "SKILL.md"
    if [p.relative_to(root).as_posix() for p in files if p.name == "SKILL.md"] != ["SKILL.md"]:
        errors.append("Expected exactly one SKILL.md at the bundle root")
    if not entry.is_file():
        return {"ok": False, "errors": errors}
    text = entry.read_text(encoding="utf-8")
    header = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    try:
        meta = yaml.safe_load(header.group(1)) if header else None
        if not isinstance(meta, dict) or meta.get("name") != "lark" or not isinstance(meta.get("description"), str) or not meta["description"].strip():
            errors.append("Invalid skill frontmatter")
    except yaml.YAMLError as exc:
        errors.append(f"Invalid YAML: {exc}")
    modules = sorted(p.parent.name for p in (root / "references").glob("*/index.md"))
    for module in modules:
        if f"(references/{module}/index.md)" not in text:
            errors.append(f"Module not routed from SKILL.md: {module}")
    links = 0
    scripts = 0
    for file in files:
        if file.suffix == ".md":
            found, missing = check_links(file, root)
            links += found
            errors.extend(missing)
        elif file.suffix == ".py":
            scripts += 1
            try:
                ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
            except SyntaxError as exc:
                errors.append(f"{file.relative_to(root)}: {exc}")
    for required in ("LICENSE", "SOURCES.md", "README.md", "uv.lock", "pyproject.toml", "tests/scenarios.json"):
        if not (root / required).is_file():
            errors.append(f"Missing distribution file: {required}")
    for resource in ("references/slides/references/xml/slides_xml_schema_definition.xml", "references/slides/references/iconpark-index.json"):
        if not (root / resource).is_file():
            errors.append(f"Missing script resource: {resource}")
    try:
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        if not any(d.startswith("pandas") for d in project.get("optional-dependencies", {}).get("dataframe", [])):
            errors.append("Dataframe helper needs a declared pandas extra")
        scenarios = json.loads((root / "tests/scenarios.json").read_text(encoding="utf-8"))
        errors.extend(check_scenarios(scenarios, modules))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid distribution metadata: {exc}")
    return {"ok": not errors, "modules": len(modules), "local_links": links, "python_files": scripts, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    result = validate(parser.parse_args().root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
