#!/usr/bin/env python3
"""Build one mobile-friendly, offline HTML course from Markdown lesson files.

Usage:
  python build_course.py LESSON_DIR --out course.html [--title "My course"] [--template path]

Each lesson is a Markdown file with front matter:

  ---
  id: depreciation          (optional; defaults to the file name)
  title: Depreciation
  group: Core ideas         (sidebar section)
  weight: 5                 (optional; how often examined, shown as a flame count)
  ---

Normal Markdown works (headings, paragraphs, lists, tables, code, quotes, **bold**,
*italic*, `code`, links). Special blocks start with ':::name' and end with ':::':

  :::kid [title]       friendly analogy box          :::warn / :::trap / :::mem / :::tip
  :::frame             lines 'Key: value' become a theory-frame table
  :::acronym NAME | what it is for      lines 'L: meaning' (one per letter)
  :::steps             '### Step title' sections, revealed one at a time
  :::try               question, a line with ---, then the answer (hidden)
  :::quiz              'Q: ...', options '- [x] right' / '- [ ] wrong', 'why: ...'

All acronym blocks are gathered into an automatic 'Acronym bank' lesson.
Exit code 1 if validation finds errors (duplicate ids, unclosed blocks, quiz without a
correct option, broken #links). Standard library only.
"""
import argparse
import html
import re
import sys
from pathlib import Path

LABELS = {"kid": "Like you're 10", "warn": "Watch out", "trap": "The trap", "mem": "Memorise", "tip": "Tip"}


# ---------- inline ----------
def esc(s):
    return html.escape(s, quote=False)


def _fmt(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)

    def link(m):
        href = m.group(2)
        if not re.match(r"^(#|https?://|mailto:)", href):
            return m.group(1)
        return '<a href="%s">%s</a>' % (href.replace('"', "%22"), m.group(1))

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def inline(s):
    out = []
    for part in re.split(r"(`[^`]+`)", s):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            out.append("<code>%s</code>" % esc(part[1:-1]))
        else:
            out.append(_fmt(esc(part)))
    return "".join(out)


# ---------- blocks ----------
LIST_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+(.*)$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def starts_block(ln):
    return bool(re.match(r"^(#{1,4}\s|```|>)", ln) or LIST_RE.match(ln))


def cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def render_md(text):
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if re.match(r"^```", ln):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(buf)))
            continue
        m = re.match(r"^(#{1,4})\s+(.+?)\s*#*$", ln)
        if m:
            lvl = min(len(m.group(1)) + 2, 5)
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue
        if "|" in ln and i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
            head = cells(ln)
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(cells(lines[i]))
                i += 1
            t = "<table><thead><tr>%s</tr></thead><tbody>" % "".join("<th>%s</th>" % inline(c) for c in head)
            for r in rows:
                t += "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r)
            out.append(t + "</tbody></table>")
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % inline(" ".join(buf)))
            continue
        lm = LIST_RE.match(ln)
        if lm:
            ordered = lm.group(1)[0].isdigit()
            items = []
            while i < len(lines):
                mm = LIST_RE.match(lines[i])
                if mm:
                    items.append(mm.group(2))
                    i += 1
                elif lines[i].startswith((" ", "\t")) and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(x) for x in items), tag))
            continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", ln):
            out.append("<hr>")
            i += 1
            continue
        buf = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not starts_block(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))
    return "\n".join(out)


# ---------- directives ----------
DIR_RE = re.compile(r"^:::(\w+)[ \t]*(.*)$")


