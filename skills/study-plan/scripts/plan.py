#!/usr/bin/env python3
"""Build a day-by-day study plan from an exam date, daily hours and topic weights.

Usage:
  python plan.py --exam-date 2026-12-10 --hours-per-day 3 --topics topics.csv \
      [--today 2026-11-23] [--rest-weekday sun] [--mock-days 3] [--out study/plan.md]

topics.csv (or .json list) columns: name, weight, mastery
  weight  = how much the topic matters (marks share or how often it is examined)
  mastery = 0 (know nothing) .. 1 (solid); default 0

Rules: need = weight * (1.2 - mastery). The last day is light (cards, acronyms, sleep).
The mock days before it each hold one timed mock plus mistake review. All other days
split the hours between learning (80 percent, interleaved across topics, sessions of
at most 1.5 h) and a 20 percent spaced-review slot (cards and past mistakes).
Standard library only.
"""
import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def load_topics(path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        rows = json.loads(p.read_text(encoding="utf-8"))
    else:
        with open(p, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    topics = []
    for r in rows:
        name = str(r.get("name", "")).strip()
        if not name:
            continue
        w = float(r.get("weight") or 1)
        m = min(max(float(r.get("mastery") or 0), 0.0), 1.0)
        topics.append({"name": name, "weight": w, "mastery": m, "need": w * (1.2 - m)})
    if not topics:
        raise SystemExit("no topics found")
    return topics


def build(exam, today, hours, topics, rest, mock_days):
    days = []
    d = today
    while d < exam:
        days.append(d)
        d += timedelta(days=1)
    if not days:
        raise SystemExit("exam date must be after today")
    plan = {}
    plan[days[-1]] = {"kind": "light", "items": [("Light review: acronyms, flashcards, weak notes. Early night.", min(hours, 1.5))]}
    pool = days[:-1]
    mocks = pool[-mock_days:] if mock_days and len(pool) > mock_days else []
    for m in mocks:
        plan[m] = {"kind": "mock", "items": [("Timed mock paper (real format, real clock)", min(hours * 0.6, 3.5)),
                                              ("Mark it, log every lost mark, re-do the weakest question", hours * 0.4)]}
    learn_days = [x for x in pool if x not in plan]
    rested = [x for x in learn_days if DAYS[x.weekday()] in rest]
    for x in rested:
        plan[x] = {"kind": "rest", "items": [("Rest day: 15 min flashcards only", 0.25)]}
    learn_days = [x for x in learn_days if x not in rested]
    total_need = sum(t["need"] for t in topics)
    capacity = hours * 0.8 * len(learn_days)
    for t in topics:
        t["hours"] = capacity * t["need"] / total_need if total_need else 0
    queue = sorted(topics, key=lambda t: -t["need"])
    remaining = {t["name"]: t["hours"] for t in queue}
    for x in learn_days:
        cap = hours * 0.8
        items = []
        guard = 0
        while cap > 1e-6 and any(v > 1e-6 for v in remaining.values()) and guard < 200:
            guard += 1
            for t in queue:
                r = remaining[t["name"]]
                if r <= 1e-6 or cap <= 1e-6:
                    continue
                chunk = min(1.5, r, cap)
                items.append((t["name"], chunk))
                remaining[t["name"]] -= chunk
                cap -= chunk
        items.append(("Spaced review: flashcards + yesterday's mistakes", hours * 0.2))
        plan[x] = {"kind": "learn", "items": items}
    return days, plan, topics


def render(days, plan, topics, exam, hours):
    out = ["# Study plan", "", "Exam: **%s**. Daily budget: %.1f h. Days: %d." % (exam.isoformat(), hours, len(days)), "",
           "## Hours per topic (before review slots)", "", "| Topic | Weight | Mastery | Hours |", "| --- | --- | --- | --- |"]
    for t in sorted(topics, key=lambda t: -t["hours"]):
        out.append("| %s | %g | %.1f | %.1f |" % (t["name"], t["weight"], t["mastery"], t["hours"]))
    out += ["", "## Day by day", ""]
    for d in days:
        p = plan[d]
        out.append("### %s %s (%s)" % (DAYS[d.weekday()].title(), d.isoformat(), p["kind"]))
        for label, h in p["items"]:
            out.append("- [ ] %s: %.1f h" % (label, h))
        out.append("")
    out += ["## How to use this", "",
            "- Tick boxes as you go. After each week, update mastery in the topics file and re-run this script.",
            "- Missed a day? Do not cram it into tomorrow. Re-run with today's date.",
            "- If a mock shows a topic below 50 percent, raise its weight and re-run.", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exam-date", required=True)
    ap.add_argument("--hours-per-day", type=float, required=True)
    ap.add_argument("--topics", required=True)
    ap.add_argument("--today")
    ap.add_argument("--rest-weekday", action="append", default=[], choices=DAYS)
    ap.add_argument("--mock-days", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    exam = date.fromisoformat(a.exam_date)
    today = date.fromisoformat(a.today) if a.today else date.today()
    days, plan, topics = build(exam, today, a.hours_per_day, load_topics(a.topics), set(a.rest_weekday), a.mock_days)
    text = render(days, plan, topics, exam, a.hours_per_day)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print("wrote %s (%d days)" % (a.out, len(days)))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
