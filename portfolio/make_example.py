import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# My plan: every product with a target, euros for every 100 EUR invested
products = pd.read_csv("data/portfolio/products.csv")
plan = products[products["target"] > 0]

# Exchange rates: one ticker for each currency that is not the euro (EURUSD=X, EURJPY=X...)
rate_tickers = []
for currency in plan["currency"].unique():
    if currency != "EUR":
        rate_tickers.append("EUR" + currency + "=X")

# The last 12 months: the first purchase is on the 2nd of the month a year ago
first_month = pd.Timestamp.today().normalize().replace(day=1) - pd.DateOffset(months=12)

# Real daily prices since then, all in euros
prices = yf.download(list(plan["ticker"]) + rate_tickers, start=first_month, progress=False)["Close"].ffill()
for _, product in plan.iterrows():
    if product["currency"] != "EUR":
        prices[product["ticker"]] = prices[product["ticker"]] / prices["EUR" + product["currency"] + "=X"]

# Buy the plan on the first trading day from the 2nd of each month
rows = []
for month in pd.date_range(first_month, periods=12, freq="MS"):
    day = prices.index[prices.index >= month + pd.Timedelta(days=1)][0]
    for _, product in plan.iterrows():
        price = prices.loc[day, product["ticker"]]
        if pd.isna(price):
            continue
        amount = product["target"]
        rows.append([day.date(), product["isin"], product["name"], product["block"], round(amount / price, 4), round(price, 2), amount, 0])

# Save the example files
folder = "data/portfolio/example/"
columns = ["date", "isin", "name", "block", "quantity", "price_eur", "amount_eur", "fee_eur"]
pd.DataFrame(rows, columns=columns).to_csv(folder + "transactions.csv", index=False)
last = prices.iloc[-1]
current = [[p["isin"], p["name"], round(last[p["ticker"]], 2), prices.index[-1].date()] for _, p in plan.iterrows()]
pd.DataFrame(current, columns=["isin", "name", "price_eur", "date"]).to_csv(folder + "current_prices.csv", index=False)
print("Example data saved:", len(rows), "purchases")
