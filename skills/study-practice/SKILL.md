---
name: study-practice
description: Generate practice questions, original mock exams and number-checked worked solutions; mark a learner's attempt against a marking guide; and keep an error log. Use when a learner wants to practise ("give me a similar question", "set me a mock", "mark my answer", "check my working", "where did this figure come from").
---

# Study practice

## Principle
A model must never mark its own arithmetic. Every question you set and every solution you show has its numbers recomputed by `scripts/verify_numbers.py`.

## Modes

### 1. Variant of a known question
1. Take a question from `study/map.md` (a hard one the learner has met).
2. Change the numbers and the context, keep the structure and the trap.
3. Solve it into a `worked.json` (inputs, steps with formulas, expected results, checks) and run:
   ```bash
   python scripts/verify_numbers.py study/practice/worked.json
   ```
   Fix the lesson or the formula until it prints `All numbers verified.`
4. Show the learner the question only. Reveal the solution after their attempt, one step at a time.
5. Label it "original practice, not a past paper".

### 2. Mock paper
Use the real format from `study/map.md` (time, number of questions, choice rules, marks). Mix topics in the proportions the map shows. Write the marking guide first (see `references/marking.md`), then the paper, then the solutions. Verify numbers. Tell the learner to use a real clock and no notes. After the mock: mark it, log errors, update mastery.

### 3. Mark an attempt
Score line by line against the marking guide, not by impression. Show marks earned, marks lost and why, and the single change that would have won the most marks. Be strict but kind. Typed answers and photographs both work: read the photo carefully and quote what you read when it is ambiguous.

### 4. Trace a figure
When asked "where did this number come from?": show the working in order, name the formula and the source page, and re-run the check script if the number is new.

## Error log
After every practice, append to `study/practice/errors.md`: date, topic, what went wrong (concept, method, arithmetic, reading the question, time), and the fix. Count categories each week. Concept errors go back to `study-teach`, memory errors to `study-cards`, time errors to a timed drill.

## Update mastery
Adjust the topic's mastery (0 to 1) in `study/STATE.md` and `study/topics.csv` after each quiz or mock. Then re-run `study-plan` if a topic changed by more than 0.2.
