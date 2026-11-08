import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# My monthly plan: isin, name, block, Yahoo ticker, euros for every 100 EUR invested
plan = [
    ["IE00BK5BQT80", "Vanguard FTSE All-World", "core", "VWCE.DE", 72],
    ["IE00BF4RFH31", "iShares MSCI World Small Cap", "small", "IUSN.DE", 10],
    ["IE00BDVPNG13", "WisdomTree Artificial Intelligence", "future", "WTAI.MI", 2],
    ["IE000J80JTL1", "First Trust Smart Grid Infrastructure", "future", "GRID.DE", 4],
    ["IE000M7V94E1", "VanEck Uranium and Nuclear", "future", "NUKL.DE", 2],
    ["IE00BM67HK77", "Xtrackers MSCI World Health Care", "future", "XDWH.DE", 4],
    ["IE00BM67HS53", "Xtrackers MSCI World Materials", "future", "XDWM.DE", 3],
    ["IE00B579F325", "Invesco Physical Gold", "gold", "8PSG.DE", 3],
]

# Real daily prices for the last 12 months
tickers = [row[3] for row in plan]
prices = yf.download(tickers, start="2025-11-01", progress=False)["Close"].ffill()

# Buy the plan on the first trading day from the 2nd of each month
rows = []
for month in pd.date_range("2025-11-02", periods=12, freq="MS"):
    day = prices.index[prices.index >= month + pd.Timedelta(days=1)][0]
    for isin, name, block, ticker, amount in plan:
        price = prices.loc[day, ticker]
        rows.append([day.date(), isin, name, block, round(amount / price, 4), round(price, 2), amount, 0])

# Save the example files
folder = "data/portfolio/example/"
columns = ["date", "isin", "name", "block", "quantity", "price_eur", "amount_eur", "fee_eur"]
pd.DataFrame(rows, columns=columns).to_csv(folder + "transactions.csv", index=False)
last = prices.iloc[-1]
current = [[isin, name, round(last[ticker], 2), prices.index[-1].date()] for isin, name, block, ticker, amount in plan]
pd.DataFrame(current, columns=["isin", "name", "price_eur", "date"]).to_csv(folder + "current_prices.csv", index=False)
print("Example data saved:", len(rows), "purchases")
