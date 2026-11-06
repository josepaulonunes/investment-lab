import yfinance as yf
import pandas as pd
import warnings
from datetime import date

# Hide library warnings and show wide tables
warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

# Choose the company to analyse (must be in data/companies/companies.csv)
company = "adobe"

# Load company files
folder = "data/companies/" + company + "/"
companies = pd.read_csv("data/companies/companies.csv", index_col="name")
ticker = companies.loc[company, "ticker"]
peer_tickers = companies.loc[company, "peers"].split(";")
accounts = pd.read_csv(folder + "accounts.csv", index_col="year")
assumptions = pd.read_csv(folder + "assumptions.csv", index_col="scenario")

# Market data
info = yf.Ticker(ticker).info
price = info.get("currentPrice")
market_cap = info.get("marketCap") / 1e6
shares = market_cap / price
print(company.upper(), "| price", price, "| market cap", round(market_cap / 1000, 1), "bn")

# 1. Ratios from the accounts
ratios = pd.DataFrame(index=accounts.index)
ratios["revenue_growth"] = accounts["revenue"].pct_change()
ratios["ebitda_margin"] = accounts["adj_ebitda"] / accounts["revenue"]
ratios["fcf_margin"] = accounts["fcf"] / accounts["revenue"]
ratios["fcf_to_net_income"] = accounts["fcf"] / accounts["net_income"]
ratios["net_debt_to_ebitda"] = accounts["net_debt"] / accounts["adj_ebitda"]
ratios["roe"] = accounts["net_income"] / accounts["equity"]
ratios["roic"] = accounts["ebit"] * (1 - 0.25) / (accounts["equity"] + accounts["net_debt"])
ratios.to_csv(folder + "ratios.csv")
print()
print("RATIOS")
print(ratios.round(3).T)

# 2. DCF: 10 years of free cash flow plus a terminal value
def dcf_value(fcf, growth_1_5, growth_6_10, terminal, discount):
    value = 0
    cash = fcf
    for year in range(1, 11):
        if year <= 5:
            cash = cash * (1 + growth_1_5)
        else:
            cash = cash * (1 + growth_6_10)
        value = value + cash / (1 + discount) ** year
    terminal_value = cash * (1 + terminal) / (discount - terminal)
    value = value + terminal_value / (1 + discount) ** 10
    return value

results = {}
for scenario, s in assumptions.iterrows():
    value = dcf_value(s["fcf"], s["growth_1_5"], s["growth_6_10"], s["terminal"], s["discount"])
    results[scenario] = {"fair_price": value / shares, "upside": value / market_cap - 1}
dcf = pd.DataFrame(results).T
dcf.to_csv(folder + "dcf.csv")
print()
print("DCF")
print(dcf.round(2))

# 3. Reverse DCF: growth per year (10 years) that today's price already assumes
central = assumptions.loc["central"]
implied_growth = None
for step in range(-50, 401):
    growth = step / 1000
    value = dcf_value(central["fcf"], growth, growth, central["terminal"], central["discount"])
    if value >= market_cap:
        implied_growth = growth
        break
print()
print("Growth per year the price already assumes:", implied_growth)

# 4. Sensitivity: fair price when growth (both periods) and discount rate move around the central case
growth_changes = [-0.04, -0.02, 0, 0.02, 0.04]
discounts = []
for change in [-0.01, -0.005, 0, 0.005, 0.01]:
    discounts.append(round(central["discount"] + change, 3))

sensitivity = pd.DataFrame(columns=discounts)
for change in growth_changes:
    g1 = round(central["growth_1_5"] + change, 3)
    g2 = round(central["growth_6_10"] + change, 3)
    for d in discounts:
        value = dcf_value(central["fcf"], g1, g2, central["terminal"], d)
        sensitivity.loc[g1, d] = round(value / shares)
sensitivity.index.name = "growth y1-5 / discount"
sensitivity.to_csv(folder + "sensitivity.csv")
print()
print("SENSITIVITY (fair price)")
print(sensitivity)

