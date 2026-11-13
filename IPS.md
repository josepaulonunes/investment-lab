# Investment Policy Statement

My rules, written before investing. I change them in the quarterly review, or when a company passes a full written analysis.

## Money
- Emergency fund and the savings for my master's stay in cash, never in the portfolio
- Investing: a fixed amount every month with automatic plans on the 2nd. More when my salary goes up
- Extra buys: up to 200 € a month from my personal budget. What I do not use stays in cash for the next good price

## Targets
The ideal mix is where I want to be. Today's plan is what the prices allow: a stock that is above its fair price waits, and its money stays in VWCE.

| Sector | Product | Ideal | Today (13 Nov 2026) |
|---|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | 52% | 62% |
| Chips and AI | Nvidia | 5% (up to 10% with extra buys) | 5% |
| Chips and AI | TSMC (ADR) | 5% | 5% |
| Chips and AI | ASML | 5% | 5% |
| Chips and AI | Broadcom | 4% | 4% |
| Power and grid | Vertiv | 4% | 4% |
| Power and grid | GE Vernova | 4% | 4% |
| Power and grid | Vistra | 3% | 3% |
| Payments | Mastercard | 5% | paused |
| Health | Eli Lilly | 5% | paused |
| Aerospace | Safran | 5% | 5% |
| Big tech | Alphabet | 3% | 3% |

Core 52%, stocks 48% in 11 companies I know and trust. I keep the Intuitive Surgical and ServiceNow shares and the gold I already bought, with no new money. The same list is in data/portfolio/products.csv (ideal, target and max columns), the limits and the numbers of the method are in data/portfolio/rules.csv and the assumptions behind each fair price are in data/portfolio/fair_inputs.csv. Why: notes/2026-11-13_my_companies.md.

## My priorities (the companies I want to own one day)
- Magnificent 7: Microsoft, Amazon, Meta, Apple, Tesla (Alphabet and Nvidia are already in)
- Chips: AMD, Micron, Intel
- Cybersecurity: CrowdStrike, Palo Alto Networks, Zscaler, Fortinet
- Quantum: IBM (Alphabet and Microsoft also lead here). Pure quantum names like IonQ have no profit, so my method cannot value them
- Remote work: Zoom (Microsoft and ServiceNow already cover the rest)
- AI: Palantir
Each one starts a plan of 3% when its price is at or below my fair price, its alarm is off and analysts are not cutting profits. The money comes from VWCE, never below 50%.

## Why this mix
- VWCE is the base of my money: thousands of companies from about 50 countries. It never goes below 50%
- Stocks only in companies I know, trust and would keep for 10 years. I do not add a new company in one evening because a model says so: a new name needs a written analysis first
- Nvidia is my strongest conviction. When it is really cheap (35% below my fair price, because it is very hard to value) and its alarm is off, I can buy more, up to 10% of the portfolio
- Sectors I believe in for the long run: chips and AI, power for data centers, payments, health, aircraft engines and big tech
- No small cap ETF and no theme ETFs (Asness and others, 2018, Ben-David and others, 2023)
- No bonds for now: my cash savings play that role. Bitcoin is optional and small (see notes/2026-11-13_method_and_portfolio.md)

## Rules
1. Invest every month, whatever the market does.
2. Never sell because prices fall. A 40% drop will happen. I keep buying.
3. A company first has to pass five tests: proven business with strong growth ahead, clearly beats its rivals, key sector, gives money back to shareholders, and a price below fair. Price comes last.
4. One method for every company (future/fair_price.py). The fair price is 60% my own DCF and 40% the Morningstar fair value (my DCF alone when Morningstar does not cover the company).
   - Cash: the analysts' profit per share for next year, read from Yahoo on every check, times the share of it that becomes free cash. My saved number is used for cycle companies and when Yahoo is more than 30% away from it.
   - Growth: my number for years 2 to 5, never above 15%, then it falls to 4% in year 10 and 2.25% after that.
   - Rate: the US 10 year yield (3 month average) plus 4.25% for normal businesses, 5.25% for cyclical ones and 6.25% for very risky ones.
   - Banks' price targets and past P/E are not in the fair price: they follow the price instead of leading it.
