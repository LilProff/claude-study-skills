---
id: depreciation
title: Depreciation (straight line and reducing balance)
group: Worked sample
weight: 5
---

:::kid
You buy a phone for 12,000 and it will last about 5 years. You would not say "I lost 12,000 this year". You spread the cost over the years you use it. That spreading is **depreciation**.

Programmer view: it is amortising a one-off cost across the time slices (periods) that benefit from it.
:::

:::frame
Definition: Systematic allocation of an asset's depreciable amount over its useful life.
Depreciable amount: Cost minus residual value.
When it starts: When the asset is available for use, not when it is paid for.
Methods: Straight line (equal each year), reducing balance (fixed % of the opening carrying amount), units of production.
Presentation: Expense in the income statement. Accumulated depreciation reduces the asset in the balance sheet.
Common mistake: Depreciating land, or forgetting to deduct the residual value in straight line.
:::

:::acronym CRUD | what you need before you can depreciate
C: Cost (including delivery and set-up)
R: Residual value (what it is worth at the end)
U: Useful life (years or units)
D: Depreciation method (straight line, reducing balance, units)
:::

## Worked example: same asset, two methods

An asset costs 12,000, has a residual value of 2,000 and a useful life of 5 years. Reducing balance uses 20% a year.

:::steps
### 1. Read the question: what is asked and what is the trap?
Two methods on the same asset, so do two small workings, not one. The trap: straight line uses cost **minus residual**, reducing balance applies the percentage to the **carrying amount** (the residual is ignored in the calculation).
### 2. Straight line, year 1
Depreciable amount = 12,000 - 2,000 = 10,000. Divide by 5 years: **2,000 a year**.
### 3. Straight line, carrying amount after 2 years
12,000 - (2 x 2,000) = **8,000**.
### 4. Reducing balance, year 1
20% x 12,000 = **2,400**. Carrying amount at end of year 1 = 9,600.
### 5. Reducing balance, year 2
20% x 9,600 = **1,920**. Notice it is smaller than year 1: that is the point of the method.
### 6. Compare
Year 1: reducing balance charges more (2,400 vs 2,000). By year 2 it charges less (1,920 vs 2,000). Total expense over the life is the same only if you stop at the residual value.
:::

| Year | Straight line | Reducing balance (20%) |
| --- | --- | --- |
| 1 | 2,000 | 2,400 |
| 2 | 2,000 | 1,920 |

:::trap
Examiners love to give a residual value and then see whether you use it in the **reducing balance** calculation. You do not subtract it first. You only stop depreciating when the carrying amount reaches the residual value.
:::

:::try
A machine costs 30,000, residual value 6,000, life 4 years. Find the straight-line charge for year 1 and the carrying amount after 3 years.
---
Charge = (30,000 - 6,000) / 4 = **6,000**. Carrying amount after 3 years = 30,000 - 3 x 6,000 = **12,000**.
:::

:::quiz
Q: Which figure does reducing balance apply the percentage to?
- [ ] Cost minus residual value
- [x] The opening carrying amount
- [ ] The residual value
why: Each year the rate is applied to what is left on the books, so the charge shrinks.
:::

:::mem
- Straight line: (Cost - Residual) / Life. Same every year.
- Reducing balance: rate x opening carrying amount. Falls every year.
- Start depreciating when the asset is ready for use. Never depreciate land.
:::
