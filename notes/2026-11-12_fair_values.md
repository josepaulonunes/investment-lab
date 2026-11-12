# 12 Nov 2026: fair prices of my 8 top priorities

Each fair price mixes four independent views, so no single source decides:

| Piece | Weight |
|---|---|
| My DCF (next 12 months profit x share that becomes cash, 9% discount, 11% for risky ones) | 30% |
| Morningstar fair value | 30% |
| Next 12 months profit x the stock's own 5-year average P/E | 20% |
| Average bank target x 0.92 (targets are one year ahead and usually optimistic) | 20% |

Company changes:
- Microsoft, Alphabet, Amazon, Meta: the 5-year P/E is cut 15% because they now spend far more on data centres, so each dollar of profit turns into less cash.
- Micron: cycle model. Two peak years of cash (176.5 and 110 USD a share x 0.6), then a normal profit of 65 USD x 12, all at 11%. Mixed 50% with Morningstar (30%) and Goldman's 1,250 USD target (20%), which already uses normal profit.
- SpaceX: three scenarios (bad 32 USD 30%, base 107 USD 50%, good 260 USD 20%), mixed 45% with Morningstar 45% and the bank average 10%.

In fair_inputs.csv I then set the DCF growth so the site shows this fair price. The growth it needs is a sanity check: if it looks impossible, the fair price is wrong.

| Company | DCF | Morningstar | P/E view | Banks x 0.92 | Fair (USD) | Buy big at | Growth needed |
|---|---|---|---|---|---|---|---|
| Microsoft | 510 | 600 | 638 | 561 | 575 | 489 | 16.2% |
| Alphabet | 278 | 450 | 301 | 373 | 355 | 302 | 18.5% |
| Amazon | 215 | 280 | 293 | 301 | 265 | 225 | 21.9% |
| Meta | 500 | 850 | 666 | 764 | 690 | 587 | 16.9% |
| Apple | 214 | 290 | 277 | 310 | 270 | 230 | 12.2% |
| IBM | 263 | 260 | 249 | 244 | 255 | 216 | 4.4% |
| Micron | cycle 782 | 700 | - | Goldman 1,150 | 830 | 704 | 12.9% |
| SpaceX | scenarios 115 | 70 | - | 212 | 105 | 89 | 32.7% |

Full write-up with sources: the Claude doc "Prioridades máximas: valor justo empresa a empresa".

Review these numbers after each company's next results (most report late January 2027; Micron in December).

## The 12 stocks I already own (same method, 12 Nov 2026, 22h)

Where Morningstar has no public value (Vertiv, Vistra) the other three pieces share the weight. No 15% cut on the P/E here. Nvidia uses 14 USD of profit, not Yahoo's 15.9 USD, which looks like the whole next fiscal year.

| Stock | Old fair | DCF | Morningstar | P/E view | Banks x 0.92 | New fair | Extra buy at | Growth needed |
|---|---|---|---|---|---|---|---|---|
| Nvidia | 175 | 204 | 310 | 448 | 301 | 305 | 259 | 17.5% |
| TSMC | 461 | 514 | 534 | 421 | 497 | 500 | 425 | 16.5% |
| ASML (EUR) | 1,522 | 1,560 | 1,800 | 1,805 | 1,840 | 1,740 | 1,479 | 17.0% |
| Broadcom | 386 | 407 | 650 | 488 | 485 | 510 | 434 | 16.2% |
| Vertiv | 253 | 259 | - | 270 | 313 | 275 | 234 | 19.2% |
| GE Vernova | 915 | 926 | 1,050 | 1,044 | 1,132 | 1,030 | 876 | 22.0% |
| Vistra | 137 | 144 | - | 173 | 220 | 175 | 149 | 9.5% |
| Mastercard | 650 | 661 | 550 | 719 | 635 | 630 | 536 | 12.1% |
| Eli Lilly | 1,420 | 1,497 | 980 | 1,923 | 1,224 | 1,370 | 1,164 | 17.3% |
| Safran (EUR) | 317 | 319 | 387 | 325 | 328 | 340 | 289 | 12.1% |
| ServiceNow | 119 | 153 | 200 | 216 | 132 | 175 | 149 | 19.5% |
| Intuitive Surgical | 354 | 357 | 378 | 750 | 478 | 465 | 395 | 20.9% |

