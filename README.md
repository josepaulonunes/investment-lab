# Investment Portfolio

My own investment tools in Python: a live dashboard of my portfolio, a screener that looks for companies with almost no competition at a fair price, and a daily check that tells me when to buy more, stop buying or look closer.

## The plan
| Block | What | Ideal | Today |
|---|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | 50% | 62% |
| Stocks | Nvidia 5%, TSMC 5%, ASML 5%, Broadcom 4%, Vertiv 4%, GE Vernova 4%, Vistra 3%, Mastercard 5%, Eli Lilly 5%, Safran 5%, Alphabet 3% | up to 50% | 38% |

About half follows the whole market. The other half is for 11 companies I know and trust: chips and AI, power for data centers, payments, health, aircraft engines and big tech. A stock gets money only when its price is at or below my fair price, so today Mastercard and Eli Lilly wait and their money stays in VWCE. My chips and big tech names can grow with extra buys when they are really cheap: up to 7% each, Nvidia up to 10%. Every company has its own file on the site: how I value its type of business, what it could be worth in 5 years, what could push it up and what could break it. My next companies are the Magnificent 7, chips, cybersecurity, quantum, remote work and AI leaders (the priorities tab). The rules are in IPS.md and the reasons in notes/2026-11-13_my_companies.md.

## How I pick the stocks
1. A list of about 180 companies in AI, chips, energy, health, payments, aviation, defense and more (data/future/universe.csv)
2. The screener scores each one: quality (growth, margin, cash, debt, return on equity), moat and future (my own scores) and the long run. I use it to find candidates and to watch the health of the business
3. For the ones I own or want, I write down my own assumptions in data/portfolio/fair_inputs.csv: how much of the profit becomes cash, growth for years 2 to 5 (never above 15%), how risky the business is, how hard it is to value, the Morningstar fair value with its date, and the alarms
4. future/fair_price.py turns that into a fair price every day: 60% my own DCF and 40% Morningstar. The DCF reads the analysts' profit for next year and the US 10 year yield from Yahoo, so the fair price follows the business and the economy without me touching it
5. A company only comes in if it passes my five tests (proven growth, beats its rivals, key sector, pays shareholders, price below fair) and I have written the analysis

## The daily check
Every weekday after the US market closes, GitHub runs the screener, the fair prices and future/alerts.py. If the alerts are different from the last check it opens an issue and I get a notification. Every stock I own gets one line:
- BUY EXTRA: below its margin of safety (15%, 25% or 35% below fair, the harder to value the bigger) and two checks agree. A one-off buy makes sense
- KEEP: up to 10% above fair. The monthly plan keeps going
- PAUSE: more than 10% above fair. Its plan goes to VWCE and I keep the shares
- SELL PART: 50% or more above fair. I sell up to half and move it to VWCE
- ALARM: I switched its alarm on by hand. No buys until two clean results
- PROFIT CUT: analysts cut next year's profit by more than 10% in 3 months. No buys until I read why
- REVIEW: one warning sign in the business (quality, revenue, debt, new shares). I look closer
- SELL: two or more warning signs at once. If the next results confirm them, I sell
- STOP BUYING: a stock is above 5% of the portfolio (7% for TSMC, ASML, Broadcom and Alphabet, 10% for Nvidia), one sector is above 30% (VWCE does not count), everything linked to AI is above 45%, or all stocks are above 50%

For the companies that wait:
- PRIORITY START PLAN: one of the stocks of my ideal mix is at or below fair, its alarm is off and analysts are not cutting profits. Its plan starts
- PRIORITY BUY BIG: it is below its full margin of safety. I also buy with the extra money
- PRIORITY CLOSE: less than 5% above its start price
- BUY: a watchlist company reached its start price. Time to write the full analysis

To keep the fair prices fresh:
- REVIEW MORNINGSTAR: the Morningstar value I typed has no date or is more than 3 months old
- REVIEW ASSUMPTION: Yahoo's profit number is more than 30% away from the one I saved, so I read why before the check uses it
- RESULTS: one of my stocks reports in the next 7 days

I never sell just because the price fell.

## The dashboard
`python -m streamlit run portfolio/dashboard.py` opens five tabs:
- Portfolio: value vs money invested, what I own, gain per product and per month
- Monthly plan: where each euro goes today, the ideal weight of each stock, and every limit (sector, AI, stocks)
- Fair prices: price vs my fair price (my DCF and Morningstar) for my stocks and the ones that wait, with the start and extra buy price of each
- DCF lab: pick a company and move the sliders (profit, cash, growth, rate) to see how the fair price changes, plus a heat map of what happens if I am wrong
- Alerts and TR levels: this week's alerts and the euro prices to set as alerts on Trade Republic

## What's inside
| Folder | What it does |
|---|---|
| portfolio/ | Dashboard (Streamlit), positions vs targets, optimizer, public data |
| future/ | Screener, fair prices and daily alerts |
| companies/ | Valuation model for any company: ratios, DCF, reverse DCF, sensitivity, peers |
| data/ | Inputs and outputs |
| notes/ | My decisions, written before deciding |
| archive/ | Old versions of the project, kept as a record. Not used anymore |

## Old versions (archive/)
These are tools I used before the current plan. I keep them to see how my thinking changed, but nothing in the plan or the daily check uses them:
- archive/companies/screener.py: my first screener, with a fixed 9% discount rate and its own watchlist. Replaced by future/future_screen.py
- archive/house_view/: scored regions by valuation and momentum. I used it in October 2026 when I was choosing country ETFs. I dropped country ETFs on 29 Oct 2026 (notes/2026-10_plan_change.md)
- archive/companies/prysmian_first_look.py: a first quick look at Prysmian before the full valuation model

Their data is in archive/data/. They still run from the main folder if I want to look again.

## How to run
My real purchases are private. The live app shows my real portfolio scaled so that all the money I put in adds up to 100: you see weights and returns, not amounts.

Easiest way: open the repo in GitHub Codespaces. The packages install on their own (.devcontainer/). Locally:

    pip install -r requirements.txt
    python -m streamlit run portfolio/dashboard.py
    python future/future_screen.py
    python future/fair_price.py
    python future/alerts.py
    python portfolio/optimize.py

Once a month, after the plans buy on the 2nd:

    python portfolio/add_month.py

It adds that month's plan purchases to my private file (at the closing price of the plan day) and updates the public file for the live app.

## Sources
Company reports and results, Vanguard factsheets, prices from yfinance.

This is a personal learning project, not investment advice.
