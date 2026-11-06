import pandas as pd
import matplotlib.pyplot as plt

# Load data
metrics = pd.read_csv("data/house_view/metrics.csv", index_col=0)
valuation = pd.read_csv("data/house_view/valuation.csv", index_col=0)
data = metrics.join(valuation)

# World and USA are only references, not candidates
candidates = data.drop(["World", "USA"])

# Z-score: distance from the average in standard deviations
def zscore(series):
    return (series - series.mean()) / series.std()

# Valuation score: cheaper is better
value = (
    zscore(-candidates["pe"])
    + zscore(-candidates["pe_forward"])
    + zscore(-candidates["pb"])
    + zscore(candidates["div_yield"])
) / 4

# Momentum score
momentum = zscore(candidates["momentum_12_1"])

# Final score: 50% value, 50% momentum
scores = pd.DataFrame({"value": value, "momentum": momentum})
scores["final"] = 0.5 * scores["value"] + 0.5 * scores["momentum"]
scores["pe_fwd_vs_pe"] = candidates["pe_forward"] / candidates["pe"]
scores = scores.sort_values("final", ascending=False)

scores.to_csv("data/house_view/scores.csv")
print(scores.round(2))

# Chart
scores["final"].sort_values().plot(kind="barh", color="grey")
plt.title("House view v0: value + momentum")
plt.tight_layout()
plt.savefig("notes/scores.png")
plt.show()