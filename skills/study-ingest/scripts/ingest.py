#!/usr/bin/env python3
"""Convert study materials into layout-preserving Markdown with page markers.

Usage:
  python ingest.py INPUT [INPUT ...] --out study/text [options]

INPUT is a file or a folder (searched recursively). Supported: .pdf .docx .pptx
.txt .md and images (.png .jpg .jpeg .tif .tiff .webp, via tesseract if installed).

Writes <out>/<name>.md (with <!-- page N --> markers so every fact can be cited
back to a page) and <out>/index.json (sources, hashes, page and character counts,
warnings). Identical files (same SHA-256) are skipped.

Standard library only. PDFs need one of: pdftotext (poppler, preferred because
-layout keeps table columns aligned), PyMuPDF (pip install pymupdf) or pypdf.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
SUPPORTED = {".pdf", ".docx", ".pptx", ".txt", ".md"} | IMAGES


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "doc"


def split_pages(text):
    pages = text.split("\f")
    while pages and not pages[-1].strip():
        pages.pop()
    return pages


def pdf_pages(path):
    exe = shutil.which("pdftotext")
    if exe:
        r = subprocess.run([exe, "-layout", str(path), "-"], capture_output=True)
        if r.returncode == 0:
            return split_pages(r.stdout.decode("utf-8", "replace"))
    try:
        import fitz  # PyMuPDF

        with fitz.open(str(path)) as doc:
            return [p.get_text() for p in doc]
    except ImportError:
        pass
    try:
        from pypdf import PdfReader

        return [(p.extract_text() or "") for p in PdfReader(str(path)).pages]
    except ImportError:
        pass
    raise RuntimeError("No PDF backend. Install poppler (pdftotext), pymupdf or pypdf.")


def docx_pages(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []

    def para_text(p):
        return "".join(t.text or "" for t in p.iter(W + "t")).strip()

    for el in list(body):
        if el.tag == W + "p":
            txt = para_text(el)
            if not txt:
                lines.append("")
                continue
            style = el.find(f"{W}pPr/{W}pStyle")
            val = style.get(W + "val", "") if style is not None else ""
            m = re.match(r"Heading\s*(\d)", val)
            lines.append(("#" * min(int(m.group(1)), 4) + " " + txt) if m else txt)
        elif el.tag == W + "tbl":
            for tr in el.iter(W + "tr"):
                cells = [" ".join(para_text(p) for p in tc.iter(W + "p")).strip() for tc in tr.iter(W + "tc")]
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
    return ["\n".join(lines)]


def pptx_pages(path):
    pages = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        names.sort(key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
        for n in names:
            root = ET.fromstring(z.read(n))
            paras = []
            for p in root.iter(A + "p"):
                t = "".join(x.text or "" for x in p.iter(A + "t")).strip()
                if t:
                    paras.append(t)
            pages.append("\n".join(paras))
    return pages


def image_pages(path, warnings):
    exe = shutil.which("tesseract")
    if not exe:
        warnings.append("image needs OCR: install tesseract or read the image directly with a vision-capable model")
        return []
    r = subprocess.run([exe, str(path), "stdout"], capture_output=True)
    return [r.stdout.decode("utf-8", "replace")]


def text_pages(path):
    return [Path(path).read_text(encoding="utf-8", errors="replace")]


def clean_page(text):
    """Trim noise without touching table numbers.

    A bare number is dropped only if it is the first or last non-empty line of
    the page (that is a page number, not a table cell)."""
    lines = [ln.rstrip() for ln in text.replace("\r", "").split("\n")]
    idx = [i for i, ln in enumerate(lines) if ln.strip()]
    for i in (idx[:1] + idx[-1:]):
        if re.fullmatch(r"\s*(page\s*)?\d{1,4}\s*", lines[i], flags=re.I):
            lines[i] = ""
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")
    return out


def promote(text, patterns):
    if not patterns:
        return text
    regs = [re.compile(p) for p in patterns]
    out = []
    for ln in text.split("\n"):
        if any(r.search(ln.strip()) for r in regs) and not ln.lstrip().startswith("#"):
            out.append("## " + ln.strip())
        else:
            out.append(ln)
    return "\n".join(out)


def parse_range(spec):
    if not spec:
        return None
    m = re.fullmatch(r"(\d+)-(\d+)", spec)
    if not m:
        raise SystemExit("--range must look like 10-40")
    return int(m.group(1)), int(m.group(2))


def render(title, pages, first_page, markers, patterns):
    parts = ["# " + title, ""]
    for i, p in enumerate(pages):
        if markers:
            parts.append("<!-- page %d -->" % (first_page + i))
        parts.append(promote(clean_page(p), patterns))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def bookmark_split(path, pages, out_dir, stem, markers, patterns, entry):
    """Split a PDF into chapter files using its bookmarks (needs PyMuPDF)."""
    try:
        import fitz
    except ImportError:
        entry["warnings"].append("--split-bookmarks needs pymupdf; wrote one file instead")
        return
    with fitz.open(str(path)) as doc:
        toc = [t for t in doc.get_toc() if t[0] == 1]
    if not toc:
        entry["warnings"].append("no bookmarks found; wrote one file instead")
        return
    chapters = []
    for n, (lvl, title, start) in enumerate(toc):
        end = toc[n + 1][2] - 1 if n + 1 < len(toc) else len(pages)
        if end < start:
            end = start
        name = "%s__%02d_%s.md" % (stem, n + 1, slug(title)[:50])
        (out_dir / name).write_text(render(title, pages[start - 1:end], start, markers, patterns), encoding="utf-8")
        chapters.append({"title": title, "pages": [start, end], "file": name})
    entry["chapters"] = chapters


def collect(inputs):
    files = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in SUPPORTED)
        elif p.is_file():
            files.append(p)
        else:
            print("skip (not found): %s" % raw, file=sys.stderr)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="study/text")
    ap.add_argument("--range", help="page range for single-file runs, e.g. 10-40")
    ap.add_argument("--promote", action="append", default=[], help="regex; matching lines become '## ' headings")
    ap.add_argument("--no-page-markers", action="store_true")
    ap.add_argument("--split-bookmarks", action="store_true", help="PDF: one file per top-level bookmark (needs pymupdf)")
    args = ap.parse_args(argv)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = parse_range(args.range)
    files = collect(args.inputs)
    index, seen = [], {}
    for f in files:
        entry = {"source": str(f), "kind": f.suffix.lower().lstrip("."), "warnings": []}
        digest = sha256(f)
        entry["sha256"] = digest
        if digest in seen:
            entry["warnings"].append("duplicate of " + seen[digest])
            entry["skipped"] = True
            index.append(entry)
            print("duplicate, skipped: %s" % f)
            continue
        seen[digest] = str(f)
        ext = f.suffix.lower()
        try:
            if ext == ".pdf":
                pages = pdf_pages(f)
            elif ext == ".docx":
                pages = docx_pages(f)
            elif ext == ".pptx":
                pages = pptx_pages(f)
            elif ext in IMAGES:
                pages = image_pages(f, entry["warnings"])
            else:
                pages = text_pages(f)
        except Exception as e:  # keep going on one bad file
            entry["warnings"].append("failed: %s" % e)
            entry["skipped"] = True
            index.append(entry)
            print("FAILED %s: %s" % (f, e), file=sys.stderr)
            continue
        first = 1
        if rng and len(files) == 1:
            first = rng[0]
            pages = pages[rng[0] - 1:rng[1]]
        chars = sum(len(p) for p in pages)
        if pages and chars / max(len(pages), 1) < 40:
            entry["warnings"].append("very little text per page: scanned? try OCR or a vision-capable read")
        stem = slug(f.stem)
        name = stem + ".md"
        (out_dir / name).write_text(render(f.stem, pages, first, not args.no_page_markers, args.promote), encoding="utf-8")
        entry.update({"out": name, "pages": len(pages), "chars": chars})
        if args.split_bookmarks and ext == ".pdf":
            bookmark_split(f, pages, out_dir, stem, not args.no_page_markers, args.promote, entry)
        index.append(entry)
        print("ok: %s -> %s (%d pages, %d chars)" % (f.name, name, len(pages), chars))
        for w in entry["warnings"]:
            print("  warning: " + w)
    (out_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    done = [e for e in index if not e.get("skipped")]
    if not done:
        print("nothing converted", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
