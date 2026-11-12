# Investment Policy Statement

My rules, written before investing. I change them in the quarterly review, or when a company passes a full written analysis.

## Money
- Emergency fund and the savings for my master's stay in cash, never in the portfolio
- Investing: a fixed amount every month with automatic plans on the 2nd. More when my salary goes up

## Targets
| Block | Product | ISIN | Target |
|---|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | IE00BK5BQT80 | 55% |
| Stock | Nvidia | US67066G1040 | 5% |
| Stock | TSMC (ADR) | US8740391003 | 5% |
| Stock | ASML | NL0010273215 | 5% |
| Stock | Broadcom | US11135F1012 | 4% |
| Stock | Vertiv | US92537N1081 | 4% |
| Stock | Mastercard | US57636Q1040 | 5% |
| Stock | Eli Lilly | US5324571083 | 5% |
| Stock | GE Vernova | US36828A1016 | 4% |
| Stock | Vistra | US92840M1027 | 3% |
| Stock | Safran | FR0000073272 | 5% |

Core 55%, stocks 45% in 10 companies (changed on 12 Nov 2026, see notes/2026-11-12_sixty_forty.md, notes/2026-11-12_safran.md and notes/2026-11-12_grid.md). I keep the Intuitive Surgical and ServiceNow shares and the gold I already bought, with no new money. The same list is in data/portfolio/products.csv, the limits are in data/portfolio/rules.csv and the assumptions behind each fair price are in data/portfolio/fair_inputs.csv.

## Why this mix
- VWCE is the default home for my money: thousands of companies from about 50 countries. Its weight is not fixed. It goes down when a good company reaches a good price and up when one gets expensive. It is at 55% today. It only goes below that to make room for one of my top priorities (see below), and never below 50% before the 2030 test
- Stocks only where the winner is clear and the price is fair or better. Nvidia makes most AI chips. TSMC makes the chips for everyone. ASML is the only maker of the machines TSMC needs. Broadcom makes custom AI chips. Vertiv makes the power and cooling gear inside data centers. Mastercard is half of a duopoly in card payments. Eli Lilly leads obesity and diabetes drugs. GE Vernova is one of three makers of big gas turbines and sells grid equipment. Vistra owns about 50 GW of power plants, including nuclear, and sells long contracts to data centers. Safran makes the engines of most single aisle jets with GE, plus landing gear and defense electronics, and earns for decades on the service of every engine.
- No small cap ETF: the extra return of small companies is weak unless you filter for quality (Asness and others, 2018), it costs more, and it is the opposite of what I look for in stocks
- No theme ETFs: specialised ETFs lost about 30% against the market in their first 5 years, mostly because the theme was already expensive when the ETF came out (Ben-David and others, 2023). If I like a theme I buy its best company at a fair price, or I wait
- VWCE and not the S&P 500 or the Nasdaq 100: my stocks are already mostly American tech
- No gold and no bonds for now: my cash savings play that role