# 5. Peers: market multiples
rows = {}
for t in [ticker] + peer_tickers:
    peer_info = yf.Ticker(t).info
    rows[t] = {
        "currency": peer_info.get("currency"),
        "pe_forward": peer_info.get("forwardPE"),
        "ev_ebitda": peer_info.get("enterpriseToEbitda"),
        "ebitda_margin": peer_info.get("ebitdaMargins"),
        "revenue_growth": peer_info.get("revenueGrowth"),
        "roe": peer_info.get("returnOnEquity"),
    }
peers = pd.DataFrame(rows).T
peers.to_csv(folder + "peers.csv")
print()
print("PEERS")
print(peers)

# 6. Risk: how much the share moved in the last 5 years, compared with VWCE
prices = yf.download([ticker, "VWCE.DE"], period="5y", interval="1wk", progress=False)["Close"].dropna()
returns = prices.pct_change().dropna()
risk = pd.DataFrame(index=[ticker, "VWCE.DE"])
risk["volatility"] = returns.std() * 52 ** 0.5
risk["max_drawdown"] = (prices / prices.cummax() - 1).min()
risk["correlation_vwce"] = returns.corr()["VWCE.DE"]
print()
print("RISK (last 5 years, weekly)")
print(risk.round(2))

# 7. My criteria (from IPS.md)
years = len(accounts) - 1
revenue_cagr = (accounts["revenue"].iloc[-1] / accounts["revenue"].iloc[0]) ** (1 / years) - 1
buy_price = dcf.loc["central", "fair_price"] * 0.85
last = ratios.iloc[-1]

checks = {
    "ROIC above 12% (average of last 3 years)": ratios["roic"].tail(3).mean() > 0.12,
    "Net debt below 2.5x EBITDA": last["net_debt_to_ebitda"] < 2.5,
    "Positive FCF in at least 4 of 5 years": (accounts["fcf"] > 0).sum() >= 4,
    "EBITDA margin at or above its 5 year average": last["ebitda_margin"] >= ratios["ebitda_margin"].mean(),
    "Revenue growth above 5% a year": revenue_cagr > 0.05,
    "Price at least 15% below central fair price": price <= buy_price,
    "Price assumes less growth than history": implied_growth is not None and implied_growth < revenue_cagr,
}

print()
print("MY CRITERIA")
for name, passed in checks.items():
    if passed:
        print("PASS |", name)
    else:
        print("FAIL |", name)

# 8. Verdict: the first 5 criteria are quality, the last 2 are price
quality_fails = list(checks.values())[:5].count(False)
if all(checks.values()):
    verdict = "BUY"
elif quality_fails <= 1:
    verdict = "WATCH"
else:
    verdict = "AVOID"
print()
print("Revenue growth per year (history):", round(revenue_cagr, 3))
print("Buy price:", round(buy_price, 2), "| today:", price)
print("VERDICT:", verdict)

# 9. One line summary, saved next to the other companies to compare them
summary_file = "data/companies/summary.csv"
new_row = pd.DataFrame([{
    "company": company,
    "date": date.today(),
    "price": price,
    "fair_price_central": round(dcf.loc["central", "fair_price"], 2),
    "buy_price": round(buy_price, 2),
    "upside_central": round(dcf.loc["central", "upside"], 3),
    "implied_growth": implied_growth,
    "revenue_cagr": round(revenue_cagr, 3),
    "pe_forward": info.get("forwardPE"),
    "ev_ebitda": info.get("enterpriseToEbitda"),
    "roic_last": round(ratios["roic"].iloc[-1], 3),
    "fcf_margin_last": round(ratios["fcf_margin"].iloc[-1], 3),
    "volatility": round(risk.loc[ticker, "volatility"], 3),
    "max_drawdown": round(risk.loc[ticker, "max_drawdown"], 3),
    "criteria_passed": list(checks.values()).count(True),
    "verdict": verdict,
}])
try:
    summary = pd.read_csv(summary_file)
    summary = summary[summary["company"] != company]
    summary = pd.concat([summary, new_row])
except FileNotFoundError:
    summary = new_row
summary.to_csv(summary_file, index=False)
print()
print("SUMMARY OF ALL COMPANIES")
print(summary.to_string(index=False))