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
max_group = rules["max_group"]
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
for _, row in held.iterrows():
    if limits_on and row["block"] in ["themes", "stocks"] and row["quantity"] > 0 and row["weight"] < min_position:
        alerts.append(["REVIEW", row["name"], f"It is {row['weight']:.1f}% of the portfolio, below {min_position:.0f}%. Raise its plan or replace it in January"])

# Rule: all bets together stay at or below the limit
bets = held[held["block"].isin(["themes", "stocks"])]["weight"].sum()
if limits_on and bets > max_bets:
    alerts.append(["STOP BUYING", "All bets", f"Bets are {bets:.1f}% of the portfolio, above {max_bets:.0f}%. New money goes to VWCE until they are back at {max_bets:.0f}%"])

# Rule: products that depend on the same thing count as one bet (group column in products.csv)
groups = held.dropna(subset=["group"]).groupby("group")["weight"].sum()
for group, weight in groups.items():
    if limits_on and weight > max_group:
        alerts.append(["STOP BUYING", "Group " + group, f"Together they are {weight:.1f}% of the portfolio, above {max_group:.0f}%. No extra buys in this group"])

# Rule: no more stocks than I can follow properly (rule 8)
stocks_held = held[(held["block"] == "stocks") & (held["quantity"] > 0)]
if len(stocks_held) > max_stocks:
    alerts.append(["REVIEW", "All stocks", f"I own {len(stocks_held)} stocks, above {max_stocks:.0f}. Pick which ones to drop in January"])

# Latest screener results (run future/future_screen.py first)
screen = pd.read_csv("data/future/future_screen.csv")
if "forward_pe" not in screen.columns:
    print("The screen is old: run future/future_screen.py first")
    exit()

# Rule: check the business and the price of each stock I own
for _, row in held[held["block"] == "stocks"].iterrows():
    match = screen[screen["name"] == row["name"]]
    name = row["name"]
    if len(match) == 0:
        alerts.append(["REVIEW", name, "Not in the screener. Add it to data/future/universe.csv with the same name"])
        continue
    company = match.iloc[0]
    if company["quality"] < 4:
        alerts.append(["REVIEW", name, f"Quality fell to {company['quality']} out of 5. Check if the business is getting worse"])
    if pd.notna(company["growth_3y"]) and company["growth_3y"] < 0:
        alerts.append(["REVIEW", name, "Revenue is lower than 3 years ago"])
    if pd.notna(company["net_debt_to_ebitda"]) and company["net_debt_to_ebitda"] > 4:
        alerts.append(["REVIEW", name, f"Debt is {company['net_debt_to_ebitda']:.1f} times yearly profits, above 4"])
    if pd.notna(company["dilution"]) and company["dilution"] > 0.05:
        alerts.append(["REVIEW", name, f"It adds {company['dilution'] * 100:.0f}% new shares a year, above 5%"])

    # Price alerts only when the DCF can be trusted for this company (verdict CHECK means it cannot)
    if company["verdict"] != "CHECK" and pd.notna(company["buy_below"]) and company["buy_below"] > 0:
        if company["price"] > company["fair_high"]:
            alerts.append(["EXPENSIVE", name, f"Price is above even the optimistic fair price ({company['fair_high']:.0f}): it assumes today's growth for more than 10 years. Keep the plan and review it in January"])
        # No extra buys if its group is already above the group limit (rule 15)
        group_full = limits_on and pd.notna(row["group"]) and groups[row["group"]] > max_group
        if company["price"] < company["buy_below"] and row["weight"] < max_position and not group_full:
            alerts.append(["BUY EXTRA", name, f"Price is {(1 - company['price'] / company['buy_below']) * 100:.0f}% below the careful fair price ({company['buy_below']:.0f}). A one-off buy from my personal budget makes sense"])

# Rule: a watchlist company reaches its fair price
watchlist = pd.read_csv("data/future/watchlist.csv")
for _, row in watchlist.iterrows():
    match = screen[screen["ticker"] == row["ticker"]]
    if len(match) == 0:
        continue
    company = match.iloc[0]
    if company["verdict"] == "BUY":
        alerts.append(["BUY", row["name"], f"Now at {company['price']:.0f}, below its careful fair price of {company['buy_below']:.0f}. Candidate for the January review"])

# Save the alerts for the dashboard and for GitHub
today = str(date.today())
os.makedirs("data/alerts", exist_ok=True)
if len(alerts) == 0:
    alerts.append(["OK", "-", "No alerts. Nothing to do"])
table = pd.DataFrame(alerts, columns=["type", "product", "message"])
table.insert(0, "date", today)
table.to_csv("data/alerts/alerts.csv", index=False)

# Text for the GitHub issue
lines = ["# Portfolio check " + today, ""]
if table["type"].iloc[0] == "OK":
    lines.append("No alerts. Nothing to do.")
else:
    lines.append("ALERTS FOUND")
    lines.append("")
    for _, row in table.iterrows():
        lines.append("- **" + row["type"] + "** " + row["product"] + ": " + row["message"])
lines.append("")
lines.append(f"Bets are {bets:.1f}% of the portfolio (limit {max_bets:.0f}%).")
if not limits_on:
    lines.append(f"Weight limits start after {months_before_limits:.0f} months of buying. Now: {months}.")
open("data/alerts/latest.md", "w").write("\n".join(lines))

print("\n".join(lines))
