# 13 Nov 2026: new fair price method, new rules, new mix

I asked for a full review of the method, the fair prices, the rules and the portfolio. This note is the result. It replaces the method of 12 Nov (notes/2026-11-12_fair_values.md).

## What was wrong
1. The DCF counted one year of growth too many. The profit I typed was already the next 12 months, and the code grew it again in year 1. Every DCF was too high by one year of growth: 12% for Mastercard, 22% for GE Vernova.
2. The growth in fair_inputs.csv was not an assumption. I picked it so the DCF would show the fair price I already had. So the "expected return" was not a return, it was the same number seen from the other side.
3. Only 30% to 40% of the fair price was mine. The rest was Morningstar, the banks' targets and the past P/E, and all of them start from the same analyst profit. Banks' targets and past P/E follow the price: after years of AI euphoria they pushed every fair price up.
4. The three "independent checks" used the same three inputs as the fair price, so they almost never said no. On 12 Nov six stocks were BUY EXTRA at once, all in AI.
5. The stocks were ranked by expected return, and a stock at its fair price returns its own discount rate. So the riskier stocks (10% and 11%) always came first.
6. The alarms were only text. Nothing in the code stopped a buy when one was on. Nvidia would have turned into BUY EXTRA the day after its results, with no permanent CEO.
7. The "analysts cutting profits" check compared Yahoo with the number I had just typed from Yahoo. Intel's forecast was cut 15% and the check showed 0%.
8. The Morningstar values were old: Nvidia 310 (now 250), ServiceNow 200 (now 100), IBM 260 (now 230).
9. I changed the method three times in one evening, the day after the market fell, and every change made my stocks look cheaper: Nvidia from 175 to 305, Broadcom from 386 to 510. Then I froze it. My own DCF said only TSMC, Vertiv and Nvidia were 15% below fair.
10. 30% of the portfolio was one bet. Chips, Vertiv, GE Vernova and Vistra all live on data center spending.

## The new method
Fair price = 60% my own DCF + 40% the Morningstar fair value. My DCF alone if Morningstar does not cover the company.

My DCF updates by itself on every check:
- Profit: the analysts' profit per share for next year, from Yahoo. When a company earns more or less, the fair price moves the same day. My saved number is only used for cycle companies (Micron, Vistra) or when Yahoo is more than 30% away from it.
- Cash: profit times the share that becomes free cash (conversion). I only change it in the reviews.
- Growth: my number for years 2 to 5, never above 15%. Very few big companies grow faster than that for 5 years (Mauboussin, Chan and others). If a price needs more than 15%, the company waits. Then growth falls to 4% in year 10 and 2.25% after.
- Rate: the US 10 year yield, 3 month average, plus 4.25% (normal), 5.25% (cyclical) or 6.25% (very risky). With the yield near 4.9% that is 9.15%, 10.15% and 11.15%. When rates go up, every fair price goes down by itself.

Morningstar is typed by hand with its date. It is the only outside opinion I keep, because it is a long term DCF made by someone who does not earn more when I buy. The check tells me when a value is more than 3 months old.

Out of the fair price: banks' targets and the past P/E.

