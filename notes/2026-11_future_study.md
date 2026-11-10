# Future study (Nov 2026)

I believe AI, chips, power and nuclear will shape the next decades. For now I hold these sectors through ETFs. This study is a test: it picks individual companies with clear rules, and in January 2028 I compare its picks with the future ETFs to see if picking stocks is worth the work.

## The chain I want to own
Chips, manufacturing, memory, networking, data center power, grid, nuclear and cloud. Since 9 Nov 2026 also companies that are in almost everything and have little competition (see 2026-11_moat_study.md). The list is in data/future/universe.csv.

## Why new criteria
My first screener asked for a forward P/E under 25. Fast growers almost never pass that, even when the price is fair for their growth. So this study asks two questions.

Is it a good business? (quality, out of 5)
1. Revenue grew more than 10% last year
2. Operating margin above 10%
3. Positive free cash flow
4. Net debt below 3x EBITDA
5. Return on equity above 15%: it turns the money it keeps into a lot more profit

Is the price backed by what the company does today?
- Reverse DCF: the yearly free cash flow growth for 10 years that the price already assumes (9% discount, 2.5% terminal)
- If the company already grows faster than that (capped at 25%), the price is backed by reality

Is it hard to replace and central to the future? (edge, out of 4, my own scores in universe.csv)
- moat: 0 no real edge, 1 some edge, 2 near monopoly or duopoly
- future: 0 no link, 1 steady need, 2 central to AI, power or health
- Why: the last year of numbers says nothing about the next ten. Morningstar's Wide Moat Focus index, which buys companies with a lasting edge only when they trade below fair value, beat the S&P 500 for years. The edge alone was not enough, the price mattered too. So I need both

Is it built for the long run? (long term, out of 2)
- Revenue grew more than 10% a year over the last 3 years, not just the last one
- It gives back more than 1% of its value a year to shareholders through dividends and buybacks

Score: quality + edge + long term, out of 11. A warning shows if the company adds more than 2% new shares a year, because that makes each share worth less. Inside each verdict, the higher score comes first.

## Verdicts
- BUY: quality 4 or 5, moat 2 (little competition), edge 3 or 4, and price at or below the buy price
- WATCH: good business, price assumes more growth than the company shows today
- CHECK: reports in another currency, value it by hand
- SPECULATIVE: no free cash flow yet (bet on the future, tiny amounts only)
- AVOID: quality below 4, moat below 2 or edge below 3

## Rules if I ever put money in it
- Never more than 10% of the portfolio, never more than 1.5% in one company
- One company per link of the chain at most, so I own a bit of everything
- If fewer than 4 BUYs, the rest goes to VWCE
- Rerun the study every January. A company that turns WATCH keeps what I bought, new money goes elsewhere
- Sell only if the business breaks, never because the price fell
- Growth over 40% gets a warning and is left out of the plan: it may be a cycle peak (memory chips are famous for this)

## What the numbers can't see (checked by hand for the finalists)
- Geopolitics: Taiwan, China export limits, sanctions
- Customers: does a big part of revenue come from one or two clients?
- Regulation and politics: drug prices, payment fees, antitrust
- Management: do they invest the money well, or buy growth with debt?

## Limits of this model
- One year of growth says little about the next ten
- Free cash flow is low when a company invests a lot (Amazon, Microsoft), which makes them look expensive
- yfinance data can be wrong. Check the annual report before buying