def split_directives(body, errors, lid):
    parts, buf, lines, i = [], [], body.split("\n"), 0
    while i < len(lines):
        m = DIR_RE.match(lines[i])
        if m:
            if buf:
                parts.append(("md", "\n".join(buf)))
                buf = []
            name, args = m.group(1), m.group(2).strip()
            i += 1
            content = []
            closed = False
            while i < len(lines):
                if lines[i].strip() == ":::":
                    closed = True
                    break
                content.append(lines[i])
                i += 1
            if not closed:
                errors.append("%s: block ':::%s' is never closed with ':::'" % (lid, name))
            parts.append(("dir", name, args, "\n".join(content)))
        else:
            buf.append(lines[i])
        i += 1
    if buf:
        parts.append(("md", "\n".join(buf)))
    return parts


def kv_rows(content):
    rows = []
    for ln in content.split("\n"):
        if not ln.strip():
            continue
        m = re.match(r"^([^:]{1,40}):\s*(.*)$", ln)
        if m:
            rows.append([m.group(1).strip(), m.group(2).strip()])
        elif rows:
            rows[-1][1] += " " + ln.strip()
    return rows


def render_dir(name, args, content, errors, lid, acronyms):
    if name in LABELS:
        title = args or LABELS[name]
        return '<div class="box %s"><b>%s</b>%s</div>' % (name, esc(title), render_md(content))
    if name == "frame":
        rows = kv_rows(content)
        if not rows:
            errors.append("%s: ':::frame' has no 'Key: value' lines" % lid)
        return '<table class="tframe">%s</table>' % "".join(
            '<tr><td class="tk">%s</td><td class="tv">%s</td></tr>' % (inline(k), inline(v)) for k, v in rows)
    if name == "acronym":
        nm, _, purpose = [x.strip() for x in args.partition("|")]
        rows = kv_rows(content)
        if not nm or not rows:
            errors.append("%s: ':::acronym NAME | purpose' needs a name and 'L: meaning' lines" % lid)
        acronyms.append((nm, purpose, rows, lid))
        return acronym_html(nm, purpose, rows)
    if name == "steps":
        chunks = re.split(r"^###\s+(.+)$", content, flags=re.M)
        if len(chunks) < 3:
            errors.append("%s: ':::steps' needs '### Step title' sections" % lid)
        out = ['<div class="steps">']
        for k in range(1, len(chunks) - 1, 2):
            out.append('<details class="step"><summary>%s</summary><div>%s</div></details>' % (
                inline(chunks[k].strip()), render_md(chunks[k + 1].strip())))
        return "".join(out) + "</div>"
    if name == "try":
        pieces = re.split(r"^---\s*$", content, maxsplit=1, flags=re.M)
        if len(pieces) < 2:
            errors.append("%s: ':::try' needs a line with --- between question and answer" % lid)
            pieces = [content, ""]
        return ('<div class="tryit"><b>Try it yourself</b>%s<details><summary>Show the answer</summary>%s</details></div>'
                % (render_md(pieces[0].strip()), render_md(pieces[1].strip())))
    if name == "quiz":
        return quiz_html(content, errors, lid)
    errors.append("%s: unknown block ':::%s'" % (lid, name))
    return ""


def acronym_html(nm, purpose, rows, lesson_id=None, link=False):
    rows_html = "".join('<div class="arow"><span class="al">%s</span><span>%s</span></div>' % (esc(k), inline(v)) for k, v in rows)
    where = ' <a href="#%s">go to lesson</a>' % html.escape(lesson_id) if link and lesson_id else ""
    return '<div class="acro"><div class="aname">%s</div><div class="apur">%s%s</div>%s</div>' % (
        esc(nm), inline(purpose), where, rows_html)


