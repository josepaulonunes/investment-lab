import pandas as pd

# My real purchases (private file, never on GitHub)
real = pd.read_csv("data/portfolio/transactions.csv")

# Scale everything so the money I put in adds up to 100: weights and returns stay the same, the euros disappear
factor = 100 / (real["amount_eur"].sum() + real["fee_eur"].sum())
public = real.copy()
public["quantity"] = (public["quantity"] * factor).round(6)
public["amount_eur"] = (public["amount_eur"] * factor).round(4)
public["fee_eur"] = (public["fee_eur"] * factor).round(4)

# Save the public file (this one goes to GitHub and to the live app)
public.to_csv("data/portfolio/public/transactions.csv", index=False)
print("Public file saved with", len(public), "purchases")
