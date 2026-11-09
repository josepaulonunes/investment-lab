# Investment Lab

My own investment tools in Python: a tracker and dashboard for my ETF portfolio, and a study that tests if picking stocks is worth it for me.

## The plan
| Block | ETF | Weight |
|---|---|---|
| Core | Vanguard FTSE All-World (VWCE) | 74% |
| Small companies | iShares MSCI World Small Cap (IUSN) | 10% |
| Future: power grid | First Trust Smart Grid Infrastructure (GRID) | 4% |
| Future: health care | Xtrackers MSCI World Health Care (XDWH) | 4% |
| Future: materials | Xtrackers MSCI World Materials (XDWM) | 3% |
| Future: nuclear | VanEck Uranium and Nuclear Technologies (NUKL) | 2% |
| Insurance | Invesco Physical Gold | 3% |

Automatic plans every month, reviewed once a year in January. The core follows the whole market. The future block (13%) is my bet on the sectors I think will shape the next decades, kept small on purpose. The rules are in IPS.md.

## What's inside
| Folder | What it does |
|---|---|
| portfolio/ | Positions, weights vs targets and the cash rule. dashboard.py is the Streamlit app |
| future/ | Screener for AI, chips, power and nuclear companies. Gives BUY, WATCH, SPECULATIVE or AVOID. In January 2028 I compare its picks with the future ETFs |
| companies/ | Valuation model for any company: ratios, DCF with 3 scenarios, reverse DCF, sensitivity, peers |
| house_view/ | Scores regions by valuation and momentum |
| data/ | Inputs and outputs of each part |
| notes/ | My decisions, written before deciding |

## How to run
My real purchases are private. The live app shows my real portfolio scaled so that all the money I put in adds up to 100, so you see weights and returns but not the amounts. If that file is not there, the scripts use example data.

    pip install -r requirements.txt
    python portfolio/portfolio.py
    python -m streamlit run portfolio/dashboard.py
    python future/future_screen.py

## Sources
MSCI, iShares, Vanguard, WisdomTree, Xtrackers, First Trust and VanEck factsheets, company annual reports, prices from yfinance.

This is a personal learning project, not investment advice.
