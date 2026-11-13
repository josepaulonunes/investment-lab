import yfinance as yf
import pandas as pd
import os
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# The DCF math lives in future/dcf.py so the dashboard uses the same numbers
from dcf import dcf_value, expected_return

# My assumptions for each company and the numbers of the method (I only change them in the quarterly review)
inputs = pd.read_csv("data/portfolio/fair_inputs.csv")
rules = pd.read_csv("data/portfolio/rules.csv").set_index("name")["value"]

# The economy: the US 10 year Treasury yield, average of the last 3 months so one bad week does not move every fair price
try:
    risk_free = yf.Ticker("^TNX").history(period="3mo")["Close"].mean() / 100
except Exception:
    risk_free = 0.045
print("Risk free rate:", round(risk_free * 100, 2), "%")

# Return I ask for: the risk free rate plus a premium that depends on how risky the business is
premium = {"normal": rules["premium_normal"] / 100, "cyclical": rules["premium_cyclical"] / 100, "risky": rules["premium_risky"] / 100}

# Margin of safety before an extra buy: the harder a company is to value, the bigger the discount I ask for
margin = {"medium": rules["margin_medium"] / 100, "high": rules["margin_high"] / 100, "very high": rules["margin_very_high"] / 100}

# Weight of my own DCF in the fair price (the rest is the Morningstar fair value)
weight_dcf = rules["weight_dcf"] / 100

# Today's price of each company, in its own currency
last = yf.download(list(inputs["ticker"]), period="10d", progress=False)["Close"].ffill().iloc[-1]

# What analysts expect each company to earn next year and the date of its next results
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

# The analysts' numbers I saved on earlier runs, to see if they are cutting their forecasts
history_file = "data/future/eps_history.csv"
history = pd.DataFrame(columns=["date", "ticker", "eps"])
if os.path.exists(history_file):
    history = pd.read_csv(history_file)
today = str(pd.Timestamp.today().date())
three_months_ago = str((pd.Timestamp.today() - pd.Timedelta(days=90)).date())
one_month_ago = str((pd.Timestamp.today() - pd.Timedelta(days=30)).date())

# Results in the next 7 days: never buy just before them
soon = str((pd.Timestamp.today() + pd.Timedelta(days=7)).date())

