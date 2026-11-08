# Investment Lab

My own investment lab. I built it to track my money and to test whether picking companies is worth it for me.

## The plan
75% in a global ETF (VWCE), 10% in world small caps (IUSN), 12% in the sectors I think will shape the future (AI, power grid, nuclear and health care) and 3% in physical gold. 700 EUR a month with automatic plans, reviewed once a year in January. The rules are in IPS.md.

## How I got here
I started with 80% VWCE plus 10% in country ETFs and 10% in gold. Then I built a model to analyse companies and moved to 90/5/5 with 5% in stocks that got a BUY. Three did (Wolters Kluwer, Adobe, Zoetis).

Before buying them I asked myself if it was worth it. My answer was no: I don't want to follow companies every quarter, the tax return gets harder and most professionals lose to the index anyway. I kept the analysis here as a study.

In November 2026 I looked at what could diversify VWCE without becoming another bet on the same big tech names. Small caps did that. Emerging markets and value ETFs did not, because their top holdings are also AI chip makers.

Then I added a small future block. I believe AI, electrification, nuclear and health care will shape the next decades, but VWCE already holds most of those companies, so the extra bet stays small: four ETFs, 12% in total.

## What's inside
| Folder | What it does |
|---|---|
| portfolio/ | Tracks positions, weights vs targets and the cash rule. dashboard.py shows it in Streamlit |
| future/ | Study of AI, chips, power and nuclear companies with criteria for fast growers. Gives BUY, WATCH, SPECULATIVE or AVOID and a monthly plan |
| companies/ | Study: screener plus one model for any company (ratios, DCF with 3 scenarios, reverse DCF, sensitivity, peers) |
| house_view/ | Study: scores regions by valuation and momentum |
| data/ | Inputs and outputs of each part |
| notes/ | My decisions and company notes, written before deciding |

## How to run
My real purchases are kept private. The live app shows my real portfolio scaled so that all the money I put in adds up to 100 (data/portfolio/public/), so you see weights and returns but not the amounts. After each monthly purchase I run python portfolio/make_public.py to update it. If neither file is there, the scripts use the example data in data/portfolio/example/.

    pip install -r requirements.txt
    python portfolio/portfolio.py
    python -m streamlit run portfolio/dashboard.py

The studies:

    python house_view/prices.py
    python house_view/metrics.py
    python house_view/score.py
    python companies/screener.py
    python companies/analyse_company.py
    python future/future_screen.py

## What I learned so far
- My first house view picked Korea and Brazil, but VWCE already holds emerging markets, so country bets add little.
- Of 10 companies I analysed, 3 got a BUY. All three were good businesses the market feared for a clear reason.
- Automatic data can be wrong. Yahoo's free cash flow for Prysmian implied 23% growth, the company's own accounts gave 6%.
- More ETFs is not more diversification. A value or emerging markets ETF can have a chip maker as its biggest holding.
- The amount I invest and how long I stay invested matter far more than which ETF I pick.

## Sources
MSCI and iShares factsheets, Vanguard and J.P. Morgan long term return forecasts, company annual reports, prices from yfinance.

This is a personal learning project, not investment advice.