5. Three things move a stock and each one has its place in the method. The company: the analysts' profit updates the fair price every day, and a cut of more than 10% in 3 months stops every buy. The economy: the 10 year yield moves the rate I ask for. Politics and rules: each company has written alarms (data/portfolio/fair_inputs.csv). I switch an alarm on by hand (alarm_on) and it stops every buy of that company until two clean results.
6. Zones, for every company:
   - A stock of my ideal mix starts its plan when its price is at or below fair, if its alarm is off and analysts are not cutting profits. These companies already passed my tests, so I do not ask for a discount to start. At fair I earn the rate I ask for (about 9%), with no room for my own mistakes. Until then it waits and its money stays in VWCE.
   - Once I own it, the plan keeps going up to 10% above fair. Beyond that it pauses and the money goes to VWCE. I keep the shares.
   - Extra buys need the full margin of safety: 15% below fair for companies that are easy to value, 25% for hard ones, 35% for very hard ones (Morningstar's uncertainty rating).
   - 50% or more above fair: I sell up to half, if the gain after the 28% tax is worth it.
7. Every extra buy, and every company that comes from the watchlist, needs two of three checks: Morningstar above the price, my own DCF above the price, analysts not cutting profits in the last 3 months. Plus: no results in the next 7 days, alarm off, no warning sign in the screener. A company with only one check available cannot be bought yet. If several qualify, the one furthest below its own buying price goes first. Up to 200 € a month, buys of 100 to 200 €, limit orders.
8. Sell in two cases, never on the day of the bad news:
   - The business breaks: one of its alarms is confirmed by the next results, or the screener shows two or more warning signs at once.
   - The price gets absurd: 50% or more above my fair price (rule 6).
9. Each stock stays between 2% and 5% of the portfolio, except Nvidia, which can go up to 10%. Maximum 15 stocks with a plan.
10. No sector above 25% of the portfolio, counting only the stocks I pick. Everything that depends on AI spending (the chips, Vertiv, GE Vernova, Vistra, the big tech names, ServiceNow) stays at or below 40%. I know this is a big bet on AI: it is my choice and VWCE is the safety net.
11. All stocks together stay at or below 50%.
12. Rules 9, 10 and 11 start after 6 months of buying (around April 2027).
13. The daily check (GitHub, every weekday after the US close) works out the fair prices and the alerts. I read the alerts, I don't react to news.
14. The Morningstar values are typed by hand with their date. The check tells me when one is more than 3 months old. After each company's results I update it.
15. The method is frozen until the review of 28 January 2027, and after that I only change it in the January review of each year. Between reviews only the inputs change. I changed the method three times on 12 November 2026 and every change made my stocks look cheaper. That is how you end up seeing what you want to see.
16. If I need money for my master's or a move: pause plans, never sell.
17. If I move country, check how it taxes ETFs and stocks before doing anything.
18. Three year test (January 2030): if my stocks together did worse than VWCE since I bought them, the stock block goes to VWCE.

## How I protect the money
- The money I may need in the next 3 years is not here
- 50% or more in VWCE, no stock above 5% (Nvidia 10%), no sector above 25%
- A stock only starts at or below fair, I never add above 110% of fair, and extra money only goes in with a real discount
- No debt, no options, no leveraged products
- In a crash nothing changes in the plans. The unused extra money is there to buy what reaches its margin of safety

## Tax notes (Portugal)
- Accumulating ETFs: no tax until I sell
- Stocks: dividends are taxed every year (US withholding plus Portugal). Small amounts for these companies
- On sale: 28% on the gain, with 10%, 20% or 30% of the gain excluded after 2, 5 or 8 years
- Trade Republic now has a Portuguese branch that withholds tax: check which annex applies before the next IRS
- Bitcoin held directly for 365 days or more: the gain is not taxed, but the sale is declared. A Bitcoin ETP is a security and pays the 28%
- Gold ETC: ask an accountant before selling
