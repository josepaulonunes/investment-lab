# Investment Lab

How I invest every month and how I value the companies I follow.

I'm an economist and I invest a fixed amount every month on Trade Republic: a small part always goes to a world ETF (VWCE) and the rest goes to a few companies in AI, chips, energy and health, but only when the analysts and my own valuation both say it is a good moment. If not, the money waits.

**[Open the live app](https://investment-lab-josenunes.streamlit.app)**

## How it works

| Part | What it does |
|---|---|
| Weekly ranking (private) | Every Monday 64 companies go through 5 gates and 18 criteria, with analyst revisions weighing the most |
| DCF models (private) | One 10 year DCF per company in Excel, with bear, base and bull scenarios and price alerts |
| My portfolio (private) | Read from Trade Republic with [pytr](https://github.com/pytr-org/pytr) |
| `export.py` | Turns those private files into small public tables in `data/`. Weights and returns only, never euros |
| `app.py` | A Streamlit app that shows the tables. It never decides anything |
| `METHOD.md` | The rules and the method on one page |
| `journal/` | One note a month: what I bought, what I didn't and why |

The app has five tabs:
- **Portfolio:** what I own, the return of each product and each theme against its limit
- **Ranking:** this week's ranking with the signals 🔥 and ⚠
- **Fair value:** today's price against the bear, base and bull value of each company, the alerts and the WACC the price implies
- **Am I beating VWCE?** my real portfolio and a ghost portfolio that follows the rules on paper, both against VWCE
- **Method:** the rules

## Every month

1. Every Monday the ranking and the valuations are updated.
2. On the 1st I check which automatic plans stay, pause or start.
3. I run `python export.py` and commit the new tables in `data/`.
4. I write a short note in `journal/`.

## Run it yourself

    pip install -r requirements.txt
    python -m streamlit run app.py

The tables in `data/` are already there, so the app works without my private files.

## Earlier versions

This is the third version. The first was a screener with daily alerts, the second one big Excel model that decided everything. Both taught me that analyst estimate revisions were the most useful signal, so I rebuilt the whole thing around them and kept one system only.

This is a personal learning project, not investment advice.