The margin of safety depends on how hard the company is to value (Morningstar's uncertainty rating): 15% for medium, 25% for high, 35% for very high.

## Each fair price (prices of 12 Nov 2026, yield 4.9%)
| Company | Price | Profit | Cash share | Growth | Rate | My DCF | Morningstar | Fair | Price vs fair | State |
|---|---|---|---|---|---|---|---|---|---|---|
| Broadcom | 364 | 19.47 | 0.90 | 15% | 10.15% | 406 | 650 | 504 | -28% | BUY EXTRA |
| Nvidia | 166 | 15.91 | 0.70 | 10% | 10.15% | 206 | 250 | 224 | -26% | Keep, alarm on |
| ResMed | 239 | 13.23 | 0.95 | 9% | 9.15% | 257 | 300 | 274 | -13% | Plan starts |
| Alphabet | 299 | 15.44 | 0.60 | 13% | 9.15% | 228 | 450 | 317 | -6% | Plan starts |
| ASML (EUR) | 1,404 | 56.43 | 0.87 | 12% | 9.15% | 1,155 | 1,800 | 1,413 | -1% | Plan starts |
| TSMC | 405 | 23.39 | 0.62 | 14% | 10.15% | 321 | 534 | 406 | 0% | Keep buying |
| Safran (EUR) | 312 | 12.51 | 0.93 | 11% | 9.15% | 261 | 378 | 308 | +1% | Wait (308) |
| Meta | 624 | 35.59 | 0.55 | 12% | 9.15% | 460 | 850 | 616 | +1% | Wait, alarm on |
| Schneider (EUR) | 245 | 12.59 | 0.90 | 9% | 9.15% | 232 | 250 | 239 | +2% | Wait (239) |
| GE Vernova | 818 | 26.06 | 1.00 | 15% | 10.15% | 604 | 1,050 | 782 | +5% | Wait (782) |
| Microsoft | 523 | 24.20 | 0.70 | 13% | 9.15% | 417 | 600 | 490 | +7% | Wait (490) |
| ServiceNow | 101 | 4.80 | 0.80 | 15% | 10.15% | 89 | 100 | 93 | +8% | Keep the shares |
| S&P Global | 469 | 20.18 | 1.00 | 10% | 9.15% | 433 | 525 | 470 | 0% | At its start price (470) |
| Mastercard | 653 | 23.16 | 1.00 | 12% | 9.15% | 545 | 550 | 547 | +19% | Pause |
| Amazon | 267 | 10.90 | 0.50 | 15% | 9.15% | 147 | 280 | 200 | +34% | Wait |
| Intuitive Surgical | 440 | 12.47 | 0.85 | 14% | 9.15% | 273 | 378 | 315 | +40% | Keep the shares |
| Eli Lilly | 1,427 | 50.64 | 0.75 | 15% | 9.15% | 1,025 | 980 | 1,007 | +42% | Wait (1,007) |
| Apple | 355 | 10.55 | 1.00 | 9% | 9.15% | 216 | 290 | 246 | +44% | Wait |

The number in brackets is the price where the plan starts: the fair price. I do not ask for a discount to start a company that already passed my tests, only for extra buys.

How I got to each growth and cash number:
- Broadcom: Morningstar models 40% revenue growth to 2030. I stop at my 15% cap and let Morningstar's 650 carry the rest. Cyclical rate because a few customers are most of its AI sales and it has debt. It is the only stock below its margin of safety today.
- Nvidia: 10%, not more. Revenue grew 65% last year, which is the top of a cycle, and the founder left on 12 Nov. Morningstar cut its value from 310 to 250 that day and calls the uncertainty very high, so I ask for 35% below fair before any extra buy. Alarm on.
- ResMed: guides to 12 to 14% profit growth with 6 to 8% revenue growth, so 9%. Net cash, 34% operating margin, masks and supplies that customers reorder. Morningstar 300.
- Alphabet, Microsoft, Meta, Amazon: 12 to 15%. The cash share is low (0.5 to 0.7) because data center spending eats the profit. That is why my DCF is far below Morningstar for all four.
- ASML: 12%. Sales guided to 44 to 45 billion in 2026 from 32.7, but the business moves in cycles, so I take the middle of the cycle. Normal rate: it is a monopoly with net cash.
- TSMC: 14% (2026 revenue guided above 40%, 2 nm ramp). Cash share 0.62 because it spends 62 billion a year on factories. Cyclical rate for Taiwan.
- Safran: 11%. Morningstar had 387 in August and cut it 2.3% on 30 Oct for higher capital spending, so I use 378. It expects operating profit to grow about 15% a year to 2028, I take less. Free cash of 4.7 to 4.9 billion on 414 million shares is close to the profit, so 0.93.
- Schneider Electric: 9%. Organic growth guided at 8 to 10%. Wide moat, medium uncertainty. I watch the debt after the 22.6 billion PTC deal.
- GE Vernova: capped at 15%, though profit should grow much faster for two years. The cash share of 1.0 is generous: today's cash comes from customer down payments. Very high uncertainty.
- S&P Global: 10% (revenue up 7 to 8%, buybacks add the rest). Morningstar 525, with low uncertainty. It is right at its fair price: if the daily check says PRIORITY START PLAN, it gets its 3%.
- Mastercard: 12%. My DCF (545) and Morningstar (550) agree, and the price is 19% above both. Great business, not a great price. Visa is in the same place (363 against 420).
- Eli Lilly: capped at 15%, cash share 0.75 while it builds factories. Both my DCF and Morningstar say about 1,000 against 1,427.
- Intuitive Surgical and ServiceNow: I keep the shares. Intuitive is 40% above fair (sell part above 473). ServiceNow is near fair after Morningstar cut it to 100.
- Apple: 9% (Morningstar projects 8% revenue growth). 44% above fair.

The watchlist uses the same method with my old growth numbers cut to 15%. I have not studied each one again, so those fair prices are rough.

## The mix
Ideal: VWCE 60%, stocks 40%.

| Sector | Stocks | Ideal |
|---|---|---|
| Chips and AI | TSMC 5, ASML 4, Broadcom 3, Nvidia 2 | 14% |
| Grid | Schneider Electric 3, GE Vernova 3 | 6% |
| Health | ResMed 3, Eli Lilly 3 | 6% |
| Payments and data | Mastercard 4, S&P Global 3 | 7% |
| Aerospace | Safran 4 | 4% |
| Big tech | the first to reach its start price | 3% |

Today: VWCE 80%, TSMC 5%, ASML 4%, Broadcom 3%, ResMed 3%, Alphabet 3%, Nvidia 2%. The others wait for their fair price and their money stays in VWCE. Safran, Meta, Schneider and GE Vernova are less than 5% away. Alphabet takes the big tech place, so Meta and Microsoft stay out.

What changed and why:
- Vistra out. A power producer earns what the power price and the Texas rules let it earn, and it has a lot of debt. Its "free cash before growth" is not free cash. It fails the test of a business an average boss could run.
- Vertiv to the watchlist. It is one more bet on data center spending, it is at its fair price, and Morningstar does not cover it, so I have no second opinion.
- Schneider Electric in for the grid: a proven leader in electrical equipment, in euros, with buildings and industry next to data centers. GE Vernova stays as the direct bet on turbines and grid gear, at 3%.
- ResMed in for health at a price below fair. Eli Lilly stays in the ideal mix but 42% above fair.
- S&P Global next to Mastercard: credit ratings and indexes are as close to a toll road as a business gets.
- Nvidia from 5% to 2%. It is the one company on my list that depended on one person.
- Big tech counts as AI (their spending is the AI cycle). Only one of them comes in: Alphabet, the first at its fair price. Its fair price leans on Morningstar (450): my own DCF says 228.
- Micron, Intel, SpaceX and IBM go from top priorities to the watchlist. Micron is at the top of a cycle with no moat, Intel lost money in 2024 and 2025, SpaceX needs more than 15% growth for many years, IBM grows 5%.

AI in the ideal mix: 14% chips + 3% GE Vernova + 3% big tech = 20% (limit 25%). It was 30%.

## What I do now
1. Plans from 2 Dec: VWCE 80%, TSMC 5%, ASML 4%, Broadcom 3%, ResMed 3%, Alphabet 3%, Nvidia 2%.
2. Extra buy on the 22nd: Broadcom only (100 to 200 €, limit order). Its results are on 9 Dec, more than 7 days away.
3. When Safran, Schneider or GE Vernova reach their fair price, the check says PRIORITY START PLAN: I move the company to the portfolio list and give it its ideal weight.
4. The Morningstar values were checked on 13 Nov against its public articles. Two are still open: GE Vernova (1,050 from July, the October value is not public) and Intuitive Surgical (378, no public article found). Meta's alarm is on: it sold 25 billion dollars of new shares to pay for AI, which is one of its alarms.
5. Nvidia: read the results of 17 Nov. The alarm stays on until there is a permanent CEO and two clean quarters.

## Bitcoin
My method cannot value Bitcoin: it has no profit and no cash flow, so there is no fair price, no margin of safety and no alarm to read. What I can say:
- The case for it: 21 million coins at most (20.1 million already exist), no company or state behind it, spot ETFs since 2024 made it easy for big investors to hold. If it keeps taking a part of the role of gold, the price is much higher in 10 years.
- The case against: nothing anchors the price. It has lost 70 to 85% several times. It fell with tech stocks this week, so it does not protect me in a crash. It pays nothing. Its future depends a lot on what governments decide.
- Today: about 72,000 dollars, 28% below a year ago and 43% below its high of 126,200.

If I want it, the only honest way is a size where being wrong does not matter:
- 2% of the monthly money, taken from VWCE, on an automatic plan. Never an extra buy, never more because it fell or rose.
- It never counts as protection, and it is not part of the stock rules: its only limit is its own size.
- If it grows above 5% of the portfolio, I stop its plan. Above 8%, I sell down to 5%.
- I hold the coin itself, not an ETP. In Portugal the gain on a coin held 365 days or more is not taxed (each monthly buy has its own clock, first in first out). An ETP is a security and pays 28%.
- I decide once and review it only in January. Minimum horizon 10 years. If I cannot watch it fall 80% without selling, the right size is 0%.
To switch it on: add a line to products.csv (block crypto, ticker BTC-EUR, target 2, ideal 2) and take 2 points from VWCE.

## Sources
- Morningstar notes of 2026 for each company (fair values and uncertainty ratings)
- Nvidia press release, 12 Nov 2026 (CEO transition)
- US Treasury, 10 year yield (4.86% on 6 Nov 2026)
- Mauboussin, Callahan and Majd, The Base Rate Book, 2016
- Chan, Karceski and Lakonishok, The Level and Persistence of Growth Rates, 2003
- Fortune, price of Bitcoin, 12 Nov 2026
- Código do IRS, artigo 10.º (crypto held 365 days or more)
