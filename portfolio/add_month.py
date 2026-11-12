import pandas as pd
import yfinance as yf
import os
import sys
from datetime import date
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# How much I invested this month (asked each time, so the amount never goes to GitHub)
monthly = float(input("How much did the plans invest this month (€)? "))

# Month to add: this month, or the one I write after the script name
# Example: python portfolio/add_month.py 2026-12
month = date.today().strftime("%Y-%m")
if len(sys.argv) > 1:
    month = sys.argv[1]

# My real purchases (private) and my plan
file = "data/portfolio/transactions.csv"
transactions = pd.read_csv(file)
products = pd.read_csv("data/portfolio/products.csv")
plan = products[products["target"] > 0]

# Trade Republic buys on the 2nd, or on the next day the market is open
start = month + "-02"
end = str((pd.Timestamp(start) + pd.Timedelta(days=8)).date())
prices = yf.download(list(plan["ticker"]) + ["EURUSD=X"], start=start, end=end, progress=False)["Close"].ffill()
if len(prices) == 0:
    print("No prices yet for", start, "- run it again after the plans have bought")
    exit()
day = prices.index[0]
plan_date = str(day.date())

# Stop if this month's plan is already in the file (a VWCE purchase on the plan day)
vwce = plan[plan["block"] == "core"]["isin"].iloc[0]
done = transactions[(transactions["date"] == plan_date) & (transactions["isin"] == vwce)]
if len(done) > 0:
    print("The plan of", month, "is already in", file)
    exit()

# One purchase per product: its share of the monthly money at that day's price in euros
rows = []
for _, product in plan.iterrows():
    price = prices.loc[day, product["ticker"]]
    if product["currency"] == "USD":
        price = price / prices.loc[day, "EURUSD=X"]
    amount = product["target"] / 100 * monthly
    rows.append([plan_date, product["isin"], product["name"], product["block"], round(amount / price, 6), round(price, 4), amount, 0.0])

# Add them to my file and update the public version
new = pd.DataFrame(rows, columns=["date", "isin", "name", "block", "quantity", "price_eur", "amount_eur", "fee_eur"])
transactions = pd.concat([transactions, new], ignore_index=True)
transactions.to_csv(file, index=False)
print(new[["name", "amount_eur", "price_eur", "quantity"]].to_string(index=False))
print("Added", len(new), "purchases on", plan_date, "(prices are the close of that day, Trade Republic may differ by a little)")
os.system("python portfolio/make_public.py")
