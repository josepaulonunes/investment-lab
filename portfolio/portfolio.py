import pandas as pd
import os
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Targets and rules (from IPS.md)
targets = {"core": 0.75, "small": 0.10, "future": 0.12, "gold": 0.03}
monthly_contribution = 100
band = 0.03

# Use my real data if it exists, otherwise the example data
folder = "data/portfolio/"
if not os.path.exists(folder + "transactions.csv"):
    folder = "data/portfolio/example/"
    print("Using example data")

# Load data
transactions = pd.read_csv(folder + "transactions.csv")
prices = pd.read_csv(folder + "current_prices.csv")
cash = pd.read_csv(folder + "cash.csv")

# Stop if there are no purchases or cash data yet
if len(transactions) == 0 or len(cash) == 0:
    print("No data yet: fill transactions.csv, current_prices.csv and cash.csv first")
    exit()
cash = cash.iloc[-1]

# Positions: total quantity and money invested per product
positions = transactions.groupby(["isin", "name", "block"]).agg(
    quantity=("quantity", "sum"),
    invested=("amount_eur", "sum"),
    fees=("fee_eur", "sum"),
).reset_index()

# Current value and gain
positions = positions.merge(prices[["isin", "price_eur"]], on="isin")
positions["value"] = positions["quantity"] * positions["price_eur"]
positions["gain"] = positions["value"] - positions["invested"] - positions["fees"]
positions["gain_pct"] = positions["gain"] / positions["invested"]

total = positions["value"].sum()
positions["weight"] = positions["value"] / total

print("POSITIONS")
print(positions[["name", "block", "invested", "value", "gain", "gain_pct", "weight"]].round(3))
print("Total invested:", round(positions["invested"].sum(), 2), "EUR")
print("Total value:", round(total, 2), "EUR")

# Weights by block vs targets
blocks = positions.groupby("block")["value"].sum() / total
print()
print("BLOCKS VS TARGETS")
for block, target in targets.items():
    weight = blocks.get(block, 0)
    gap = weight - target
    flag = "REBALANCE" if abs(gap) > band else "ok"
    print(block, "| weight", round(weight * 100, 1), "% | target", target * 100, "% |", flag)

# Cash rule: cash must cover the emergency fund plus short term savings
print()
print("CASH RULE")
minimum_cash = cash["emergency"] + cash["savings"]
if cash["tr_cash"] >= minimum_cash:
    print("ok:", cash["tr_cash"], "EUR in cash, minimum", minimum_cash, "EUR")
else:
    print("WARNING:", cash["tr_cash"], "EUR in cash, minimum", minimum_cash, "EUR")

# Suggested split of next month's money to move back towards targets
print()
print("SUGGESTED SPLIT OF NEXT MONTH (for every 100 EUR)")
new_total = total + monthly_contribution
needs = {}
for block, target in targets.items():
    current = blocks.get(block, 0) * total
    needs[block] = max(0, new_total * target - current)
total_needs = sum(needs.values())
for block in targets:
    amount = monthly_contribution * needs[block] / total_needs
    print(block, ":", round(amount), "EUR")
