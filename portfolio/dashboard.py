import streamlit as st
import pandas as pd
import yfinance as yf
import os
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Page setup
st.set_page_config(page_title="My portfolio", layout="wide")
st.title("My portfolio")

# Yahoo ticker for each product I own (all in EUR on Xetra)
tickers = {
    "IE00BK5BQT80": "VWCE.DE",
    "IE00BF4RFH31": "IUSN.DE",
    "IE00B579F325": "8PSG.DE",
}
targets = {"core": 0.85, "small": 0.10, "gold": 0.05}

# Use my real data if it exists, otherwise the example data
file = "data/portfolio/transactions.csv"
if not os.path.exists(file):
    file = "data/portfolio/example/transactions.csv"
    st.caption("Showing example data")

# Load my purchases
transactions = pd.read_csv(file, parse_dates=["date"])
if len(transactions) == 0:
    st.write("No purchases yet: fill data/portfolio/transactions.csv first")
    st.stop()

# Daily prices in euros since my first purchase
start = transactions["date"].min()
data = yf.download(list(tickers.values()), start=start, progress=False)
prices = data["Close"].ffill()

# Value of the portfolio and money invested on each day
value = pd.Series(0.0, index=prices.index)
invested = pd.Series(0.0, index=prices.index)
for _, row in transactions.iterrows():
    after = prices.index >= row["date"]
    value[after] = value[after] + row["quantity"] * prices.loc[after, tickers[row["isin"]]]
    invested[after] = invested[after] + row["amount_eur"] + row["fee_eur"]

# Top numbers
gain = value.iloc[-1] - invested.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Value", str(round(value.iloc[-1], 2)) + " EUR")
col2.metric("Invested", str(round(invested.iloc[-1], 2)) + " EUR")
col3.metric("Gain", str(round(gain, 2)) + " EUR", str(round(gain / invested.iloc[-1] * 100, 1)) + "%")

# Chart: value vs money invested
st.subheader("Value vs money invested")
st.line_chart(pd.DataFrame({"Value": value, "Invested": invested}))

# Chart: gain or loss of each month (without the new money I put in)
st.subheader("Gain or loss per month")
monthly_value = value.resample("ME").last()
monthly_invested = invested.resample("ME").last()
monthly_gain = (monthly_value - monthly_invested).diff()
monthly_gain.iloc[0] = monthly_value.iloc[0] - monthly_invested.iloc[0]
monthly_gain.index = monthly_gain.index.strftime("%Y-%m")
st.bar_chart(monthly_gain)

# Table: each product today
positions = transactions.groupby(["isin", "name", "block"]).agg(
    quantity=("quantity", "sum"),
    invested=("amount_eur", "sum"),
).reset_index()
positions["price"] = [prices[tickers[isin]].iloc[-1] for isin in positions["isin"]]
positions["value"] = positions["quantity"] * positions["price"]
positions["gain"] = positions["value"] - positions["invested"]
positions["gain_%"] = positions["gain"] / positions["invested"] * 100
positions["weight_%"] = positions["value"] / positions["value"].sum() * 100
st.subheader("Positions")
st.dataframe(positions[["name", "block", "invested", "value", "gain", "gain_%", "weight_%"]].round(2), hide_index=True)

# Chart: weight of each block vs target
st.subheader("Blocks vs targets (%)")
blocks = positions.groupby("block")["value"].sum() / positions["value"].sum() * 100
compare = pd.DataFrame({"Now": blocks, "Target": pd.Series(targets) * 100})
st.bar_chart(compare, stack=False)

