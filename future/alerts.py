import yfinance as yf
import pandas as pd
import os
from datetime import date
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Limits from IPS.md (change them in data/portfolio/rules.csv, not here)
rules = pd.read_csv("data/portfolio/rules.csv").set_index("name")["value"]
max_position = rules["max_position"]
min_position = rules["min_position"]
max_bets = rules["max_bets"]
max_sector = rules["max_sector"]
months_before_limits = rules["months_before_limits"]
max_stocks = rules["max_stocks"]

# My products and my purchases (real file if it exists, otherwise the public one)
products = pd.read_csv("data/portfolio/products.csv")
file = "data/portfolio/transactions.csv"
if not os.path.exists(file):
    file = "data/portfolio/public/transactions.csv"
transactions = pd.read_csv(file)

# Exchange rates: one ticker for each currency that is not the euro (EURUSD=X, EURJPY=X...)
rate_tickers = []
for currency in products["currency"].unique():
    if currency != "EUR":
        rate_tickers.append("EUR" + currency + "=X")

# Today's price of each product in euros
last = yf.download(list(products["ticker"]) + rate_tickers, period="10d", progress=False)["Close"].ffill().iloc[-1]
prices_eur = []
for _, product in products.iterrows():
    price = last[product["ticker"]]
    if product["currency"] != "EUR":
        price = price / last["EUR" + product["currency"] + "=X"]
    prices_eur.append(price)
products["price_eur"] = prices_eur

# If Yahoo fails for a product, use the price I last paid for it
last_paid = transactions.groupby("isin")["price_eur"].last()
for i, product in products.iterrows():
    if pd.isna(product["price_eur"]) and product["isin"] in last_paid:
        print("No price today for", product["name"], "so I use my last purchase price")
        products.loc[i, "price_eur"] = last_paid[product["isin"]]

# Weight of each product I own
held = transactions.groupby("isin")["quantity"].sum().reset_index()
held = held.merge(products, on="isin")
held["value"] = held["quantity"] * held["price_eur"]
held["weight"] = held["value"] / held["value"].sum() * 100

alerts = []

# The weight limits only start after some months: a one-off buy makes the first months look off
months = pd.to_datetime(transactions["date"]).dt.strftime("%Y-%m").nunique()
limits_on = months >= months_before_limits

# Rule: no bet above the maximum weight
for _, row in held.iterrows():
    if limits_on and row["block"] in ["themes", "stocks"] and row["weight"] > max_position:
        alerts.append(["STOP BUYING", row["name"], f"It is {row['weight']:.1f}% of the portfolio, above {max_position:.0f}%. Move its monthly plan to VWCE"])

# Rule: no bet below the minimum weight (too small to change anything)
# Only products still in the plan (target above 0): one I stopped buying but still hold is fine
for _, row in held.iterrows():
    if limits_on and row["block"] in ["themes", "stocks"] and row["target"] > 0 and row["quantity"] > 0 and row["weight"] < min_position:
        alerts.append(["REVIEW", row["name"], f"It is {row['weight']:.1f}% of the portfolio, below {min_position:.0f}%. Raise its plan or replace it in the next review"])

# Rule: all bets together stay at or below the limit
bets = held[held["block"].isin(["themes", "stocks"])]["weight"].sum()
if limits_on and bets > max_bets:
    alerts.append(["STOP BUYING", "All bets", f"Bets are {bets:.1f}% of the portfolio, above {max_bets:.0f}%. New money goes to VWCE until they are back at {max_bets:.0f}%"])

# Rule: no sector above the limit (sector column in products.csv, VWCE does not count)
sectors = held.dropna(subset=["sector"]).groupby("sector")["weight"].sum()
for sector, weight in sectors.items():
    if limits_on and weight > max_sector:
        alerts.append(["STOP BUYING", "Sector " + sector, f"My stocks in this sector are {weight:.1f}% of the portfolio, above {max_sector:.0f}%. No new money in this sector: look for good companies in other sectors"])

# Rule: no more stocks than I can follow properly (rule 8), counting only stocks still in the plan (target above 0)
stocks_held = held[(held["block"] == "stocks") & (held["target"] > 0) & (held["quantity"] > 0)]
if len(stocks_held) > max_stocks:
    alerts.append(["REVIEW", "All stocks", f"I own {len(stocks_held)} stocks, above {max_stocks:.0f}. Pick which ones to drop in the next review"])

# Latest screener results (run future/future_screen.py first)
screen = pd.read_csv("data/future/future_screen.csv")
if "forward_pe" not in screen.columns:
    print("The screen is old: run future/future_screen.py first")
    exit()

