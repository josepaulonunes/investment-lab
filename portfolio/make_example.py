import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# My plan: every product with a target, euros for every 100 EUR invested
products = pd.read_csv("data/portfolio/products.csv")
plan = products[products["target"] > 0]

# Real daily prices for the last 12 months, all in euros
prices = yf.download(list(plan["ticker"]) + ["EURUSD=X"], start="2025-11-01", progress=False)["Close"].ffill()
for _, product in plan.iterrows():
    if product["currency"] == "USD":
        prices[product["ticker"]] = prices[product["ticker"]] / prices["EURUSD=X"]

# Buy the plan on the first trading day from the 2nd of each month
rows = []
for month in pd.date_range("2025-11-02", periods=12, freq="MS"):
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