## Rules
1. Invest every month, whatever the market does.
2. Never sell because prices fall. A 40% drop will happen. I keep buying.
3. A company first has to pass five tests: strong growth ahead, clearly beats its rivals, key sector, gives money back to shareholders, and a fair price. Price comes last.
4. One method for every company, weighted by the type of business (notes/2026-11-12_fair_values.md). The fair price mixes four views: my DCF (next year's profit per share times the share of it that becomes cash, 5 years of growth that then fades to 4%, discounted at 9%, 10% for cyclical and 11% for very risky companies), the Morningstar fair value, the profit times the stock's own 5-year average P/E, and the average bank target times 0.92. Stable companies lean on the DCF, chips cap the P/E at 30x, the big cloud companies cut it by 15%, GE Vernova, Intuitive and Eli Lilly skip it, Vistra uses free cash flow, Micron a cycle model and SpaceX scenarios. In fair_inputs.csv the growth is set so the site shows that fair price.
4b. The method and the buying rules are frozen until the review of 28 January 2027. Between reviews only the numbers change, after each company's results (profit, Morningstar, bank targets), always with the same method. An alarm means I review that company, not the method. Weights never change mid year. Changing the method every time a number looks wrong is how you end up seeing what you want to see.
5. A company enters at or below its entry price in data/portfolio/fair_inputs.csv. Once it is in, the monthly plan keeps going up to 10% above the fair price. Beyond that the plan pauses and the money goes to VWCE. I keep the shares.
6. Extra buys only when all of this is true: the price is 15% or more below the fair price; at least two of three independent checks agree (Morningstar fair value above the price, forward P/E below the stock's own 5-year average, banks' average target 15% or more above the price with an average rating of buy); analysts are not cutting their profit forecast by more than 10%; no results in the next 7 days; none of the company's alarms is on. If several qualify, the one with the highest expected return goes first. Up to 200 € a month, buys of 100 to 200 €, limit orders, from my personal budget, never from the savings for my master's. A stock without a monthly plan gets no extra buys.
7. Sell in two cases, never on the day of the bad news:
   - The business breaks: one of its alarms is confirmed (they are written in data/portfolio/fair_inputs.csv), or the screener shows two or more warning signs at once (quality below 4 out of 5, revenue falling, revenue lower than 3 years ago, debt above 4 times profits, more than 5% new shares a year). One sign alone means I look closer. Two mean I sell if the next results confirm them.
   - The price gets absurd: 50% or more above my fair price. Then the expected return is below what VWCE gives, so I sell up to half and move it to VWCE, if the gain after the 28% tax is worth it. I keep the other half, because a great business can stay expensive for years.
8. Each stock stays between 2% and 5% of the portfolio. Above 5% I stop buying it. Maximum 10 stocks with a plan, plus up to 4 of my top priorities (Micron, Microsoft, Alphabet, Apple, Amazon, SpaceX, Meta, IBM, Intel). A priority starts a plan only 10% or more below my fair price, and I buy big only 20% or more below it, both with the same checks as rule 6. No other stock has to leave: the money comes from VWCE.
9. No sector above 20% of the portfolio, counting only the stocks I pick (VWCE does not count). The sector of each stock is in data/portfolio/products.csv. When a sector is full, the next good company has to come from another sector. That keeps me looking at the whole economy, not only at what is in the news. On top of that, everything that depends on AI spending (chips, Micron, Vertiv, GE Vernova and Vistra, the ai column in products.csv) stays at or below 30%. Platform companies with many businesses (Microsoft, Alphabet, Apple, Amazon, Meta, IBM) go in their own sector, Big tech, and are not counted as AI. SpaceX goes in Space.
10. All stocks together stay at or below 45%, or 50% once a top priority has a plan.
11. Rules 8, 9 and 10 start after 6 months of buying (around April 2027): the one-off buy in Nov 2026 makes the first months look off.
12. The daily check (GitHub, every weekday after the US close) works out the fair prices and the alerts, and tells me when analysts change their profit forecasts by more than 15%. I read the alerts, I don't react to news.
13. Plans only change in the quarterly review, or when a watchlist company reaches its entry price and passes a full written analysis.
14. If I need money for my master's or a move: pause plans, never sell.
15. If I move country, check how it taxes ETFs and stocks before doing anything.
16. Three year test (January 2030): if my stocks together did worse than VWCE since I bought them, the stock block goes to VWCE. Most people who pick stocks end up below the market, and this tells me if I am one of them.

## Tax notes (Portugal)
- Accumulating ETFs: no tax until I sell
- Stocks: dividends are taxed every year (US withholding plus Portugal). Small amounts for these companies
- On sale: 28% on the gain, with 10%, 20% or 30% of the gain excluded after 2, 5 or 8 years
- Trade Republic is a foreign broker: sales and dividends go in Anexo J
- Gold ETC: may not get the 10/20/30% exclusion. Ask an accountant before selling