# Rule: check the business of each stock I own
selling = []
for _, row in held[held["block"] == "stocks"].iterrows():
    match = screen[screen["name"] == row["name"]]
    name = row["name"]
    if len(match) == 0:
        alerts.append(["REVIEW", name, "Not in the screener. Yahoo may have failed for it this week, or add it to data/future/universe.csv with the same name"])
        continue
    company = match.iloc[0]

    # Each sign that the business is getting worse
    problems = []
    if company["quality"] < 4:
        problems.append(f"quality fell to {company['quality']} out of 5")
    if pd.notna(company["revenue_growth"]) and company["revenue_growth"] < 0:
        problems.append("revenue is falling")
    if pd.notna(company["growth_3y"]) and company["growth_3y"] < 0:
        problems.append("revenue is lower than 3 years ago")
    if pd.notna(company["net_debt_to_ebitda"]) and company["net_debt_to_ebitda"] > 4:
        problems.append(f"debt is {company['net_debt_to_ebitda']:.1f} times yearly profits")
    if pd.notna(company["dilution"]) and company["dilution"] > 0.05:
        problems.append(f"it adds {company['dilution'] * 100:.0f}% new shares a year")

    # One problem: look closer. Two or more: the business is breaking, time to sell
    if len(problems) == 1:
        alerts.append(["REVIEW", name, f"Warning sign: {problems[0]}. Check its alarms and the next results before doing anything"])
    if len(problems) >= 2:
        selling.append(name)
        alerts.append(["SELL", name, "The business is getting worse: " + ", ".join(problems) + ". If the next quarterly results confirm it, sell and move the money to VWCE or a better company. Never on the day of the news"])

# Fair prices from my own DCF (run future/fair_price.py first)
fair = pd.read_csv("data/future/fair_prices.csv")
keeps = []

# Rule: every stock in the plan gets one line: buy extra, keep buying or pause
for _, row in fair[fair["list"] == "portfolio"].iterrows():
    name = row["name"]
    product = products[products["name"] == name].iloc[0]
    weight = 0
    if name in list(held["name"]):
        weight = held[held["name"] == name]["weight"].iloc[0]

    # No extra buys if the stock or its sector is already above its limit
    full = limits_on and weight > max_position
    if limits_on and pd.notna(product["sector"]) and product["sector"] in sectors and sectors[product["sector"]] > max_sector:
        full = True

    if row["status"] == "BUY EXTRA" and not full:
        alerts.append(["BUY EXTRA", name, f"Price is {-row['gap']:.0f}% below my fair price ({row['fair']:.0f} {row['currency']}). Expected return {row['return']:.1f}% a year. A one-off buy from my personal budget makes sense if none of its alarms is on"])
    elif row["status"] == "SELL PART":
        alerts.append(["SELL PART", name, f"Price is {row['gap']:.0f}% above my fair price ({row['fair']:.0f} {row['currency']}) and the expected return is only {row['return']:.1f}% a year, less than VWCE. Sell up to half and move it to VWCE if the gain after the 28% tax is worth it. Keep the rest: a great business can stay expensive for years"])
    elif row["status"] == "PAUSE":
        alerts.append(["PAUSE", name, f"Price is {row['gap']:.0f}% above my fair price ({row['fair']:.0f} {row['currency']}). That is more than 10%, so no new money: its plan goes to VWCE until the price comes back. I keep the shares"])
    elif row["status"] == "NO PRICE":
        alerts.append(["REVIEW", name, "No price from Yahoo this week. Check the ticker in data/portfolio/fair_inputs.csv"])
    elif name not in selling:
        keeps.append(["KEEP", name, f"Price is {row['gap']:+.0f}% vs my fair price ({row['fair']:.0f} {row['currency']}). The monthly plan keeps going. Sell only if: {row['alarm']}"])

# Rule: a watchlist company reaches my entry price
for _, row in fair[fair["list"] == "watchlist"].iterrows():
    if row["status"] == "BUY":
        alerts.append(["BUY", row["name"], f"Now at {row['price']:.0f} {row['currency']}, at or below my entry price of {row['entry']:.0f}. Write the full analysis before buying"])

# The KEEP lines go last: they are not a call to action
alerts = alerts + keeps

# Save the alerts for the dashboard and for GitHub
today = str(date.today())
os.makedirs("data/alerts", exist_ok=True)
if len(alerts) == 0:
    alerts.append(["OK", "-", "No alerts. Nothing to do"])
table = pd.DataFrame(alerts, columns=["type", "product", "message"])
table.insert(0, "date", today)

# Last week's alerts: only the type and the product count, the numbers in the message move every week
last_week = []
if os.path.exists("data/alerts/alerts.csv"):
    old = pd.read_csv("data/alerts/alerts.csv")
    for _, row in old.iterrows():
        last_week.append(row["type"] + " " + row["product"])
this_week = []
for _, row in table.iterrows():
    this_week.append(row["type"] + " " + row["product"])
changed = sorted(this_week) != sorted(last_week)
table.to_csv("data/alerts/alerts.csv", index=False)

# Text for the GitHub issue
lines = ["# Portfolio check " + today, ""]
if table["type"].iloc[0] == "OK":
    lines.append("No alerts. Nothing to do.")
else:
    lines.append("ALERTS FOUND")
    if changed:
        lines.append("ALERTS CHANGED SINCE LAST WEEK")
    lines.append("")
    for _, row in table.iterrows():
        new = ""
        if row["type"] + " " + row["product"] not in last_week:
            new = " (new)"
        lines.append("- **" + row["type"] + "** " + row["product"] + new + ": " + row["message"])
lines.append("")
lines.append(f"Bets are {bets:.1f}% of the portfolio (limit {max_bets:.0f}%).")
if not limits_on:
    lines.append(f"Weight limits start after {months_before_limits:.0f} months of buying. Now: {months}.")
open("data/alerts/latest.md", "w").write("\n".join(lines))

print("\n".join(lines))
