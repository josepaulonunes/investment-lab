import yfinance as yf
import pandas as pd
import numpy as np
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Settings: the bets are 30% of the portfolio, each one between 2% and 5%
bets_total = 0.30
min_weight = 0.02
max_weight = 0.05
risk_free = 0.02
monthly_money = 600
simulations = 50000

# The bets: 5 stocks and 4 theme ETFs (ticker on Yahoo and currency)
assets = {
    "TSMC": ["TSM", "USD"],
    "Mastercard": ["MA", "USD"],
    "Broadcom": ["AVGO", "USD"],
    "Nvidia": ["NVDA", "USD"],
    "Intuitive Surgical": ["ISRG", "USD"],
    "Health ETF": ["XDWH.DE", "EUR"],
    "Grid ETF": ["GRID.DE", "EUR"],
    "Quantum ETF": ["QUTM.DE", "EUR"],
    "Nuclear ETF": ["NUKL.DE", "EUR"],
}

# Daily prices for the last 3 years
tickers = [assets[name][0] for name in assets]
prices = yf.download(tickers + ["EURUSD=X"], period="3y", progress=False)["Close"].ffill()

# Put every price in euros (I invest in euros)
euro_prices = pd.DataFrame()
for name in assets:
    ticker, currency = assets[name]
    if currency == "USD":
        euro_prices[name] = prices[ticker] / prices["EURUSD=X"]
    else:
        euro_prices[name] = prices[ticker]

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

# Monte Carlo: try many random mixes, each asset between 2% and 5%, all together 30%
names = list(assets.keys())
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

# Simple rule to compare: more weight to the calmer assets (inverse risk), kept between 2% and 5%
inverse = (1 / yearly_risk) / (1 / yearly_risk).sum() * bets_total
inverse = inverse.clip(min_weight, max_weight)
inverse = inverse / inverse.sum() * bets_total

# Show the three options
options = pd.DataFrame({
    "best_sharpe_%": best[0] * 100,
    "calmest_%": calm[0] * 100,
    "inverse_risk_%": inverse.values * 100,
}, index=names)
options["best_eur_month"] = best[0] * monthly_money
print()
print("WEIGHTS IN % OF THE WHOLE PORTFOLIO (bets = 30%)")
print(options.round(1).to_string())
print()
print("Best Sharpe mix: return", round(best[1] * 100, 1), "% a year, risk", round(best[2] * 100, 1), "%, Sharpe", round(best[3], 2))
print("Calmest mix: return", round(calm[1] * 100, 1), "% a year, risk", round(calm[2] * 100, 1), "%, Sharpe", round(calm[3], 2))
print("Mixes tested:", len(results))
