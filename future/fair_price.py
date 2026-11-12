import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# The DCF math lives in future/dcf.py so the dashboard uses the same numbers
from dcf import dcf_value, expected_return

# My assumptions for each company (I only change them in the quarterly review)
inputs = pd.read_csv("data/portfolio/fair_inputs.csv")

# Today's price of each company, in its own currency
last = yf.download(list(inputs["ticker"]), period="10d", progress=False)["Close"].ffill().iloc[-1]

# What analysts expect each company to earn next year and the date of its next results (Yahoo)
analyst_eps = {}
next_results = {}
for ticker in inputs["ticker"]:
    analyst_eps[ticker] = None
    next_results[ticker] = None
    try:
        info = yf.Ticker(ticker).info
        analyst_eps[ticker] = info.get("forwardEps")
        stamp = info.get("earningsTimestampStart", info.get("earningsTimestamp"))
        if stamp:
            day = pd.to_datetime(stamp, unit="s").date()
            if day >= pd.Timestamp.today().date():
                next_results[ticker] = str(day)
    except Exception:
        print("No analyst data for", ticker)

# Fair price, expected return and status of each company
rows = []
for _, company in inputs.iterrows():
    price = last[company["ticker"]]
    cash = company["eps"] * company["conversion"]
    fair = dcf_value(cash, company["growth"], company["discount"])
    gap = (price / fair - 1) * 100
    yearly_return = expected_return(price, cash, company["growth"]) * 100

    # Stocks in the plan: buy extra 15% below fair, keep buying up to 10% above fair, pause beyond that
    # The 10% of room is there so a plan does not stop and start on small price moves
    if company["list"] == "portfolio":
        entry = fair * 0.85
        status = "PAUSE"
        if price <= fair * 1.10:
            status = "KEEP BUYING"
        if price <= entry:
            status = "BUY EXTRA"
        # Far too expensive: 50% or more above fair, the price already counts on many years of perfect growth
        if price >= fair * 1.5:
            status = "SELL PART"

    # Watchlist: buy at my entry price (the fair price if I did not set one)
    if company["list"] == "watchlist":
        entry = fair
        if pd.notna(company["entry"]):
            entry = company["entry"]
        status = "WAIT"
        if price <= entry:
            status = "BUY"

    # No price from Yahoo this week
    if pd.isna(price):
        status = "NO PRICE"

    # How far the analysts are from my profit number (Vistra uses cash, not profit, so it is not compared)
    eps_gap = None
    if company["compare"] == "yes" and analyst_eps[company["ticker"]]:
        eps_gap = (analyst_eps[company["ticker"]] / company["eps"] - 1) * 100

    rows.append([company["name"], company["ticker"], company["list"], company["currency"], price, fair, gap, yearly_return, entry, status, company["alarm"], company["eps"], analyst_eps[company["ticker"]], eps_gap, next_results[company["ticker"]]])

# Save for the alerts and the dashboard, cheapest first
table = pd.DataFrame(rows, columns=["name", "ticker", "list", "currency", "price", "fair", "gap", "return", "entry", "status", "alarm", "my_eps", "analyst_eps", "eps_gap", "next_results"])
table = table.sort_values("gap")
table.to_csv("data/future/fair_prices.csv", index=False)
print(table[["name", "list", "price", "fair", "gap", "return", "status"]].round(1).to_string(index=False))
