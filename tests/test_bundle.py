from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_skill import check_links, check_scenarios
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
