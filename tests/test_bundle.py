from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_skill import check_instruction_language, check_links, check_markdown_fences, check_scenarios
from upstream_diff import compare, inventory


class LinkValidationTests(unittest.TestCase):
    def test_real_broken_link_is_reported_but_examples_and_urls_are_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "index.md"
            file.write_text('[missing](missing.md)\n`[example](sample.md)`\n```md\n[example](sample2.md)\n```\n[web](https://example.org/a.md)\n', encoding="utf-8")
            count, errors = check_links(file, root)
            self.assertEqual(count, 0)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing.md", errors[0])

    def test_relative_encoded_path_survives_relocation(self):
        with tempfile.TemporaryDirectory(prefix="lark bundle ") as tmp:
            root = Path(tmp)
            (root / "a b.md").write_text("# target", encoding="utf-8")
            sub = root / "nested"
            sub.mkdir()
            file = sub / "index.md"
            file.write_text('[`target`](../a%20b.md#target)', encoding="utf-8")
            self.assertEqual(check_links(file, root), (1, []))

    def test_external_files_are_not_treated_as_bundled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "index.md"
            file.write_text('[outside](../outside.md)', encoding="utf-8")
            self.assertIn("external local path", check_links(file, root)[1][0])

    def test_translated_anchors_duplicates_and_missing_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "reference.md"
            file.write_text('<a id="旧标题"></a>\n# New title\n## `--flag` usage\n## `--flag` usage\n[Old](#%E6%97%A7%E6%A0%87%E9%A2%98)\n[Duplicate](#--flag-usage-1)\n[Missing](#absent)\n', encoding="utf-8")
            count, errors = check_links(file, root)
            self.assertEqual(count, 3)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing anchor #absent", errors[0])


class InstructionLanguageTests(unittest.TestCase):
    def test_unclosed_fence_cannot_hide_instruction_prose(self):
        self.assertEqual(check_markdown_fences('````md\n```python\nexample\n```\n````\n'), [])
        self.assertEqual(check_markdown_fences('> ~~~bash\n> example\n> ~~~\n'), [])
        self.assertIn('line 1', check_markdown_fences('```bash\nexample\n')[0])

    def test_prose_is_checked_without_translating_literal_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "reference.md"
            file.write_text('Use `状态` as the field name.\n<a id="旧标题"></a>\n[Details](#旧标题)\n```json\n{"name":"张三"}\n```\n', encoding="utf-8")
            self.assertEqual(check_instruction_language(file, root), [])
            file.write_text('# 操作说明\n', encoding="utf-8")
            self.assertIn("untranslated instruction", check_instruction_language(file, root)[0])

    def test_xml_documentation_is_distinct_from_schema_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "schema.xml"
            file.write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:documentation>Use the exact font identifier.</xs:documentation><xs:enumeration value="思源黑体"/></xs:schema>', encoding="utf-8")
            self.assertEqual(check_instruction_language(file, root), [])
            file.write_text('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:documentation>字体说明</xs:documentation></xs:schema>', encoding="utf-8")
            self.assertIn("untranslated XML documentation", check_instruction_language(file, root)[0])
            file.write_text('<broken>', encoding="utf-8")
            self.assertIn("invalid XML", check_instruction_language(file, root)[0])

    def test_legacy_xml_named_markdown_redirect_is_checked_as_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "compat.xml"
            file.write_text('<a id="旧入口"></a>\n# Compatibility entrypoint\nSee [schema](xml/schema.xml).\n', encoding="utf-8")
            self.assertEqual(check_instruction_language(file, root), [])
            file.write_text('# 兼容入口\n', encoding="utf-8")
            self.assertIn("untranslated instruction prose", check_instruction_language(file, root)[0])

    def test_source_comments_are_distinct_from_runtime_ui_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "helper.py"
            file.write_text('"""English usage."""\nlabel = "中文界面"\n# English comment\n', encoding="utf-8")
            self.assertEqual(check_instruction_language(file, root), [])
            file.write_text('"""执行说明。"""\n# 操作说明\n', encoding="utf-8")
            self.assertEqual(len(check_instruction_language(file, root)), 2)
            file = root / "template.html"
            file.write_text('<p>中文用户内容</p><!-- English instruction. -->', encoding="utf-8")
            self.assertEqual(check_instruction_language(file, root), [])
            file.write_text('<p>中文用户内容</p><!-- 执行说明 -->', encoding="utf-8")
            self.assertEqual(len(check_instruction_language(file, root)), 1)


class ScenarioValidationTests(unittest.TestCase):
    def test_malformed_cases_return_errors_instead_of_crashing(self):
        for cases in (None, {}, [], [None], [{"id": []}], [{"id": "a", "request": 42}],
                      [{"id": "a", "request": "Read", "expected": {"modules": [None]}}]):
            with self.subTest(cases=cases):
                self.assertTrue(check_scenarios(cases, ["doc"]))

    def test_unique_cases_can_include_a_nonactivation_case(self):
        case = {"id": "local", "request": "Local HTML", "expected": {"modules": [], "behavior": "Do not activate Lark"}}
        self.assertEqual(check_scenarios([case], ["doc"]), [])
        self.assertTrue(check_scenarios([case, case], ["doc"]))
        case["expected"]["modules"] = ["missing"]
        self.assertTrue(check_scenarios([case], ["doc"]))


class UpstreamDiffTests(unittest.TestCase):
    def test_reports_text_binary_deletions_and_aliases_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old, new = root / "old", root / "new"
            for tree in (old, new):
                (tree / "skills/lark-doc").mkdir(parents=True)
                (tree / "skills/lark-doc/SKILL.md").write_text("same", encoding="utf-8")
            (old / "skills/lark-doc/removed.md").write_text("gone", encoding="utf-8")
            (new / "skills/lark-doc/new.md").write_text("new", encoding="utf-8")
            (old / "skills/lark-doc/asset.png").write_bytes(b"before")
            (new / "skills/lark-doc/asset.png").write_bytes(b"after")
            (new / "skills/lark-note").mkdir()
            (new / "skills/lark-note/SKILL.md").write_text("alias", encoding="utf-8")
            snapshots = (inventory(old), inventory(new))
            result = {item["source"]: item for item in compare(old, new)}
            self.assertEqual(result["lark-doc/asset.png"]["status"], "modified")
            self.assertEqual(result["lark-doc/removed.md"]["status"], "removed")
            self.assertEqual(result["lark-doc/new.md"]["local_path"], "references/doc/new.md")
            self.assertTrue(result["lark-note/SKILL.md"]["alias_only"])
            self.assertEqual(result["lark-note/SKILL.md"]["local_path"], "references/meeting/index.md")
            self.assertEqual(len(result), 4)
            self.assertEqual(snapshots, (inventory(old), inventory(new)))

    def test_missing_or_empty_checkout_does_not_silently_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                inventory(root)
            (root / "skills").mkdir()
            with self.assertRaises(ValueError):
                inventory(root)


if __name__ == "__main__":
    unittest.main()
