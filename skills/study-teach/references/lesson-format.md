# Lesson format (Markdown with a few special blocks)

One file per topic in `study/lessons/`. `scripts/build_course.py` turns them into one HTML course. A finished sample: `examples/depreciation/lessons/depreciation.md`.

## Front matter
```
---
id: group-accounts        optional, defaults to the file name (letters, digits, - and _)
title: Group accounts     shown in the sidebar and as the lesson heading
group: Core topics        sidebar section; lessons with the same group sit together
weight: 14                optional; how often examined, shown as "14x"
---
```
Lessons appear in file-name order, so name files `01-...`, `02-...`.

## Normal Markdown
Headings (`#`, `##`, `###` are shown as small headings inside the lesson), paragraphs, bullet and numbered lists, pipe tables, fenced code, `> quotes`, `**bold**`, `*italic*`, `` `code` ``, links to the web or to other lessons (`[see this](#depreciation)`).

## Special blocks
Each starts with `:::name` on its own line and ends with `:::` on its own line. Blocks cannot be nested.

| Block | Use | Content |
| --- | --- | --- |
| `:::kid` | The "like I'm 10" analogy | Markdown. Optional custom title after the name: `:::kid In plain words` |
| `:::warn`, `:::trap`, `:::mem`, `:::tip` | Coloured boxes (watch out, examiner's trap, memorise, tip) | Markdown |
| `:::frame` | Theory frame table | One row per line: `Key: value`. A line without `Key:` continues the previous value |
| `:::acronym NAME \| purpose` | A mnemonic card | One line per letter: `L: meaning`. Collected into the automatic Acronym bank |
| `:::steps` | A worked example shown one step at a time | Sections that start with `### Step title`; Markdown under each |
| `:::try` | Solve-it-yourself | Question, then a line containing only `---`, then the answer (hidden until tapped) |
| `:::quiz` | One multiple-choice question | `Q: question`, then options `- [ ] wrong` and exactly one `- [x] right`, then `why: one line` |

## Skeleton
````
---
id: topic-id
title: Topic title
group: Core topics
weight: 6
---

:::kid
Two or three sentences a ten-year-old understands. One analogy from the learner's field if it fits.
:::

:::frame
Definition: ...
Scope: ...
Rule or steps: ...
Exceptions: ...
Presented as: ...
Common mistake: ...
:::

:::acronym NAME | what the list is for
A: first item
B: second item
C: third item
:::

## Where it was examined
| Sitting | Marks | What was asked | Difficulty |
| --- | --- | --- | --- |
| 2024 Q3 | 20 | ... | hard |

## Worked example 1 (hardest first)
Short statement of the question and its figures.

:::steps
### 1. Read the question: what is asked, what is the trap?
...
### 2. Set out the layout first
...
### 3. Workings
...
### 4. Final answer and where the marks were
...
:::

:::trap
What the examiners complained about.
:::

:::try
A fresh question.
---
The answer with its working.
:::

:::quiz
Q: One small, factual question?
- [ ] Wrong option
- [x] Right option
- [ ] Wrong option
why: One-line reason.
:::

:::mem
- One-liner 1
- One-liner 2
:::
````

## Check before you build
- Every worked example has a matching entry in `worked.json` and `verify_numbers.py` prints `All numbers verified.`
- Every list the exam asks for has an `:::acronym` block with all the items, in the exam's order.
- `build_course.py` reports no errors.
