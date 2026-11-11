import pandas as pd

# My real purchases (private file, never on GitHub)
real = pd.read_csv("data/portfolio/transactions.csv")

# Scale the purchases so they add up to 100: weights and returns stay the same, the euros disappear
factor = 100 / real["amount_eur"].sum()
public = real.copy()
public["quantity"] = (public["quantity"] * factor).round(6)
public["amount_eur"] = (public["amount_eur"] * factor).round(4)

# Fees stay out: the broker fee is a fixed amount, so a scaled fee would show how much I invest
public["fee_eur"] = 0.0

# Save the public file (this one goes to GitHub and to the live app)
public.to_csv("data/portfolio/public/transactions.csv", index=False)
print("Public file saved with", len(public), "purchases")
