import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Prices of Prysmian and VWCE (both in EUR)
tickers = {"Prysmian": "PRY.MI", "VWCE": "VWCE.DE"}
data = yf.download(list(tickers.values()), start="2021-01-01", interval="1wk", auto_adjust=True)
prices = data["Close"].dropna()

names = {}
for name, ticker in tickers.items():
    names[ticker] = name
prices = prices.rename(columns=names)

# Growth of 100 EUR invested
growth = prices / prices.iloc[0] * 100
growth.plot()
plt.title("100 EUR invested in 2021")
plt.ylabel("EUR")
plt.tight_layout()
plt.savefig("notes/companies/prysmian_vs_vwce.png")
plt.show()

# Quick valuation snapshot
company = yf.Ticker("PRY.MI")
info = company.info
snapshot = {
    "price": info.get("currentPrice"),
    "market_cap_bn": info.get("marketCap", 0) / 1e9,
    "pe": info.get("trailingPE"),
    "pe_forward": info.get("forwardPE"),
    "ev_ebitda": info.get("enterpriseToEbitda"),
    "price_to_book": info.get("priceToBook"),
    "dividend_yield": info.get("dividendYield"),
}
print(pd.Series(snapshot).round(2))

# Income statement of the last years
income = company.income_stmt
rows = ["Total Revenue", "EBITDA", "Net Income"]
income = income.loc[income.index.intersection(rows)] / 1e6
income.to_csv("data/companies/prysmian/income_first_look.csv")
print(income.round(0))