Warning: this method gives higher values than my old DCF alone, because banks and past P/E come from years of AI euphoria. After the November fall, seven stocks look cheap at once. They all move together, extras stay at 200 € a month at most, and Nvidia waits for its 17 Nov results.

Full write-up with sources: the Claude doc "Carteira: valor justo empresa a empresa".

## Weights by type of company (12 Nov 2026, 22h30)

The weights now depend on the sector, the way analysts value each kind of business.

| Type | Companies | Weights |
|---|---|---|
| Stable and predictable | Mastercard, Apple, IBM, Safran | DCF 40%, Morningstar 30%, P/E 15%, banks 15% |
| Growth chips | Nvidia, TSMC, ASML, Broadcom | 30/30/20/20, past P/E capped at 30x (chips are cyclical) |
| Big cloud | Microsoft, Alphabet, Amazon, Meta | 30/30/20/20, P/E cut 15% for data centre spending |
| Short history or extreme P/E | GE Vernova, Intuitive Surgical | No P/E: DCF 35%, Morningstar 35%, banks 30% |
| No Morningstar | Vertiv | DCF 40%, P/E (max 30x) 30%, banks 30% |
| Pharma | Eli Lilly | No P/E (the obesity drug boom distorts it): DCF 40%, Morningstar 35%, banks 25% |
| Power producer | Vistra | Free cash flow 13.9 USD a share in 2027 (company guide 4.3 to 5.1 billion USD, 339 million shares) x 13.5, plus DCF on that cash, P/E and banks (30/30/20/20) |
| Software | ServiceNow | P/E capped at 35x |
| Cycle and new | Micron, SpaceX | Cycle model and scenarios |

Changes: Eli Lilly 1,370 to 1,250 (now 16% above fair: pause the plan), Intuitive 465 to 400, Vistra 175 to 190 (eps column now holds free cash flow a share, not compared with Yahoo), ASML 1,740 to 1,710 EUR, Nvidia 305 to 300, Vertiv 275 to 280, ServiceNow 175 to 165, Apple 270 to 260. The rest moved less than 1%.

## Stricter buying rules (12 Nov 2026, 23h)

A cheap price alone is not enough. Every buy needs at least two of three independent checks: Morningstar fair value above the price, forward P/E below the stock's own 5-year average (Yahoo), and banks' average target 15% or more above the price with an average rating of buy (Yahoo). Analysts must not be cutting their profit forecast by more than 10%, and there must be no results in the next 7 days. The columns morningstar and pe5y in fair_inputs.csv hold the first two; I update them in the reviews.

- My stocks: buy extra at 15% or more below fair, only if confirmed. Otherwise the status is CHEAP, NOT CONFIRMED and the plan just keeps going.
- Top priorities: start a plan at 10% below fair (margin of safety), buy big at 20% below, only if confirmed.
- Several cheap at once: the highest expected return goes first. 200 € a month is the cap.
- Keep, pause (above 110%) and sell part (above 150%) did not change.

## Intel (added 12 Nov 2026, 23h)

Turnaround, so no past P/E (it lost money in 2024 and 2025). DCF 35%, Morningstar 35%, banks 30%, discount 11%.
- DCF: 2027 profit 1.79 USD (analysts' normalized estimate, cut from 2.11 after the Q3 outlook) x 0.5 (heavy spending on factories) = 35
- Morningstar: 85 USD (4 stars, very high uncertainty, no moat)
- Banks: about 100 USD average x 0.92 = 92 (most rate it hold)
- Fair 70 USD; start plan at 63, buy big at 56. Price about 59 USD on 10 Nov.
- Checks: Morningstar yes; banks no (target is high but the average rating is hold); no past P/E. 1 of 2: not confirmed, so WAIT even though the price is in the zone.
