# The method behind these skills

These skills encode a process that was first done by hand for a real, difficult professional exam: tens of past papers, a 900-page study text, three days left, and a learner who had already failed once. The process worked well enough to be worth repeating, so it was written down as skills. This page explains the reasoning so you can bend it to your subject.

## 1. Start from what is tested, not from the textbook
A textbook explains everything equally. An exam does not test everything equally. Reading the past papers and the markers' reports first tells you which topics carry the marks, what the questions look like, and which mistakes cost the most. That is `study-map`. It is the cheapest way to cut a mountain of material down to a path.

## 2. Teach the frame, then the hardest example
Every topic gets a short **frame** (definition, scope, rules, exceptions, presentation) so the learner has a map before the details. Then the hardest question that has actually been asked is solved **slowly**, one decision per step with the reason, because a learner who can do the hard one can do the easy ones. Steps are hidden until tapped so the learner tries first. This follows worked-example and retrieval-practice ideas from learning science: study a solved problem, then recall and apply, rather than rereading.

## 3. Make the explanation small enough to remember
- A "like I'm 10" analogy builds the first, intuitive hook.
- An acronym for every list the exam asks for, because lists are tested word for word and are the cheapest marks to lose.
- Flashcards one fact at a time, reviewed on a spaced schedule, because forgetting is normal and review just before forgetting is efficient.

## 4. Never trust a model's arithmetic
A confident wrong number in a lesson does more damage than no lesson. Every worked example stores its inputs, formulas and expected results as data and a script recomputes them. The same script checks practice questions you generate. This is the single most important rule in the repo.

## 5. Keep official answers honest
Sometimes the published solution is wrong, or garbled in the scan. Do not silently fix it and do not silently copy it. Show both, say which one the marker will reward, and mark doubts `(?)`.

## 6. Practice under exam conditions
Understanding is not the same as being able to produce an answer in 30 minutes. Variants of hard questions, timed mocks with a marking guide written first, and an error log that sorts mistakes into concept, memory, method, arithmetic, reading and time turn practice into targeted repair.

## 7. Plan backwards from the date
`study-plan` allocates time by weight times (1.2 minus mastery), interleaves topics (mixing topics in a week beats blocking one for days), keeps a daily slot for spaced review, puts mocks near the end, and leaves the last day light. When you fall behind it re-plans from today instead of piling work on tomorrow.

## 8. Make the work survive the session
Sessions end, context runs out, accounts change. `study/STATE.md` records where you are, what is next and what you could not verify, so any session (or any other agent) can resume in minutes. Large files are never read whole; search and ranges keep the context small, and heavy reading goes to subagents that write their results to disk.

## What this does not do
- It does not replace the exam body's syllabus, study text or a qualified tutor.
- It does not guarantee a pass. It makes your time more efficient and your gaps visible.
- It cannot read what is not in the text: scanned pages need OCR or a careful visual read, and tables should be spot-checked against the original.
- It does not supply exam content. You bring your own materials and are responsible for having the right to use them.
