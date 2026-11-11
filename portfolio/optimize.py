import yfinance as yf
import pandas as pd
import numpy as np
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Limits for each bet (from data/portfolio/rules.csv)
rules = pd.read_csv("data/portfolio/rules.csv").set_index("name")["value"]
min_weight = rules["min_position"] / 100
max_weight = rules["max_position"] / 100
risk_free = 0.02
simulations = 50000

# The bets: every stock and theme ETF with a target in data/portfolio/products.csv
products = pd.read_csv("data/portfolio/products.csv")
bets = products[products["block"].isin(["themes", "stocks"]) & (products["target"] > 0)]
bets_total = bets["target"].sum() / 100
names = list(bets["name"])

# Exchange rates: one ticker for each currency that is not the euro (EURUSD=X, EURJPY=X...)
rate_tickers = []
for currency in bets["currency"].unique():
    if currency != "EUR":
        rate_tickers.append("EUR" + currency + "=X")

# Daily prices for the last 3 years
prices = yf.download(list(bets["ticker"]) + rate_tickers, period="3y", progress=False)["Close"].ffill()

# Put every price in euros (I invest in euros)
euro_prices = pd.DataFrame()
for _, bet in bets.iterrows():
    if bet["currency"] != "EUR":
        euro_prices[bet["name"]] = prices[bet["ticker"]] / prices["EUR" + bet["currency"] + "=X"]
    else:
        euro_prices[bet["name"]] = prices[bet["ticker"]]

# Yearly return and risk of each asset
returns = euro_prices.pct_change()
yearly_return = returns.mean() * 252
yearly_risk = returns.std() * np.sqrt(252)
covariance = returns.cov() * 252

# Past returns are a bad guess of the future: use half the asset's own return and half the average of all, capped at 30%
expected = (0.5 * yearly_return + 0.5 * yearly_return.mean()).clip(upper=0.30)

print("EACH ASSET (in euros, last 3 years or since launch)")
table = pd.DataFrame({"past_return": yearly_return, "risk": yearly_risk, "return_used": expected})
print((table * 100).round(1).to_string())

# How much the bets move together (1 = always together, 0 = no link). Low numbers are what diversifies
print()
print("CORRELATION BETWEEN THE BETS")
print(returns.corr().round(2).to_string())

# Monte Carlo: try many random mixes, each asset between the minimum and the maximum weight
results = []
for i in range(simulations):
    extra = np.random.dirichlet(np.ones(len(names))) * (bets_total - min_weight * len(names))
    weights = min_weight + extra
    if weights.max() > max_weight:
        continue
    mix_return = (weights * expected.values).sum() / bets_total
    mix_risk = np.sqrt(weights @ covariance.values @ weights) / bets_total
    sharpe = (mix_return - risk_free) / mix_risk
    results.append([weights, mix_return, mix_risk, sharpe])

# Best mix: highest return for each unit of risk (Sharpe), and the calmest mix
best = max(results, key=lambda r: r[3])
calm = min(results, key=lambda r: r[2])

# Simple rule to compare: more weight to the calmer assets (inverse risk), kept between the limits
inverse = (1 / yearly_risk) / (1 / yearly_risk).sum() * bets_total
inverse = inverse.clip(min_weight, max_weight)
inverse = inverse / inverse.sum() * bets_total

# Show the three options next to my targets
options = pd.DataFrame({
    "my_target_%": bets["target"].values,
    "best_sharpe_%": best[0] * 100,
    "calmest_%": calm[0] * 100,
    "inverse_risk_%": inverse.values * 100,
}, index=names)
print()
print("WEIGHTS IN % OF THE WHOLE PORTFOLIO (bets =", round(bets_total * 100), "%)")
print(options.round(1).to_string())
print()
print("Best Sharpe mix: return", round(best[1] * 100, 1), "% a year, risk", round(best[2] * 100, 1), "%, Sharpe", round(best[3], 2))
print("Calmest mix: return", round(calm[1] * 100, 1), "% a year, risk", round(calm[2] * 100, 1), "%, Sharpe", round(calm[3], 2))
print("Mixes tested:", len(results))
