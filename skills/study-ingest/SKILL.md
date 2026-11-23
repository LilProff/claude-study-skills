---
name: study-ingest
description: Convert a learner's study materials (PDF, Word, PowerPoint, text, images) into clean, page-marked Markdown so they can be searched, split and cited. Use at the start of a study project, when new materials arrive, or when a PDF is too big to read directly.
---

# Study ingest

Goal: turn every file into text you can search and cite, without ever loading a big document into context.

## Steps
1. List what you have: `ls` the materials folder. Note file types, sizes and anything that looks like a duplicate.
2. Convert everything in one go:
   ```bash
   python scripts/ingest.py study/materials --out study/text
   ```
   (`scripts/` is next to this SKILL.md.) It writes `study/text/<name>.md` with `<!-- page N -->` markers and `index.json` (hashes, page counts, warnings). Identical files are skipped.
3. Read `index.json`, not the texts. Act on every warning:
   - "very little text per page": the file is scanned. Use OCR (`tesseract`) or look at the page images yourself and transcribe only what you need.
   - "image needs OCR": same.
   - "duplicate of ...": ignore the copy.
4. Spot-check one page of each source against the original (open the PDF page or compare a table). Layout extraction keeps columns aligned, but tables can still garble. When a table does not add up, rebuild it from its totals and mark any doubtful cell `(?)`.
5. **Trim what is out of scope.** Multi-subject bundles hold other subjects. Find boundaries by cover pages or headings (for example a title page that names the next subject), not by fixed page numbers, because order changes between editions. Convert only the relevant range with `--range 10-140`, or delete the unneeded files from `study/text/`.
6. **Split big books into chapters.** `--split-bookmarks` (needs PyMuPDF) writes one file per top-level bookmark. Otherwise split on headings. Use `--promote '^(Question|Section) \d+'` to turn recurring structural lines into `##` headings so you can navigate with grep.
7. Record in `study/STATE.md`: sources ingested, scanned or doubtful files, and the page ranges that matter.

## Reading discipline
- Use `grep -n` to find things and read only the lines you need.
- A single analysis pass should cover at most about 30 pages. For more, split the work across subagents, each writing its result to a file.
- Never paste a whole chapter into the conversation. Quote only the lines you will use, with their page marker.

## Scripts
`scripts/ingest.py --help` shows all options. Standard library only; PDFs need `pdftotext` (poppler) or PyMuPDF or pypdf.
