# claude-study-skills

Study faster with Claude Code. Bring a pile of notes, slides, textbooks and past questions. Get step-by-step lessons in plain language, flashcards, acronyms for every list you must memorise, practice with numbers checked by code, and a day-by-day plan that works backwards from your exam date.

Built for people with **a lot of material to cover and a lot of work to practise**: professional exams, certifications, university courses, bootcamps.

> **Status: v0.1.** The five scripts are unit-tested (16 tests) and the sample course was checked on a 375 px phone viewport. The skill prompts come from a real exam-prep project but have not yet been tested across many subjects. Plugin-marketplace install is untested; the manual install below is the safe path. Issues and PRs welcome.

## What you get

| Skill | You say | You get |
| --- | --- | --- |
| `study-coach` | "Help me prepare for my exam" | Intake questions, a `study/` workspace, a `STATE.md` so work resumes next session |
| `study-ingest` | "Here are my PDFs" | Clean, page-marked Markdown of every file (PDF, Word, PowerPoint, text, images) |
| `study-map` | "What should I focus on?" | `map.md`: what is tested, how often, where marks are won and lost, a ranked learn-first list |
| `study-teach` | "Teach me X like I'm 10" | Analogy, theory frame, acronyms, hard worked examples one step at a time, try-it, quizzes; builds an offline phone-friendly course |
| `study-cards` | "Make flashcards and mnemonics" | Cards, cloze cards, acronym cards, Anki export, spaced-review scheduling |
| `study-practice` | "Set me a mock", "mark my answer" | Variants, mocks with marking guides, marking, error log, every number verified by a script |
| `study-plan` | "My exam is on 10 Dec, 3 h a day" | Day-by-day plan with interleaving, spaced review, mocks and a light last day |

## Install

**Manual (works everywhere):** copy the skills into your Claude Code skills folder.
```bash
git clone https://github.com/OWNER/claude-study-skills
mkdir -p ~/.claude/skills
cp -r claude-study-skills/skills/* ~/.claude/skills/
```
On Windows PowerShell: `Copy-Item -Recurse claude-study-skills\skills\* $HOME\.claude\skills\`. To use them in one project only, copy into `<project>/.claude/skills/` instead.

**As a plugin (untested):**
```
/plugin marketplace add OWNER/claude-study-skills
/plugin install study-skills@study-skills
```

**Requirements:** Python 3.9 or newer. For PDFs, one of: `pdftotext` (poppler, best for tables), `pip install pymupdf`, or `pip install pypdf`. For scanned pages, `tesseract` is optional (or let Claude read the page images). The scripts use only the standard library.

## Quick start (60 seconds)
1. Open Claude Code in a folder that holds your materials.
2. Say: **"Use study-coach. I am studying for <exam>, the date is <date>, I have <n> hours a day, my materials are in ./materials. I am a <background>."**
3. Answer its few questions. It creates `study/`, ingests your files, maps the exam, and proposes what to learn first.
4. Say **"Teach me the first topic"**. Work through the steps, try the question before you reveal the answer, then say **"build the course"** to get `study/course.html` for your phone.
5. Each day: **"What is due today?"** (cards, then new material). When you leave: Claude updates `study/STATE.md`; next time it picks up where you stopped.

## See it work
`examples/depreciation/` holds a small original lesson (straight-line and reducing-balance depreciation), its flashcards, a number-check file and the built course:
```bash
python skills/study-practice/scripts/verify_numbers.py examples/depreciation/worked.json
python skills/study-teach/scripts/build_course.py examples/depreciation/lessons --title "Sample" --out /tmp/course.html
python skills/study-cards/scripts/cards.py anki examples/depreciation/cards.md -o /tmp/anki.tsv
```
Open `examples/depreciation/course.html` in a browser (try it narrow, like a phone).

## How it works
```
 your files --> study-ingest --> study/text/ (page-marked)
                                    |
 past papers + syllabus ----------> study-map --> map.md, topics.csv
                                    |
              study-teach --> lessons/*.md --> course.html (phone)
              study-cards --> cards.md --> Anki / spaced review
              study-practice --> variants, mocks, marking, errors.md
              study-plan --> plan.md (re-run weekly)
                                    |
                      study/STATE.md remembers everything
```
The design rules that matter: **numbers are verified by code, not by the model**; every fact points to a file and page; official answers and correct answers are shown side by side when they differ; garbled sources are flagged, not guessed; big files are never read whole; every session ends with a saved state. More in [docs/method.md](docs/method.md).

## The helper scripts
All standard library, each has `--help`.

| Script | Does |
| --- | --- |
| `skills/study-ingest/scripts/ingest.py` | Files to Markdown with page markers, duplicate detection, bookmark splitting, heading promotion |
| `skills/study-teach/scripts/build_course.py` | Markdown lessons to one validated offline HTML course (drawer, Prev/Next, swipe, progress, steps, quizzes, dark mode, acronym bank) |
| `skills/study-cards/scripts/cards.py` | Parse decks, Anki export, acronym cards from lessons, Leitner scheduling |
| `skills/study-practice/scripts/verify_numbers.py` | Recompute every figure in a worked example with a safe formula evaluator |
| `skills/study-plan/scripts/plan.py` | Day-by-day plan from the exam date, hours and topic weights |

## Your materials and copyright
This repository contains no exam content. You bring your own materials and are responsible for having the right to use them. Do not redistribute papers, official answers or study texts you only hold a licence to read. Keep your `study/` folder out of any public repository (it is in `.gitignore`).

## Limits, honestly
- It will not make you pass; it makes your time efficient and your gaps visible.
- Extraction can garble tables. Spot-check against the original, and keep the `(?)` flags until you have.
- Two or three past papers give a hint about what is tested, not a rule.
- The skills guide the model; they do not replace a good tutor or the exam body's own syllabus.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Tests: `python -m unittest discover -s tests -v`.

## Licence
MIT. See [LICENSE](LICENSE).
