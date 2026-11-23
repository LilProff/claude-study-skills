# Contributing

Thanks for helping people study better. Keep changes small and tested.

## Ground rules
- **No third-party exam content.** Never add past papers, official answers, textbook passages or anything you do not have the right to share. Examples must be original (the depreciation sample was written for this repo).
- **Skills stay short and concrete.** A `SKILL.md` says when to use it and what to do, with exact commands. Put long reference material in `references/`.
- **Scripts use only the Python standard library** (3.9+). Optional extras (PyMuPDF, pypdf, tesseract) must degrade gracefully with a clear message.
- **Numbers are verified by code.** If you add a feature that shows figures, route them through `verify_numbers.py`.
- **Mobile first** for anything that produces a page: check at 375 px wide, tap targets at least 44 px, no horizontal page scroll.

## Run the tests
```bash
python -m unittest discover -s tests -v
```
Add a test for every script change. PDF tests must skip when no backend is installed.

## Pull requests
Say what you changed, how you tested it, and what you did not test. If you change a skill's wording, say which situation it fixes (what the model did wrong before).

## Ideas welcome
Better mnemonics guidance for non-English learners, more export formats (Quizlet, Obsidian), a spaced-repetition scheduler with proper intervals, subject-specific lesson skeletons (maths, law, medicine, languages), accessibility improvements to the course page.
