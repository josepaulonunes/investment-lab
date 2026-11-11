import pandas as pd
import matplotlib.pyplot as plt

# Load prices and compute monthly returns
prices = pd.read_csv("data/house_view/prices_eur.csv", index_col=0, parse_dates=True)
returns = prices.pct_change()

# Metrics for each region
results = {}
for region in prices.columns:
    p = prices[region].dropna()
    r = returns[region].dropna()

    if len(p) < 24:
        print("Not enough data for", region)
        continue

    years = len(r) / 12
    annual_return = (p.iloc[-1] / p.iloc[0]) ** (1 / years) - 1
    volatility = r.std() * 12 ** 0.5
    max_drawdown = (p / p.cummax() - 1).min()
    momentum = p.iloc[-2] / p.iloc[-13] - 1
    correlation = r.corr(returns["World"])

    results[region] = {
        "start": p.index[0].date(),
        "annual_return": annual_return,
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "momentum_12_1": momentum,
        "corr_world": correlation,
    }

# Save the table
table = pd.DataFrame(results).T
table.to_csv("data/house_view/metrics.csv")
print(table)

# Chart: momentum by region
table["momentum_12_1"].astype(float).sort_values().plot(kind="barh", color="grey")
plt.title("Momentum 12-1 in EUR")
plt.tight_layout()
plt.savefig("notes/momentum.png")
plt.show()