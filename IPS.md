# Investment Policy Statement

My rules, written before investing. I only change them in the January review.

## Money
- Emergency fund and the savings for my master's stay in cash, never in the portfolio
- Investing: a fixed amount every month with automatic plans on the 2nd. More when my salary goes up

## Targets
| Block | Product | ISIN | Target |
|---|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | IE00BK5BQT80 | 60% |
| Small | iShares MSCI World Small Cap (IUSN) | IE00BF4RFH31 | 10% |
| Theme ETF | Xtrackers MSCI World Health Care (XDWH) | IE00BM67HK77 | 3% |
| Theme ETF | First Trust Smart Grid Infrastructure (GRID) | IE000J80JTL1 | 3% |
| Theme ETF | VanEck Uranium and Nuclear Technologies (NUKL) | IE000M7V94E1 | 2% |
| Stock | TSMC (ADR) | US8740391003 | 4% |
| Stock | Mastercard | US57636Q1040 | 4% |
| Stock | Broadcom | US11135F1012 | 3% |
| Stock | Nvidia | US67066G1040 | 3% |
| Stock | Safran | FR0000073272 | 3% |
| Stock | Eli Lilly | US5324571083 | 3% |
| Stock | Intuitive Surgical | US46120E6023 | 2% |

Base 70%, bets 30% (22% stocks, 8% theme ETFs). The same list is in data/portfolio/products.csv and the limits are in data/portfolio/rules.csv.

## Why this mix
- VWCE and IUSN are the safe part: thousands of companies from about 50 countries, big and small. Even if every bet goes wrong I stay close to the market
- Stocks only where the winner is clear: almost no competition, top quality in the screener, growing, and at a fair price. TSMC makes the chips for everyone. Mastercard is half of a duopoly in card payments. Broadcom makes custom AI chips and optical links. Nvidia makes most AI chips. Safran makes half of the engine on most single aisle planes and earns for decades on parts and repairs. Eli Lilly shares the market for obesity and diabetes drugs with Novo Nordisk. Intuitive Surgical leads robotic surgery
- Theme ETFs where the theme is clear but the winner is not: health and biotech, power grid, nuclear
- Safran and Eli Lilly came in because my stocks were almost all AI chips and all in dollars. Safran is in euros and doesn't depend on AI, Lilly is health with real growth
- No quantum ETF for now: most pure quantum companies lose money and trade at many times their sales. I follow the sector in the screener and look again every January. It comes back if some of them make a profit or prices fall to normal levels
- Weights mix a portfolio optimizer (portfolio/optimize.py) with the quality of each company. TSMC and Mastercard get more: TSMC wins whoever wins in AI, Mastercard is the calmest stock and moves differently from chips. Intuitive gets less until its January test
- No gold: it earns about 1.5% a year above inflation against about 8% for stocks. I keep the small amount I bought in Nov 2026
- No bonds for now: my cash savings play that role

## Rules
1. Invest every month, whatever the market does.
2. Never sell because prices fall. A 40% drop will happen. I keep buying.
3. Each bet stays between 2% and 5% of the portfolio. Below 2% it doesn't change anything, so it's not worth having. Above 5% I stop buying it and its plan goes to VWCE. I don't sell to fix it.
4. All bets together stay at or below 30%. Above that, new money goes to VWCE.
5. Rules 3, 4 and 15 start after 6 months of buying (around April 2027): the one-off stock buy in Nov 2026 makes the first months look off.
6. Sell or replace a stock only if the business gets worse: quality below 4 out of 5, revenue lower than 3 years ago, debt above 4 times profits, or more than 5% new shares a year. Then I decide in January, not on the day.
7. Extra buys only when the weekly check says a stock is below its careful fair price (method in notes/2026-11_fair_price_method.md), at least 50 EUR, from my personal budget, never from the savings for my master's.
8. A watchlist company only comes in if it is clearly better than my weakest stock, and only in January. Maximum 7 stocks: more than that and I can't follow them properly.
9. The weekly check (GitHub, every Monday) runs the screener and the alerts. I read the alerts, I don't react to news.
10. No changes because of videos, news, social media or other AIs. New ideas wait for January.
11. If I need money for my master's or a move: pause plans, never sell.
12. If I move country, check how it taxes ETFs and stocks before doing anything.
13. A stock above its optimistic fair price is EXPENSIVE: no extra buys, its plan keeps going and I look at it in January.
14. Three year test (January 2030): if my stocks together did worse than VWCE since I bought them, the stock block goes to VWCE. Most people who pick stocks end up below the market, and this tells me if I am one of them.
15. Stocks that depend on the same thing count as one bet. TSMC, Broadcom and Nvidia (AI chips) stay under 12% together. Above that, no extra buys in the group.

## Tax notes (Portugal)
- Accumulating ETFs: no tax until I sell
- Stocks: dividends are taxed every year (US withholding plus Portugal). Small amounts for these companies
- On sale: 28% on the gain, with 10%, 20% or 30% of the gain excluded after 2, 5 or 8 years
- Trade Republic is a foreign broker: sales and dividends go in Anexo J
- Gold ETC: may not get the 10/20/30% exclusion. Ask an accountant before selling
