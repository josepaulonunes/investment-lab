import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Value of one share today: the cash of the next 10 years plus what comes after
def dcf_value(cash, growth, discount):
    value = 0
    for year in range(1, 11):
        # 5 years at full growth, then it falls in a straight line to 4% in year 10
        rate = growth
        if year > 5:
            rate = growth + (0.04 - growth) * (year - 5) / 5
        cash = cash * (1 + rate)
        value = value + cash / (1 + discount) ** year
    # After year 10 the cash grows 2.25% a year
    final = cash * 1.0225 / (discount - 0.0225)
    return value + final / (1 + discount) ** 10

# Yearly return if I buy at today's price and the base case happens
def expected_return(price, cash, growth):
    rate = 0.03
    while rate < 0.30 and dcf_value(cash, growth, rate) > price:
        rate = rate + 0.001
    return rate

# My assumptions for each company (I only change them in the quarterly review)
inputs = pd.read_csv("data/portfolio/fair_inputs.csv")

# Today's price of each company, in its own currency
last = yf.download(list(inputs["ticker"]), period="10d", progress=False)["Close"].ffill().iloc[-1]

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

    rows.append([company["name"], company["ticker"], company["list"], company["currency"], price, fair, gap, yearly_return, entry, status, company["alarm"]])

# Save for the alerts and the dashboard, cheapest first
table = pd.DataFrame(rows, columns=["name", "ticker", "list", "currency", "price", "fair", "gap", "return", "entry", "status", "alarm"])
table = table.sort_values("gap")
table.to_csv("data/future/fair_prices.csv", index=False)
print(table[["name", "list", "price", "fair", "gap", "return", "status"]].round(1).to_string(index=False))