# Fair price, expected return and status of each company
rows = []
new_history = []
for _, company in inputs.iterrows():
    ticker = company["ticker"]
    price = last[ticker]

    # Profit a share: the analysts' number from today, so the fair price follows the real business
    # I keep my saved number when the company is not compared (cycle or cash based), when Yahoo has nothing, or when Yahoo is more than 30% away (a mistake or a big change I have to read first)
    eps = company["eps"]
    eps_gap = None
    if company["compare"] == "yes" and analyst_eps[ticker]:
        eps_gap = (analyst_eps[ticker] / company["eps"] - 1) * 100
        if abs(eps_gap) <= 30:
            eps = analyst_eps[ticker]
        new_history.append([today, ticker, analyst_eps[ticker]])

    # How much analysts changed their profit forecast in the last 3 months (it needs at least one month of saved numbers)
    eps_change = None
    before = history[(history["ticker"] == ticker) & (history["date"] >= three_months_ago) & (history["date"] <= one_month_ago)].sort_values("date")
    if len(before) > 0 and company["compare"] == "yes" and analyst_eps[ticker]:
        eps_change = (analyst_eps[ticker] / before["eps"].iloc[0] - 1) * 100

    # My DCF: growth is never above the cap, because very few big companies keep growing faster for 5 years
    cash = eps * company["conversion"]
    growth = min(company["growth"], rules["max_growth"] / 100)
    discount = risk_free + premium[company["risk"]]
    dcf = dcf_value(cash, growth, discount)

    # Fair price: my DCF mixed with the Morningstar fair value, or my DCF alone if Morningstar does not cover the company
    fair = dcf
    if pd.notna(company["morningstar"]):
        fair = weight_dcf * dcf + (1 - weight_dcf) * company["morningstar"]
    gap = (price / fair - 1) * 100
    yearly_return = expected_return(price, cash, growth) * 100

    # The Morningstar number is old if I did not write its date or if it is more than about 3 months old
    ms_old = "no"
    if pd.notna(company["morningstar"]):
        if pd.isna(company["ms_date"]) or (pd.Timestamp.today() - pd.to_datetime(company["ms_date"])).days > rules["morningstar_days"]:
            ms_old = "yes"

    # Three checks that the stock is really cheap: Morningstar above the price, my own DCF above the price, and analysts not cutting profits
    checks = 0
    available = 1
    if dcf > price:
        checks = checks + 1
    if pd.notna(company["morningstar"]):
        available = available + 1
        if company["morningstar"] > price:
            checks = checks + 1
    if eps_change is not None:
        available = available + 1
        if eps_change > -5:
            checks = checks + 1

    # A buy needs two checks, analysts not cutting profits by more than 10%, and no alarm on
    # A company with no Morningstar value and no saved history has only one check, so it cannot be confirmed yet
    safe = company["alarm_on"] != "yes"
    if eps_change is not None and eps_change < -10:
        safe = False
    confirmed = checks >= 2 and safe
    results_soon = next_results[ticker] is not None and next_results[ticker] <= soon

    # Price levels: a plan starts at the fair price (minus start_margin, 0 today), an extra buy (or buy big) needs the full margin of safety
    start = fair * (1 - rules["start_margin"] / 100)
    entry = fair * (1 - margin[company["uncertainty"]])

    # Stocks I own or have in the plan: keep buying up to 10% above fair, pause beyond that, sell part 50% above
    if company["list"] == "portfolio":
        status = "PAUSE"
        if price <= fair * 1.10:
            status = "KEEP BUYING"
        if price <= entry:
            status = "CHEAP, NOT CONFIRMED"
            if confirmed:
                status = "BUY EXTRA"
                if results_soon:
                    status = "WAIT RESULTS"
        if price >= fair * 1.5:
            status = "SELL PART"

    # Companies waiting for a good price: priorities start a plan, watchlist ones get a full analysis first
    if company["list"] != "portfolio":
        status = "WAIT"
        if price <= start:
            status = "CHEAP, NOT CONFIRMED"
            # A priority already passed my five tests, so its plan starts if its alarm is off and profits are not being cut
            if company["list"] == "priority" and safe:
                status = "START PLAN"
            # A watchlist company and every big buy still need two checks
            if company["list"] == "watchlist" and confirmed:
                status = "BUY"
            if price <= entry and confirmed:
                status = "BUY BIG"
            if results_soon and status != "CHEAP, NOT CONFIRMED":
                status = "WAIT RESULTS"

    # No price from Yahoo this week
    if pd.isna(price):
        status = "NO PRICE"

    rows.append([company["name"], ticker, company["list"], company["currency"], price, fair, gap, yearly_return, entry, start, status, f"{checks}/{available}", company["alarm"], company["eps"], analyst_eps[ticker], eps_gap, next_results[ticker], dcf, company["morningstar"], discount * 100, margin[company["uncertainty"]] * 100, eps, eps_change, company["alarm_on"], ms_old])

# Save for the alerts and the dashboard, cheapest first
columns = ["name", "ticker", "list", "currency", "price", "fair", "gap", "return", "entry", "start", "status", "checks", "alarm", "my_eps", "analyst_eps", "eps_gap", "next_results", "dcf", "morningstar", "discount", "margin", "eps_used", "eps_change", "alarm_on", "ms_old"]
table = pd.DataFrame(rows, columns=columns)
table = table.sort_values("gap")
table.to_csv("data/future/fair_prices.csv", index=False)

# Save today's analyst numbers (one line per company per day, one year of history is enough)
history = history[history["date"] != today]
history = pd.concat([history, pd.DataFrame(new_history, columns=["date", "ticker", "eps"])])
one_year_ago = str((pd.Timestamp.today() - pd.Timedelta(days=365)).date())
history = history[history["date"] >= one_year_ago]
history.to_csv(history_file, index=False)

print(table[["name", "list", "price", "dcf", "morningstar", "fair", "gap", "return", "checks", "status"]].round(1).to_string(index=False))
