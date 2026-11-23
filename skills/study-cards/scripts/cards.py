#!/usr/bin/env python3
"""Flashcards: parse a Markdown deck, export to Anki, schedule reviews, build acronym cards.

Deck format (cards.md): blocks separated by a blank line.

  Q: What does the matching principle say?
  A: Record an expense in the same period as the revenue it helped earn.
  tags: concepts, week1
  src: notes.md p.12

  C: The {{matching}} principle links expenses to the revenue they earn.

  Q = front, A = back (may continue on following lines), C = cloze (the {{hidden}}
  words become [...] on the front and show on the back).

Commands:
  parse   DECK                          print the cards as JSON
  anki    DECK -o deck.tsv              Anki-importable file (tab separated, with tags)
  acronyms LESSON_DIR -o acronyms.md    cards from :::acronym blocks in lesson Markdown
  due     DECK --state s.json [--limit 20] [--today YYYY-MM-DD]
  grade   DECK --state s.json ID again|good|easy [--today YYYY-MM-DD]
  stats   DECK --state s.json

Scheduling is a simple Leitner ladder: boxes at 1, 2, 4, 8, 16 days. again -> box 0,
good -> next box, easy -> skip a box. Standard library only.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

INTERVALS = [1, 2, 4, 8, 16]


def card_id(text):
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()[:8]


def parse_deck(text):
    cards = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().split("\n")
        card = {"tags": [], "src": ""}
        field = None
        for ln in lines:
            m = re.match(r"^(Q|A|C|tags|src):\s*(.*)$", ln)
            if m:
                field = m.group(1)
                val = m.group(2)
                if field == "tags":
                    card["tags"] = [t.strip() for t in val.split(",") if t.strip()]
                elif field == "src":
                    card["src"] = val.strip()
                elif field == "Q":
                    card["q"] = val
                elif field == "A":
                    card["a"] = val
                elif field == "C":
                    card["c"] = val
            elif field in ("Q", "A", "C"):
                key = field.lower()
                card[key] = card.get(key, "") + "\n" + ln
        if "c" in card:
            card["q"] = re.sub(r"\{\{(.+?)\}\}", "[...]", card["c"])
            card["a"] = re.sub(r"\{\{(.+?)\}\}", r"\1", card["c"])
        if card.get("q") and card.get("a"):
            card["id"] = card_id(card["q"])
            cards.append(card)
    return cards


def load_deck(path):
    return parse_deck(Path(path).read_text(encoding="utf-8"))


def to_anki(cards):
    rows = ["#separator:tab", "#html:true", "#tags column:3"]
    for c in cards:
        back = html.escape(c["a"]).replace("\n", "<br>")
        if c["src"]:
            back += '<br><small>%s</small>' % html.escape(c["src"])
        front = html.escape(c["q"]).replace("\n", "<br>")
        tags = " ".join(t.replace(" ", "_") for t in c["tags"])
        rows.append("\t".join([front, back, tags]))
    return "\n".join(rows) + "\n"


ACRO_RE = re.compile(r"^:::acronym[ \t]+(.+?)\n(.*?)^:::[ \t]*$", re.S | re.M)


def acronym_cards(lesson_dir):
    out = []
    for f in sorted(Path(lesson_dir).glob("*.md")):
        for m in ACRO_RE.finditer(f.read_text(encoding="utf-8")):
            head = [x.strip() for x in m.group(1).split("|", 1)]
            name, purpose = head[0], (head[1] if len(head) > 1 else "")
            rows = []
            for ln in m.group(2).strip().split("\n"):
                k, _, v = ln.partition(":")
                if v.strip():
                    rows.append("%s = %s" % (k.strip(), v.strip()))
            if not rows:
                continue
            out.append("Q: Spell out the mnemonic %s%s.\nA: %s\ntags: acronym\nsrc: %s" % (
                name, " (%s)" % purpose if purpose else "", "\n".join(rows), f.name))
            if purpose:
                out.append("Q: Which mnemonic covers: %s?\nA: %s\ntags: acronym\nsrc: %s" % (purpose, name, f.name))
    return "\n\n".join(out) + "\n"


def load_state(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_state(path, state):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")


def today_of(a):
    return date.fromisoformat(a.today) if getattr(a, "today", None) else date.today()


def due_cards(cards, state, today, limit=None):
    due = []
    for c in cards:
        s = state.get(c["id"])
        if s is None or date.fromisoformat(s["due"]) <= today:
            due.append(c)
    return due[:limit] if limit else due


def grade(state, cid, result, today):
    s = state.get(cid, {"box": 0, "reviews": 0})
    if result == "again":
        s["box"] = 0
    elif result == "good":
        s["box"] = min(s["box"] + 1, len(INTERVALS) - 1)
    elif result == "easy":
        s["box"] = min(s["box"] + 2, len(INTERVALS) - 1)
    else:
        raise SystemExit("grade must be again, good or easy")
    s["reviews"] = s.get("reviews", 0) + 1
    s["due"] = (today + timedelta(days=INTERVALS[s["box"]])).isoformat()
    state[cid] = s
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parse"); p.add_argument("deck")
    p = sub.add_parser("anki"); p.add_argument("deck"); p.add_argument("-o", "--out", required=True)
    p = sub.add_parser("acronyms"); p.add_argument("lessons"); p.add_argument("-o", "--out", required=True)
    for name in ("due", "grade", "stats"):
        p = sub.add_parser(name)
        p.add_argument("deck")
        p.add_argument("--state", required=True)
        p.add_argument("--today")
        if name == "due":
            p.add_argument("--limit", type=int)
        if name == "grade":
            p.add_argument("id")
            p.add_argument("result", choices=["again", "good", "easy"])
    a = ap.parse_args(argv)

    if a.cmd == "parse":
        print(json.dumps(load_deck(a.deck), indent=2, ensure_ascii=False))
    elif a.cmd == "anki":
        cards = load_deck(a.deck)
        Path(a.out).write_text(to_anki(cards), encoding="utf-8")
        print("wrote %s (%d cards). In Anki: File > Import, then pick the file." % (a.out, len(cards)))
    elif a.cmd == "acronyms":
        text = acronym_cards(a.lessons)
        Path(a.out).write_text(text, encoding="utf-8")
        print("wrote %s (%d cards)" % (a.out, len(parse_deck(text)) if text.strip() else 0))
    else:
        cards = load_deck(a.deck)
        state = load_state(a.state)
        t = today_of(a)
        if a.cmd == "due":
            for c in due_cards(cards, state, t, a.limit):
                print("%s\t%s" % (c["id"], c["q"].replace("\n", " ")))
        elif a.cmd == "grade":
            ids = {c["id"] for c in cards}
            if a.id not in ids:
                raise SystemExit("unknown card id: %s" % a.id)
            s = grade(state, a.id, a.result, t)
            save_state(a.state, state)
            print("%s -> box %d, next review %s" % (a.id, s["box"], s["due"]))
        elif a.cmd == "stats":
            boxes = [0] * len(INTERVALS)
            for c in cards:
                s = state.get(c["id"])
                if s:
                    boxes[s["box"]] += 1
            print("cards: %d, new: %d, due now: %d" % (len(cards), len(cards) - sum(boxes), len(due_cards(cards, state, t))))
            print("boxes: " + ", ".join("%dd:%d" % (INTERVALS[i], n) for i, n in enumerate(boxes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
