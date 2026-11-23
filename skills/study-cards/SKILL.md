---
name: study-cards
description: Make flashcards, cloze cards and memorable acronyms from lessons or notes, export them to Anki, and schedule spaced reviews. Use when a learner needs to memorise definitions, rules, formulas or lists ("make flashcards", "give me a mnemonic for this list", "quiz me on this", "export to Anki").
---

# Study cards

## Flashcards that work
- **One fact per card.** If an answer has "and" in it, split it.
- **Ask for retrieval, not recognition.** "Why does X happen?" or "What is the formula for X?" beats yes/no.
- **Cloze for rules and definitions:** `C: The {{matching}} principle links expenses to revenue.`
- **Give a cue, not the answer.** The front must be answerable from memory.
- **Include the reverse** only for things the exam asks both ways (term to definition, definition to term).
- **Add `src:`** (file and page) and `tags:` (topic, week) so cards can be traced and filtered.
- **Verify every figure** in a card with `study-practice/scripts/verify_numbers.py` before saving.
- Aim for 5 to 15 cards per lesson. Fewer, sharper cards beat hundreds.

Deck format (`study/cards/cards.md`, blocks separated by a blank line):
```
Q: Straight-line formula?
A: (Cost - Residual value) / Useful life.
tags: depreciation, formulas
src: notes.md p.12

C: Reducing balance applies a fixed rate to the opening {{carrying amount}}.
tags: depreciation
```

## Acronyms and mnemonics
Use them for lists the exam asks for in full. Rules, and a way to build good ones, are in `references/mnemonics.md`. Put each one in the lesson as an `:::acronym` block, then generate cards from all lessons:
```bash
python scripts/cards.py acronyms study/lessons -o study/cards/acronyms.md
```

## Export and review
```bash
python scripts/cards.py parse  study/cards/cards.md                     # check it parses
python scripts/cards.py anki   study/cards/cards.md -o study/cards/anki.tsv   # import in Anki: File > Import
python scripts/cards.py due    study/cards/cards.md --state study/cards/review-state.json --limit 20
python scripts/cards.py grade  study/cards/cards.md --state study/cards/review-state.json CARDID good
python scripts/cards.py stats  study/cards/cards.md --state study/cards/review-state.json
```
`due` lists today's cards (new cards first appear immediately). In a chat review: show the front, wait for the learner's answer, show the back, ask them to rate `again`, `good` or `easy`, then run `grade`. Boxes are 1, 2, 4, 8 and 16 days, so a wrong card returns tomorrow.

## Daily rhythm to suggest
Ten to twenty minutes of due cards first, then new material. Never skip two days in a row. In the last three days before the exam, review only the cards marked `again` in the past week plus all acronyms.
