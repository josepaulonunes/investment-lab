# Future study (Nov 2026)

I believe AI, chips, power and nuclear will shape the next decades. For now I hold these sectors through ETFs. This study is a test: it picks individual companies with clear rules, and in January 2028 I compare its picks with the future ETFs to see if picking stocks is worth the work.

## The chain I want to own
Chips, manufacturing, memory, networking, data center power, grid, nuclear and cloud. The list is in data/future/universe.csv.

## Why new criteria
My first screener asked for a forward P/E under 25. Fast growers almost never pass that, even when the price is fair for their growth. So this study asks two questions.

Is it a good business? (quality, out of 4)
1. Revenue grew more than 10% last year
2. Operating margin above 10%
3. Positive free cash flow
4. Net debt below 3x EBITDA

Is the price backed by what the company does today?
- Reverse DCF: the yearly free cash flow growth for 10 years that the price already assumes (9% discount, 2.5% terminal)
- If the company already grows faster than that (capped at 25%), the price is backed by reality

## Verdicts
- BUY: quality 3 or 4 and price at or below the buy price
- WATCH: good business, price assumes more growth than the company shows today
- CHECK: reports in another currency, value it by hand
- SPECULATIVE: no free cash flow yet (bet on the future, tiny amounts only)
- AVOID: quality below 3

## Rules if I ever put money in it
- Never more than 10% of the portfolio, never more than 1.5% in one company
- One company per link of the chain at most, so I own a bit of everything
- If fewer than 4 BUYs, half goes to WTAI (IE00BDVPNG13)
- Rerun the study every January. A company that turns WATCH keeps what I bought, new money goes elsewhere
- Sell only if the business breaks, never because the price fell
- Growth over 40% gets a warning and is left out of the plan: it may be a cycle peak (memory chips are famous for this)

## Limits of this model
- One year of growth says little about the next ten
- Free cash flow is low when a company invests a lot (Amazon, Microsoft), which makes them look expensive
- yfinance data can be wrong. Check the annual report before buying
