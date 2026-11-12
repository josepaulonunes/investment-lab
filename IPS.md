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
- VWCE is the default home for my money: thousands of companies from about 50 countries. Its weight is not fixed. It goes down when a good company reaches a good price and up when one gets expensive. It is at its floor of 55% and never goes below it before the 2030 test
- Stocks only where the winner is clear and the price is fair or better. Nvidia makes most AI chips. TSMC makes the chips for everyone. ASML is the only maker of the machines TSMC needs. Broadcom makes custom AI chips. Vertiv makes the power and cooling gear inside data centers. Mastercard is half of a duopoly in card payments. Eli Lilly leads obesity and diabetes drugs. GE Vernova is one of three makers of big gas turbines and sells grid equipment. Vistra owns about 50 GW of power plants, including nuclear, and sells long contracts to data centers. Safran makes the engines of most single aisle jets with GE, plus landing gear and defense electronics, and earns for decades on the service of every engine.
- No small cap ETF: the extra return of small companies is weak unless you filter for quality (Asness and others, 2018), it costs more, and it is the opposite of what I look for in stocks
- No theme ETFs: specialised ETFs lost about 30% against the market in their first 5 years, mostly because the theme was already expensive when the ETF came out (Ben-David and others, 2023). If I like a theme I buy its best company at a fair price, or I wait
- VWCE and not the S&P 500 or the Nasdaq 100: my stocks are already mostly American tech
- No gold and no bonds for now: my cash savings play that role

## Rules
1. Invest every month, whatever the market does.
2. Never sell because prices fall. A 40% drop will happen. I keep buying.
3. A company first has to pass five tests: strong growth ahead, clearly beats its rivals, key sector, gives money back to shareholders, and a fair price. Price comes last.
4. One method for every company (future/fair_price.py): next year's profit per share times the share of it that becomes cash, 5 years of growth that then fades to 4%, discounted at 9% (10% for cyclical or riskier companies). I also work out the yearly return the price gives me. I ask for at least 9%.
5. A company enters at or below its entry price in data/portfolio/fair_inputs.csv. Once it is in, the monthly plan keeps going up to 10% above the fair price. Beyond that the plan pauses and the money goes to VWCE. I keep the shares.
6. Extra buys only when the price is 15% or more below the fair price and none of the company's alarms is on. From my personal budget, never from the savings for my master's.
7. Sell in two cases, never on the day of the bad news:
   - The business breaks: one of its alarms is confirmed (they are written in data/portfolio/fair_inputs.csv), or the screener shows two or more warning signs at once (quality below 4 out of 5, revenue falling, revenue lower than 3 years ago, debt above 4 times profits, more than 5% new shares a year). One sign alone means I look closer. Two mean I sell if the next results confirm them.
   - The price gets absurd: 50% or more above my fair price. Then the expected return is below what VWCE gives, so I sell up to half and move it to VWCE, if the gain after the 28% tax is worth it. I keep the other half, because a great business can stay expensive for years.
8. Each stock stays between 2% and 5% of the portfolio. Above 5% I stop buying it. Maximum 10 stocks with a plan, so a new one only comes in when another leaves.
9. No sector above 20% of the portfolio, counting only the stocks I pick (VWCE does not count). The sector of each stock is in data/portfolio/products.csv. When a sector is full, the next good company has to come from another sector. That keeps me looking at the whole economy, not only at what is in the news. On top of that, everything that depends on AI (chips, Vertiv, GE Vernova and Vistra, the ai column in products.csv) stays at or below 30%.
10. All stocks together stay at or below 45%.
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
