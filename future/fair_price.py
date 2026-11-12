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

# What analysts expect each company to earn next year, the date of its next results,
# the forward P/E, the banks' average target and their average rating (Yahoo: 1 = strong buy, 5 = sell)
analyst_eps = {}
next_results = {}
forward_pe = {}
bank_target = {}
bank_rating = {}
for ticker in inputs["ticker"]:
    analyst_eps[ticker] = None
    next_results[ticker] = None
    forward_pe[ticker] = None
    bank_target[ticker] = None
    bank_rating[ticker] = None
    try:
        info = yf.Ticker(ticker).info
        analyst_eps[ticker] = info.get("forwardEps")
        forward_pe[ticker] = info.get("forwardPE")
        bank_target[ticker] = info.get("targetMeanPrice")
        bank_rating[ticker] = info.get("recommendationMean")
        stamp = info.get("earningsTimestampStart", info.get("earningsTimestamp"))
        if stamp:
            day = pd.to_datetime(stamp, unit="s").date()
            if day >= pd.Timestamp.today().date():
                next_results[ticker] = str(day)
    except Exception:
        print("No analyst data for", ticker)

# Results in the next 7 days: never buy extra just before them
soon = str((pd.Timestamp.today() + pd.Timedelta(days=7)).date())

# Fair price, expected return and status of each company
rows = []
for _, company in inputs.iterrows():
    ticker = company["ticker"]
    price = last[ticker]
    cash = company["eps"] * company["conversion"]
    fair = dcf_value(cash, company["growth"], company["discount"])
    gap = (price / fair - 1) * 100
    yearly_return = expected_return(price, cash, company["growth"]) * 100

    # How far the analysts are from my profit number (Vistra uses cash, not profit, so it is not compared)
    eps_gap = None
    if company["compare"] == "yes" and analyst_eps[ticker]:
        eps_gap = (analyst_eps[ticker] / company["eps"] - 1) * 100

    # Three independent checks that the stock is really cheap
    checks = 0
    available = 0
    if pd.notna(company["morningstar"]):
        available = available + 1
        if company["morningstar"] > price:
            checks = checks + 1
    if pd.notna(company["pe5y"]) and forward_pe[ticker]:
        available = available + 1
        if forward_pe[ticker] < company["pe5y"]:
            checks = checks + 1
    if bank_target[ticker] and bank_rating[ticker]:
        available = available + 1
        if bank_target[ticker] >= price * 1.15 and bank_rating[ticker] <= 2.5:
            checks = checks + 1

    # A buy needs at least two checks, analysts not cutting their profit forecast by more than 10%, and no results this week
    confirmed = checks >= 2
    if eps_gap is not None and eps_gap < -10:
        confirmed = False
    results_soon = next_results[ticker] is not None and next_results[ticker] <= soon

    # Stocks in the plan: buy extra 15% below fair, keep buying up to 10% above fair, pause beyond that
    # The 10% of room is there so a plan does not stop and start on small price moves
    start = None
    if company["list"] == "portfolio":
        entry = fair * 0.85
        status = "PAUSE"
        if price <= fair * 1.10:
            status = "KEEP BUYING"
        if price <= entry:
            status = "CHEAP, NOT CONFIRMED"
            if confirmed:
                status = "BUY EXTRA"
                if results_soon:
                    status = "WAIT RESULTS"
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

    # Top priorities, the companies I want to own one day: start a monthly plan 10% below the fair price, buy big 20% below it
    if company["list"] == "priority":
        start = fair * 0.90
        entry = fair * 0.80
        status = "WAIT"
        if price <= start:
            status = "CHEAP, NOT CONFIRMED"
            if confirmed:
                status = "START PLAN"
                if price <= entry:
                    status = "BUY BIG"
                if results_soon:
                    status = "WAIT RESULTS"

    # No price from Yahoo this week
    if pd.isna(price):
        status = "NO PRICE"

    rows.append([company["name"], ticker, company["list"], company["currency"], price, fair, gap, yearly_return, entry, start, status, f"{checks}/{available}", company["alarm"], company["eps"], analyst_eps[ticker], eps_gap, next_results[ticker]])

# Save for the alerts and the dashboard, cheapest first
table = pd.DataFrame(rows, columns=["name", "ticker", "list", "currency", "price", "fair", "gap", "return", "entry", "start", "status", "checks", "alarm", "my_eps", "analyst_eps", "eps_gap", "next_results"])
table = table.sort_values("gap")
table.to_csv("data/future/fair_prices.csv", index=False)
print(table[["name", "list", "price", "fair", "gap", "return", "checks", "status"]].round(1).to_string(index=False))
