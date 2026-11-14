# Investment Lab

How I invest every month and how I value the companies I follow.

I'm an economist and I invest a fixed amount every month: most of it in a world ETF (VWCE) and the rest in a few companies I know well, in chips and AI, software, payments, the power grid and health. I only want to buy them at a fair price, so I built a valuation model for each one, the way investment banks do it.

**[Open the live app](https://investment-lab-josenunes.streamlit.app)**

## How it works

| Part | What it does |
|---|---|
| My Excel model (private) | Where everything is decided. One DCF per company, the comparables, the rules and the monthly plan. I update it on the 1st of every month |
| `export.py` | Reads the Excel and saves five small tables in `data/`. It keeps weights and returns, never euros |
| `app.py` | A Streamlit app that shows those tables. It never decides anything |
| `METHOD.md` | The method and my rules on one page |
| `journal/` | One note a month: what changed in the plan and why |

The app has five tabs:
- **Portfolio:** what I own and the return of each product
- **Monthly plan:** where this month's money goes, and which stocks are paused because they are too expensive
- **Fair value:** today's price against the bear, base and bull value of each company, and how both move over time
- **Watchlist:** the price at which each company becomes an extra buy
- **Method:** how the model works

## The valuation model

Each company has a 10 year DCF with three scenarios. The discount rate uses a sector beta (from similar companies, without and then with debt), the terminal value only rewards growth that earns more than its cost of capital, and every value is checked with a reverse DCF, an exit multiple and the multiples of similar companies. The full method is in [METHOD.md](METHOD.md).

## Every month

1. On the 1st I update prices, rates and my positions in the Excel.
2. I run `python export.py` and commit the new tables in `data/`.
3. I write a short note in `journal/`.
4. The automatic plans buy on the 2nd.

## Run it yourself

    pip install -r requirements.txt
    python -m streamlit run app.py

The tables in `data/` are already there, so the app works without my Excel.

## Earlier version

The first version of this project (a screener, daily GitHub alerts and a fair price mixed with Morningstar) is saved in the tag `v1-old`. I replaced it because it was a second system making decisions next to my Excel, and two systems can disagree.

This is a personal learning project, not investment advice.