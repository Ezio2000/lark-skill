"""Offline structural validation; this does not evaluate agent behavior or live APIs."""

from __future__ import annotations

import argparse
import ast
import io
import json
from pathlib import Path
import re
import sys
import tomllib
import tokenize
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

import yaml

IGNORED = {".git", ".venv", "__pycache__"}
RESOURCE_SUFFIXES = {".md", ".py", ".json", ".xml", ".html", ".jsx", ".js", ".yaml", ".toml", ".png", ".svg"}
LINK = re.compile(r"\]\((<?[^\s)]+>?)(?:\s+\"[^\"\n]*\")?\)")
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


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


def check_markdown_fences(text: str) -> list[str]:
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"\s*(?:>\s*)?(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        if fence is None:
            fence = (match[1], number)
        elif match[1][0] == fence[0][0] and len(match[1]) >= len(fence[0]) and not match[2].strip():
            fence = None
    return [f"line {fence[1]}: unclosed Markdown fence"] if fence else []


def markdown_anchors(text: str) -> set[str]:
    anchors = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', text, re.I))
    seen: dict[str, int] = {}
    fence = None
    for line in text.splitlines():
        marker = re.match(r"\s*(?:>\s*)?(`{3,}|~{3,})(.*)$", line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if fence or not heading:
            continue
        title = re.sub(r"<[^>]*>", "", heading[1]).lower()
        slug = "".join(c for c in title if c in "_-" or c.isspace() or unicodedata.category(c)[0] in "LMN")
        slug = re.sub(r"\s", "-", slug)
        duplicate = seen.get(slug, 0)
        seen[slug] = duplicate + 1
        anchors.add(f"{slug}-{duplicate}" if duplicate else slug)
    return anchors


def check_links(file: Path, root: Path) -> tuple[int, list[str]]:
    count, errors = 0, []
    for number, line in prose_lines(file.read_text(encoding="utf-8")):
        for match in LINK.finditer(line):
            target = match.group(1).strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            raw = unquote(parsed.path)
            if any(char in raw for char in "<>${}") or raw.startswith("@"):
                continue
            path = (file.parent / raw).resolve() if raw else file.resolve()
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
                if parsed.fragment and path.suffix == ".md":
                    fragment = unquote(parsed.fragment)
                    if fragment not in markdown_anchors(path.read_text(encoding="utf-8")):
                        errors.append(f"{file.relative_to(root)}:{number}: missing anchor {target}")
    return count, errors


def instruction_text(text: str) -> str:
    """Exclude literal identifiers, links, and anchors, not human-facing prose."""
    text = re.sub(r"(`+).*?\1", "", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"</?[A-Za-z][^>]*>", "", text)
    return text


def is_markdown_reference(file: Path, source: str) -> bool:
    # Two upstream compatibility entrypoints use .xml names for Markdown redirects.
    return file.suffix == ".md" or (
        file.suffix == ".xml"
        and bool(re.match(r"(?:<a\b[^>]*></a>\s*)?#{1,6}\s", source.lstrip()))
    )


def check_instruction_language(file: Path, root: Path) -> list[str]:
    errors = []
    source = file.read_text(encoding="utf-8")
    if is_markdown_reference(file, source):
        for number, line in prose_lines(source):
            if HAN.search(instruction_text(line)):
                errors.append(f"{file.relative_to(root)}:{number}: untranslated instruction prose")
    elif file.suffix == ".xml":
        try:
            tree = ET.fromstring(source)
        except ET.ParseError as exc:
            return [f"{file.relative_to(root)}: invalid XML: {exc}"]
        for element in tree.iter("{http://www.w3.org/2001/XMLSchema}documentation"):
            if HAN.search(instruction_text("".join(element.itertext()))):
                errors.append(f"{file.relative_to(root)}: untranslated XML documentation")
        for comment in re.findall(r"<!--([\s\S]*?)-->", source):
            if HAN.search(instruction_text(comment)):
                errors.append(f"{file.relative_to(root)}: untranslated XML comment")
    elif file.suffix == ".py":
        try:
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                if token.type == tokenize.COMMENT and HAN.search(instruction_text(token.string)):
                    errors.append(f"{file.relative_to(root)}:{token.start[0]}: untranslated Python comment")
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node)
                    if doc and HAN.search(instruction_text(doc)):
                        errors.append(f"{file.relative_to(root)}: untranslated Python docstring")
        except (SyntaxError, tokenize.TokenError):
            pass  # Syntax errors are reported by the bundle's Python AST check.
    elif file.suffix in {".js", ".jsx", ".html"}:
        pattern = r"<!--([\s\S]*?)-->" if file.suffix == ".html" else r"/\*([\s\S]*?)\*/|^\s*//(.*)$"
        for match in re.finditer(pattern, source, re.M):
            comment = "".join(part for part in match.groups() if part)
            if HAN.search(instruction_text(comment)):
                number = source.count("\n", 0, match.start()) + 1
                errors.append(f"{file.relative_to(root)}:{number}: untranslated source comment")
    return errors


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


def validate(root: Path, *, english: bool = False) -> dict:
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
        if english and (file == entry or "references" in file.relative_to(root).parts) and file.suffix in {".md", ".xml", ".py", ".js", ".jsx", ".html"}:
            errors.extend(check_instruction_language(file, root))
        if file.suffix == ".md" or (file.suffix == ".xml" and is_markdown_reference(file, file.read_text(encoding="utf-8"))):
            errors.extend(f"{file.relative_to(root)}: {error}" for error in check_markdown_fences(file.read_text(encoding="utf-8")))
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
    parser.add_argument("--english", action="store_true", help="Check LLM-facing prose while preserving literal example data")
    args = parser.parse_args()
    result = validate(args.root.resolve(), english=args.english)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
