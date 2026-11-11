import yfinance as yf
import pandas as pd

# Regions and the ETF used as reference for each one
regions = {
    "World": "ACWI",
    "Emerging": "EEM",
    "India": "INDA",
    "China": "MCHI",
    "Taiwan": "EWT",
    "Korea": "EWY",
    "Brazil": "EWZ",
    "Mexico": "EWW",
    "Japan": "EWJ",
    "Europe": "VGK",
    "USA": "SPY",
}

# Download monthly prices in dollars
tickers = list(regions.values())
data = yf.download(tickers, start="2010-01-01", interval="1mo", auto_adjust=True)
prices_usd = data["Close"]

# Download the euro to dollar rate
fx = yf.download("EURUSD=X", start="2010-01-01", interval="1mo", auto_adjust=True)
eurusd = fx["Close"].squeeze()

# Convert prices to euros
prices_eur = prices_usd.div(eurusd, axis=0)

# Use region names instead of tickers
names = {}
for region, ticker in regions.items():
    names[ticker] = region
prices_eur = prices_eur.rename(columns=names)
prices_eur = prices_eur[list(regions.keys())]

# Save
prices_eur.to_csv("archive/data/house_view/prices_eur.csv")
print(prices_eur.tail())