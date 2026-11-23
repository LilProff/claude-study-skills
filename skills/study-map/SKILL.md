---
name: study-map
description: Analyse past questions, the syllabus and marking guides to find what an exam really tests, how often, how marks are won and lost, and which topics to learn first. Use after ingesting materials and before writing lessons or planning, or when a learner asks "what should I focus on?".
---

# Study map (the exam model)

Goal: produce `study/map.md`, the one page that tells you and the learner where the marks are.

## Inputs
- Past papers, ideally with marking guides, suggested solutions and examiner or chief-marker reports (`study/text/`).
- The syllabus or table of contents with weights, if there is one.
- If there are no past papers: build the map from the syllabus and the materials, and say clearly that frequency data is missing.

## Method
1. **Inventory.** List every paper (sitting/year) and every question in it. Check the count against the paper's stated format.
2. **Analyse each question into one record.** Save as `study/analysis/<paper>.md` (or `.jsonl`). One record:
   ```
   paper, number, marks, section, optional?
   topic(s), syllabus area
   what is asked (verb: calculate, explain, discuss, prepare...)
   figures given (only what matters)
   official approach in 4 to 8 steps
   marking guide: where the marks sit
   examiner's comments: common mistakes, praise
   difficulty (easy/medium/hard) and why
   traps
   official_errors: where the official answer looks wrong (official vs correct, reason)
   uncertain: anything garbled or doubted, marked (?)
   source: file and page
   ```
3. **Parallelise safely.** With many papers, give each subagent 3 papers and one output file each, with this schema. They write to disk, so a stopped job can resume. Do not let them skip questions.
4. **Verify.** Marks should sum to the paper total. Question counts should match the format. Re-add any table you rely on.
5. **Synthesise `study/map.md`:**
   - Paper format: time, number of questions, choice rules, marks per section.
   - Topic frequency table: topic, papers it appeared in out of available, typical marks, where it sits in the paper.
   - Calculation vs theory split.
   - Recurring examiner complaints (write them as rules the learner can follow).
   - Hardest question per topic, to be used as the worked example in `study-teach`.
   - Theory lists that are asked again and again (feeds `study-cards` acronyms).
   - A ranked "learn first" list: weight x frequency.
6. Seed `study/topics.csv` (`name,weight,mastery`) from the table so `study-plan` can use it.

## Rules
- Report what the data shows, not what you expect. If a topic is rare, say so.
- Distinguish **official answer** from **correct answer** whenever they differ, and keep both.
- A map built from three papers is a hint, not a law. State the sample size in the map.
- Every claim in the map points back to a file and page.