def quiz_html(content, errors, lid):
    lines = content.split("\n")
    q, opts, why, mode = [], [], "", "q"
    for ln in lines:
        m = re.match(r"^\s*-\s*\[( |x|X)\]\s*(.*)$", ln)
        if m:
            opts.append((m.group(1).lower() == "x", m.group(2)))
            mode = "o"
        elif re.match(r"^why:\s*", ln):
            why = re.sub(r"^why:\s*", "", ln)
            mode = "w"
        elif ln.strip():
            if mode == "q":
                q.append(re.sub(r"^Q:\s*", "", ln))
            elif mode == "w":
                why += " " + ln.strip()
    right = [i for i, (ok, _) in enumerate(opts) if ok]
    if len(opts) < 2 or len(right) != 1:
        errors.append("%s: ':::quiz' needs 2+ options and exactly one '- [x]' correct option" % lid)
    idx = right[0] if right else -1
    btns = "".join('<button class="opt" type="button" data-i="%d">%s</button>' % (i, inline(t)) for i, (_, t) in enumerate(opts))
    return ('<div class="quiz" data-correct="%d"><p class="q">%s</p><div class="opts">%s</div><p class="why" hidden>%s</p></div>'
            % (idx, inline(" ".join(q)), btns, inline(why)))


def parse_front(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    meta = {}
    if m:
        for ln in m.group(1).split("\n"):
            k, _, v = ln.partition(":")
            if v.strip():
                meta[k.strip().lower()] = v.split("#")[0].strip() if k.strip().lower() == "weight" else v.strip()
        text = text[m.end():]
    return meta, text


def build(lesson_dir, title, template_path):
    errors, acronyms, sections, ids, links = [], [], [], {}, []
    files = sorted(Path(lesson_dir).glob("*.md"))
    if not files:
        raise SystemExit("no .md lessons found in %s" % lesson_dir)
    for f in files:
        meta, body = parse_front(f.read_text(encoding="utf-8"))
        lid = re.sub(r"[^a-z0-9_-]+", "-", (meta.get("id") or f.stem).lower()).strip("-")
        if lid in ids:
            errors.append("duplicate lesson id '%s' (%s and %s)" % (lid, ids[lid], f.name))
        ids[lid] = f.name
        ltitle = meta.get("title") or f.stem
        group = meta.get("group") or "Lessons"
        heat = re.sub(r"\D", "", meta.get("weight", ""))
        parts = []
        for p in split_directives(body, errors, lid):
            if p[0] == "md":
                parts.append(render_md(p[1]))
            else:
                parts.append(render_dir(p[1], p[2], p[3], errors, lid, acronyms))
        sections.append('<section class="lesson" id="%s" data-group="%s" data-title="%s"%s><h2>%s</h2>%s</section>' % (
            html.escape(lid), html.escape(group), html.escape(ltitle),
            ' data-heat="%s"' % heat if heat else "", esc(ltitle), "\n".join(parts)))
        for target in re.findall(r"\]\(#([^)\s]+)\)", body):
            links.append((lid, target))
    if acronyms:
        cards = "".join(acronym_html(n, p, r, l, link=True) for n, p, r, l in acronyms)
        sections.append('<section class="lesson" id="acronym-bank" data-group="Revision" data-title="Acronym bank">'
                        "<h2>Acronym bank</h2><p>Every mnemonic from the course in one place.</p>%s</section>" % cards)
        ids["acronym-bank"] = "(auto)"
    for lid, target in links:
        if target not in ids:
            errors.append("%s: link to #%s does not match any lesson id" % (lid, target))
    tpl = Path(template_path).read_text(encoding="utf-8")
    page = tpl.replace("{{TITLE}}", html.escape(title)).replace("{{LESSONS}}", "\n".join(sections))
    return page, errors, len(files), len(acronyms)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lessons")
    ap.add_argument("--out", default="course.html")
    ap.add_argument("--title", default="Study course")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "assets" / "template.html"))
    a = ap.parse_args(argv)
    page, errors, n, na = build(a.lessons, a.title, a.template)
    for e in errors:
        print("ERROR " + e, file=sys.stderr)
    if errors:
        print("%d error(s); nothing written." % len(errors), file=sys.stderr)
        return 1
    Path(a.out).write_text(page, encoding="utf-8")
    print("wrote %s: %d lessons, %d acronyms, %d KB" % (a.out, n, na, len(page.encode("utf-8")) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
