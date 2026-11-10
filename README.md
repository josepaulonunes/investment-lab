# Investment Lab

My own investment tools in Python: a live dashboard of my portfolio, a screener that looks for companies with almost no competition at a fair price, and a weekly check that tells me when to buy more, stop buying or look closer.

## The plan
| Block | What | Weight |
|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | 60% |
| Small companies | iShares MSCI World Small Cap (IUSN) | 10% |
| Theme ETFs | Health care 4%, power grid 3%, quantum computing 3%, nuclear 3% | 13% |
| Stocks | TSMC 4%, Mastercard 4%, Broadcom 3%, Nvidia 3%, Intuitive Surgical 3% | 17% |

70% follows the whole market. 30% are bets on the sectors I think will shape the next decades, each between 3% and 5%. Automatic plans every month, a check every Monday, a review every January. The rules are in IPS.md.

## How I picked the stocks
1. A list of about 100 companies in AI, chips, energy, nuclear, health, payments and more (data/future/universe.csv)
2. The screener scores each one: quality (growth, margin, cash, debt, return on equity), moat and future (my own scores, 0 to 4) and the long run (3 year growth and money given back to shareholders)
3. A DCF gives two fair prices: a careful one where growth fades to 2.5% over 10 years, as research says it usually does, and an optimistic one where it doesn't. The discount rate is the 10 year Treasury yield plus beta times Damodaran's equity risk premium (notes/2026-11_fair_price_method.md)
4. Only companies with a near monopoly, top quality and a price below the careful fair price get a BUY
5. A portfolio optimizer (portfolio/optimize.py) helps set the weights

## The weekly check
Every Monday GitHub runs the screener and future/alerts.py. If something needs my attention it opens an issue and I get a notification:
- BUY or BUY EXTRA: a stock is below its careful fair price
- EXPENSIVE: a stock I own is above its optimistic fair price. I keep buying and look at it in January
- STOP BUYING: a bet is above 5% of the portfolio, or bets are above 30%
- REVIEW: the business got worse (quality, revenue, debt, new shares)

I never sell just because the price fell.

## What's inside
| Folder | What it does |
|---|---|
| portfolio/ | Dashboard (Streamlit), positions vs targets, optimizer, public data |
| future/ | Screener and weekly alerts |
| companies/ | Valuation model for any company: ratios, DCF, reverse DCF, sensitivity, peers |
| house_view/ | Scores regions by valuation and momentum |
| data/ | Inputs and outputs |
| notes/ | My decisions, written before deciding |

## How to run
My real purchases are private. The live app shows my real portfolio scaled so that all the money I put in adds up to 100: you see weights and returns, not amounts.

    pip install -r requirements.txt
    python -m streamlit run portfolio/dashboard.py
    python future/future_screen.py
    python future/alerts.py
    python portfolio/optimize.py

## Sources
Company reports, MSCI, Vanguard, iShares, Xtrackers, First Trust and VanEck factsheets, prices from yfinance.

This is a personal learning project, not investment advice.
