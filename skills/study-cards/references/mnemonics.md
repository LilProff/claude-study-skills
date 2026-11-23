# Mnemonics and acronyms

## When to make one
- The exam asks for a list in full ("state the criteria", "list the steps", "outline the factors").
- The list has three or more items. For one or two items, just learn them.
- The list is stable: the items do not change between editions or textbooks.

## How to build a good one
1. **Write the list exactly as the source or the marking guide words it.** Number the items. Do not reword the exam's terms to make a nicer acronym.
2. **Take the first letter of each item** (or the first letter of its key word).
3. **Try to make a real word or short phrase.** If the list is ordered, keep the order. If it is not, you may rearrange to make a word, and say so on the card.
4. **Fall back to a sentence** when no word works: each word starts with the next letter (like "Every Good Boy Deserves Football").
5. **Make it vivid.** A strange image is easier to recall than a neat one. Programmers: a pun on a familiar term works well (for example CRUD for Cost, Residual value, Useful life, Depreciation method).
6. **Check completeness.** Count the letters against the items. Check no item is missing or duplicated.
7. **Test it tomorrow.** On a blank page, write the acronym, then expand it. If you stumble, change the mnemonic, not the learner.

## Card format
Put it in the lesson:
```
:::acronym CRUD | what you need before you can depreciate
C: Cost (including delivery and set-up)
R: Residual value
U: Useful life
D: Depreciation method
:::
```
`scripts/cards.py acronyms study/lessons` then produces two cards per acronym: spell it out, and "which mnemonic covers this topic?".

## Anti-patterns
- Forcing nonsense letters to spell a word, then forgetting what the letters mean. Prefer a sentence.
- One acronym covering two different lists.
- Acronyms for things the exam asks you to explain (you need understanding, not letters).
- Long acronyms over seven letters. Split the list into two, each with its own mnemonic.
- Mnemonics without a worked use. After the letters, add one line saying how an answer would use each item.

## Writing the answer from a mnemonic
Acronym letters are for recall, not for the answer. In the exam, write the full items as headings, one line of explanation each, and an example if the question says "discuss" or "explain". Markers reward the content, not the letters.
