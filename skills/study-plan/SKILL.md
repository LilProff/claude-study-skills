---
name: study-plan
description: Build and maintain a day-by-day study plan from the exam date, daily hours and topic weights, with interleaved topics, spaced review, timed mocks and a light final day. Use when a learner gives an exam date or says they are behind ("plan my revision", "I have 12 days left", "re-plan, I missed two days").
---

# Study plan

## Build it
1. Make sure `study/topics.csv` exists with `name,weight,mastery` (from `study-map`; mastery starts at 0 unless the learner has evidence).
2. Ask for the exam date, hours per day, and fixed rest days.
3. Run:
   ```bash
   python scripts/plan.py --exam-date 2026-12-10 --hours-per-day 3 \
     --topics study/topics.csv --rest-weekday sun --mock-days 3 --out study/plan.md
   ```
   The script splits hours by `weight x (1.2 - mastery)`, interleaves topics in sessions of at most 1.5 h, keeps 20 percent of every day for spaced review (cards and yesterday's mistakes), puts timed mocks in the last days, and makes the final day light.
4. Read the plan back to the learner in five lines: total days, top three topics by hours, when the mocks are, what the last day looks like, and what you dropped or shrank because time is short.

## Keep it alive
- **Weekly:** update mastery from quizzes and mocks, re-run with today's date (`--today`).
- **Missed days:** do not cram. Re-run with today's date. If time no longer covers the high-weight topics, say which low-weight topics are being dropped and why.
- **A mock below 50 percent in a topic:** raise its weight and re-run.
- **Sessions:** 45 to 60 minutes, then a 10-minute break. Start each session with five minutes of retrieval (cards or a blank-page recall), not rereading.

## Triage when time is very short
1. Learn the frame and the commonest question type for the top three topics.
2. Memorise every acronym and formula sheet.
3. Do one timed mock, mark it hard, fix the two biggest errors.
4. Sleep the night before. A rested learner beats an extra hour of cramming.
