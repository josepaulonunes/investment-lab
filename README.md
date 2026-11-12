# Investment Lab

My own investment tools in Python: a live dashboard of my portfolio, a screener that looks for companies with almost no competition at a fair price, and a daily check that tells me when to buy more, stop buying or look closer.

## The plan
| Block | What | Weight |
|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | 60% |
| Stocks | Nvidia 5%, TSMC 5%, ASML 5%, Broadcom 4%, ServiceNow 4%, Mastercard 5%, Eli Lilly 5%, GE Vernova 4%, Vistra 3% | 40% |

60% follows the whole market. 40% is in 9 companies from 5 sectors that clearly beat their rivals, bought only at a fair price or below. VWCE never goes below 60%: when a stock gets expensive its monthly plan goes to VWCE, and a watchlist company only comes in when another one leaves. Automatic plans every month, a check every Monday, a review every quarter. The rules are in IPS.md.

I dropped the small cap ETF and the theme ETFs on 12 Nov 2026 (notes/2026-11-12_plan_change.md).

## How I pick the stocks
1. A list of about 180 companies in AI, chips, energy, health, payments, aviation, defense and more (data/future/universe.csv)
2. The screener scores each one: quality (growth, margin, cash, debt, return on equity), moat and future (my own scores) and the long run. I use it to find candidates and to watch the health of the business
3. For the ones I own or want, I write down my own assumptions in data/portfolio/fair_inputs.csv: profit per share for the next 12 months, how much of it becomes cash, and growth for the next 5 years
4. future/fair_price.py turns that into a fair price with a simple DCF and tells me the yearly return today's price gives me. I ask for at least 9%
5. A company only comes in if it passes my five tests (growth, beats its rivals, key sector, pays shareholders, fair price) and I have written the analysis

## The daily check
Every weekday after the US market closes, GitHub runs the screener, the fair prices and future/alerts.py. If the alerts are different from the last check it opens an issue and I get a notification. Every stock I own gets one line:
- BUY EXTRA: 15% or more below its fair price. A one-off buy makes sense
- KEEP: up to 10% above fair. The monthly plan keeps going
- PAUSE: more than 10% above fair. Its plan goes to VWCE and I keep the shares
- SELL PART: 50% or more above fair. The price already counts on years of perfect growth, so I sell up to half and move it to VWCE
- REVIEW: one warning sign in the business (quality, revenue, debt, new shares). I look closer
- SELL: two or more warning signs at once. If the next results confirm them, I sell
- STOP BUYING: a stock is above 5% of the portfolio, one sector is above 20% (VWCE does not count), everything linked to AI is above 30%, or all stocks are above 40%

And for the watchlist:
- BUY: the price reached my entry price. Time to write the full analysis

To keep the fair prices fresh:
- CLOSE: a stock is less than 5% above its buying price, so I get the order ready
- REVIEW ASSUMPTION: analysts now expect a profit more than 15% away from mine, usually after results. I update data/portfolio/fair_inputs.csv
- RESULTS: one of my stocks reports in the next 7 days

I never sell just because the price fell.

## The dashboard
`python -m streamlit run portfolio/dashboard.py` opens five tabs:
- Portfolio: value vs money invested, what I own, gain per product and per month
- Monthly plan: where each euro goes for any monthly amount, and every limit (sector, AI, stocks)
- Fair prices: price vs my fair price for my stocks and the watchlist, and the yearly return each price gives me
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

## Sources
Company reports and results, Vanguard factsheets, prices from yfinance.

This is a personal learning project, not investment advice.
