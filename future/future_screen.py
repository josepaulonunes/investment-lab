import yfinance as yf
import pandas as pd
import warnings
from datetime import date

# Hide library warnings and show wide tables
warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)

# Settings
discount = 0.09
terminal = 0.025
max_growth = 0.25
monthly_budget = 15

# Same DCF as the screener: 10 years of free cash flow plus a terminal value
def dcf_value(fcf, growth):
    value = 0
    cash = fcf
    for year in range(1, 11):
        cash = cash * (1 + growth)
        value = value + cash / (1 + discount) ** year
    terminal_value = cash * (1 + terminal) / (discount - terminal)
    value = value + terminal_value / (1 + discount) ** 10
    return value

# Companies linked to AI, chips, power and nuclear (add a line to the csv to add one)
universe = pd.read_csv("data/future/universe.csv")

rows = []
for _, company in universe.iterrows():
    print("Loading", company["name"])
    stock = yf.Ticker(company["ticker"])
    info = stock.info
    market_cap = info.get("marketCap")
    price = info.get("currentPrice")
    if not market_cap or not price:
        print("No data for", company["name"], "- check the ticker")
        continue

    # Revenue growth over the last full year (more stable than the last quarter)
    growth = info.get("revenueGrowth")
    income = stock.income_stmt
    if "Total Revenue" in income.index:
        revenue = income.loc["Total Revenue"].dropna()
        if len(revenue) >= 2:
            growth = revenue.iloc[0] / revenue.iloc[1] - 1

    # Free cash flow from the last annual cash flow statement
    fcf = None
    cashflow = stock.cashflow
    if "Free Cash Flow" in cashflow.index:
        values = cashflow.loc["Free Cash Flow"].dropna()
        if len(values) > 0:
            fcf = values.iloc[0]

    # Debt compared with yearly profits (negative means more cash than debt)
    net_debt_to_ebitda = None
    ebitda = info.get("ebitda")
    if ebitda and ebitda > 0:
        net_debt_to_ebitda = ((info.get("totalDebt") or 0) - (info.get("totalCash") or 0)) / ebitda
    margin = info.get("operatingMargins")

    # Quality: is it a good business?
    checks = [
        growth is not None and growth > 0.10,
        margin is not None and margin > 0.10,
        fcf is not None and fcf > 0,
        net_debt_to_ebitda is not None and net_debt_to_ebitda < 3,
    ]
    quality = checks.count(True)

    # Price: growth per year the price assumes vs growth the company shows today (capped at 25%)
    same_currency = info.get("financialCurrency") == info.get("currency")
    implied_growth = None
    buy_below = None
    growth_used = None
    if fcf and fcf > 0 and same_currency and growth is not None:
        for step in range(-50, 601):
            g = step / 1000
            if dcf_value(fcf, g) >= market_cap:
                implied_growth = g
                break
        growth_used = min(growth, max_growth)
        shares = market_cap / price
        buy_below = dcf_value(fcf, growth_used) / shares

    # Verdict
    if fcf is None or fcf <= 0:
        verdict = "SPECULATIVE"
    elif quality < 3:
        verdict = "AVOID"
    elif not same_currency:
        verdict = "CHECK"
    elif buy_below is not None and price <= buy_below:
        verdict = "BUY"
    else:
        verdict = "WATCH"

    # Warnings
    warning = ""
    if not same_currency:
        warning = "Reports in another currency: check by hand"
    if growth is not None and growth > 0.4:
        warning = "Growth over 40%: cycle peak?"

    rows.append({
        "name": company["name"],
        "link": company["link"],
        "price": price,
        "currency": info.get("currency"),
        "revenue_growth": growth,
        "op_margin": margin,
        "net_debt_to_ebitda": net_debt_to_ebitda,
        "implied_growth": implied_growth,
        "growth_used": growth_used,
        "buy_below": buy_below,
        "quality": quality,
        "verdict": verdict,
        "warning": warning,
    })

# Rank: BUY first, then the cheapest compared with its growth
screen = pd.DataFrame(rows)
order = {"BUY": 0, "WATCH": 1, "CHECK": 2, "SPECULATIVE": 3, "AVOID": 4}
screen["rank"] = screen["verdict"].map(order)
screen["price_vs_growth"] = screen["implied_growth"] / screen["growth_used"]
screen = screen.sort_values(["rank", "price_vs_growth"]).drop(columns="rank")
screen.to_csv("data/future/future_screen.csv", index=False)
screen.to_csv("data/future/future_screen_" + str(date.today()) + ".csv", index=False)
print()
print("FUTURE STUDY (quality out of 4)")
print(screen.round(2).to_string(index=False))

# Suggested monthly plan: the best BUY without warnings in each link of the chain, the rest in WTAI
picks = screen[(screen["verdict"] == "BUY") & (screen["warning"] == "")].drop_duplicates("link")
print()
print("SUGGESTED PLAN FOR THE", str(monthly_budget) + "% FUTURE BLOCK (% of the monthly money)")
if len(picks) >= 4:
    each = monthly_budget / len(picks)
    wtai = 0
else:
    each = monthly_budget / 2 / max(len(picks), 1)
    wtai = monthly_budget - each * len(picks)
for _, pick in picks.iterrows():
    print(pick["name"], "(" + pick["link"] + "):", round(each, 1), "%")
print("WTAI:", round(wtai, 1), "%")
