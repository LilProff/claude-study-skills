"""Tests for the helper scripts. Run from the repo root:

    python -m unittest discover -s tests -v

Standard library only. PDF tests are skipped when no PDF backend is installed.
"""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "depreciation"


def load(rel):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


build_course = load("skills/study-teach/scripts/build_course.py")
verify = load("skills/study-practice/scripts/verify_numbers.py")
cards = load("skills/study-cards/scripts/cards.py")
plan = load("skills/study-plan/scripts/plan.py")
ingest = load("skills/study-ingest/scripts/ingest.py")


class BuildCourse(unittest.TestCase):
    def build(self, files):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        for name, text in files.items():
            (d / name).write_text(text, encoding="utf-8")
        tpl = ROOT / "skills/study-teach/assets/template.html"
        return build_course.build(d, "T", tpl)

    def test_example_lesson_builds(self):
        page, errors, n, na = build_course.build(EX / "lessons", "Sample", ROOT / "skills/study-teach/assets/template.html")
        self.assertEqual(errors, [])
        self.assertEqual((n, na), (1, 1))
        for needle in ('class="quiz" data-correct="1"', "<details class=\"step\">", 'class="acro"', 'id="acronym-bank"',
                       'class="tryit"', 'class="tframe"', "<table><thead>"):
            self.assertIn(needle, page)
        self.assertNotIn("{{", page)

    def test_html_is_escaped(self):
        page, errors, *_ = self.build({"a.md": "---\nid: a\ntitle: A\n---\nHello <script>alert(1)</script> and [x](javascript:alert(1))\n"})
        self.assertEqual(errors, [])
        self.assertNotIn("<script>alert", page)
        self.assertNotIn('href="javascript', page)

    def test_validation_errors(self):
        _, errors, *_ = self.build({
            "a.md": "---\nid: same\n---\n:::kid\nnever closed\n",
            "b.md": "---\nid: same\n---\n:::quiz\nQ: ?\n- [ ] a\n- [ ] b\n:::\n[x](#missing)\n",
        })
        text = "\n".join(errors)
        self.assertIn("duplicate lesson id", text)
        self.assertIn("never closed", text)
        self.assertIn("exactly one", text)
        self.assertIn("#missing", text)

    def test_markdown_basics(self):
        h = build_course.render_md("# T\n\n- a\n- b\n\n1. x\n2. y\n\n**b** *i* `c<d>`\n\n```\nraw <x>\n```")
        self.assertIn("<h3>T</h3>", h)
        self.assertIn("<ul><li>a</li><li>b</li></ul>", h)
        self.assertIn("<ol><li>x</li><li>y</li></ol>", h)
        self.assertIn("<strong>b</strong> <em>i</em> <code>c&lt;d&gt;</code>", h)
        self.assertIn("raw &lt;x&gt;", h)


class VerifyNumbers(unittest.TestCase):
    def test_example_passes(self):
        for ex in verify.load(EX / "worked.json"):
            self.assertEqual(verify.check_example(ex, quiet=True), [])

    def test_wrong_claim_fails(self):
        ex = {"inputs": {"a": 10}, "steps": [{"name": "b", "formula": "a * 2", "result": 21}]}
        fails = verify.check_example(ex, quiet=True)
        self.assertEqual(len(fails), 1)
        self.assertIn("claimed 21", fails[0])

    def test_unsafe_formula_rejected(self):
        for bad in ("__import__('os').system('x')", "(1).__class__", "open('f')", "2 ** 1000"):
            ex = {"inputs": {}, "steps": [{"name": "x", "formula": bad, "result": 0}]}
            self.assertTrue(verify.check_example(ex, quiet=True), bad)

    def test_check_mismatch_fails(self):
        ex = {"inputs": {"a": 1}, "checks": [{"left": "a", "right": "2"}]}
        self.assertTrue(verify.check_example(ex, quiet=True))


