---
name: study-teach
description: Teach a topic step by step in plain language, with an analogy, a theory frame, mnemonics, hard worked examples revealed one step at a time, a try-it and quizzes, then build all lessons into one phone-friendly offline course. Use when a learner wants to understand a topic ("explain X like I'm 10", "teach me Y", "walk me through this question") or wants a study course made from their materials.
---

# Study teach

Two modes: **write lessons** (a course for later) and **live tutoring** (right now, in chat). Both follow the same recipe.

## The lesson recipe (in this order)
1. **Analogy** in a `:::kid` box. Two or three sentences a ten-year-old gets. Add one analogy from the learner's own field (for example a programmer analogy) when it is truly apt.
2. **Theory frame** in a `:::frame` table. Rows depend on the subject. Examples: definition, scope, when it applies, rules or steps, measurement, exceptions, how it is presented, common mistake. Keep each cell to one line.
3. **Mnemonics** in `:::acronym` blocks for every list the exam asks for (see the `study-cards` skill for rules).
4. **Exam map**: a small table of where this topic appeared (from `study/map.md`): sitting, marks, what was asked, difficulty.
5. **Two or three hard worked examples**, hardest first from the map, each as `:::steps`:
   - Step 1: how to read the question and what the trap is.
   - Then one step per decision, each with the reason, not just the arithmetic.
   - A last step: where the marks were and what the marker complained about.
   Put layout or format first (the proforma, the table), then workings, then the finished answer.
6. **Try it** in `:::try`: a fresh question with the answer hidden.
7. **Quizzes** in `:::quiz`: two or three questions, one fact each, with a one-line reason.
8. **Memorise** in `:::mem`: five to ten one-liners for the night before.

Exact syntax and a skeleton are in `references/lesson-format.md`. A finished sample is in `examples/depreciation/lessons/depreciation.md`.

## Quality bar
- Every number in a worked example is verified by `study-practice/scripts/verify_numbers.py` before the lesson is saved. Put the example in a `worked.json` next to the lesson.
- Facts from the learner's materials carry a page tag. Anything you add from general knowledge is marked as such.
- Theory is complete where the exam asks for lists: count the items against the source.
- Short sentences. One idea per paragraph. Define a term the first time you use it. No filler, no emoji.
- If the source and the correct rule disagree, show both and say which the marker rewards.

## Write lessons for a course
1. Choose topics in map order (highest weight x frequency first). Create `study/lessons/NN-topic.md` with front matter (`id`, `title`, `group`, `weight`).
2. For many topics, run one writer subagent per topic stream with the same brief (this file plus `references/lesson-format.md`), each saving its own files and an acronym list. Review for consistency afterwards.
3. Build and check:
   ```bash
   python scripts/build_course.py study/lessons --title "My course" --out study/course.html
   ```
   The script validates (duplicate ids, unclosed blocks, quizzes without a correct option, broken links), adds an automatic acronym bank, and makes one offline HTML file with a topic drawer, bottom Prev/Next bar, swipe, progress ticks, revealable steps, quizzes, dark mode and resume where you stopped.
4. Tell the learner to open `course.html` on their phone (send it to themselves, or serve the folder locally). Note it in STATE.md.

## Live tutoring (in chat)
- **One step at a time.** Show the analogy, then the rule, then ask the learner to try the next step before you reveal it.
- **Ask before telling.** When they are stuck, ask a question that points at the missing idea ("what do we know about the cost?"). Give the answer only after a genuine attempt or a clear request.
- **Check understanding.** After each idea, ask for it back in their own words or with one small question.
- **Trace any figure.** When asked "where did this number come from?", show the working line by line and name the source page.
- **Record mastery.** After each exchange, note in STATE.md which topic they got right or wrong.