class Cards(unittest.TestCase):
    def setUp(self):
        self.deck = cards.load_deck(EX / "cards.md")

    def test_parse(self):
        self.assertEqual(len(self.deck), 5)
        cloze = [c for c in self.deck if "[...]" in c["q"]][0]
        self.assertIn("carrying amount", cloze["a"])
        self.assertEqual(len({c["id"] for c in self.deck}), 5)

    def test_anki_export(self):
        out = cards.to_anki(self.deck).split("\n")
        self.assertEqual(out[0], "#separator:tab")
        self.assertEqual(out[3].count("\t"), 2)

    def test_leitner(self):
        t = date(2026, 1, 1)
        state = {}
        cid = self.deck[0]["id"]
        self.assertEqual(len(cards.due_cards(self.deck, state, t)), 5)
        cards.grade(state, cid, "good", t)
        self.assertEqual(state[cid]["due"], "2026-01-03")
        self.assertEqual(len(cards.due_cards(self.deck, state, t)), 4)
        cards.grade(state, cid, "again", t)
        self.assertEqual(state[cid]["box"], 0)
        self.assertEqual(state[cid]["due"], "2026-01-02")

    def test_acronym_cards(self):
        parsed = cards.parse_deck(cards.acronym_cards(EX / "lessons"))
        self.assertEqual(len(parsed), 2)
        self.assertIn("C = Cost", parsed[0]["a"])
        self.assertEqual(parsed[1]["a"], "CRUD")


class Plan(unittest.TestCase):
    def test_plan_shape(self):
        topics = [{"name": "A", "weight": 3, "mastery": 0.0, "need": 3.6},
                  {"name": "B", "weight": 1, "mastery": 0.9, "need": 0.3}]
        days, p, t = plan.build(date(2026, 12, 10), date(2026, 12, 1), 3.0, topics, {"sun"}, 2)
        self.assertEqual(len(days), 9)
        self.assertEqual(p[days[-1]]["kind"], "light")
        self.assertEqual([p[d]["kind"] for d in days[-3:-1]], ["mock", "mock"])
        hours = {x["name"]: x["hours"] for x in t}
        self.assertGreater(hours["A"], hours["B"] * 5)
        self.assertAlmostEqual(sum(hours.values()), 3.0 * 0.8 * sum(1 for d in days if p[d]["kind"] == "learn"), places=5)
        self.assertIn("## Day by day", plan.render(days, p, t, date(2026, 12, 10), 3.0))

    def test_exam_in_past_is_an_error(self):
        with self.assertRaises(SystemExit):
            plan.build(date(2026, 1, 1), date(2026, 1, 2), 2.0, [{"name": "A", "weight": 1, "mastery": 0, "need": 1.2}], set(), 0)


class Ingest(unittest.TestCase):
    def test_text_docx_and_duplicates(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "a.txt").write_text("12\nBody line\n\n\n\n500\nTotal 500\n7\n", encoding="utf-8")
        (d / "copy.txt").write_text("12\nBody line\n\n\n\n500\nTotal 500\n7\n", encoding="utf-8")
        W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        xml = ('<w:document xmlns:w="%s"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Title</w:t></w:r></w:p>'
               '<w:p><w:r><w:t>Plain text</w:t></w:r></w:p>'
               '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>X</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Y</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
               '</w:body></w:document>') % W
        with zipfile.ZipFile(d / "b.docx", "w") as z:
            z.writestr("word/document.xml", xml)
        out = d / "out"
        rc = ingest.main([str(d / "a.txt"), str(d / "copy.txt"), str(d / "b.docx"), "--out", str(out)])
        self.assertEqual(rc, 0)
        idx = json.loads((out / "index.json").read_text(encoding="utf-8"))
        self.assertTrue(any(e.get("skipped") for e in idx))
        a = (out / "a.md").read_text(encoding="utf-8")
        self.assertIn("<!-- page 1 -->", a)
        self.assertIn("500\nTotal 500", a)  # table-like number in the middle is kept
        self.assertNotIn("\n12\n", a)  # leading page number dropped
        b = (out / "b.md").read_text(encoding="utf-8")
        self.assertIn("# Title", b)
        self.assertIn("| X | Y |", b)

    def test_page_split(self):
        self.assertEqual(ingest.split_pages("a\fb\f"), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
