import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import os
import warnings

# Hide library warnings
warnings.filterwarnings("ignore")

# Page setup
st.set_page_config(page_title="My portfolio", page_icon="📈", layout="wide")
st.title("My portfolio")
st.caption("75% global stocks, 12% small companies, 13% future sectors (power grid, health, materials, nuclear). No new gold since Dec 2026. Automatic plans every month, reviewed every January.")

# Yahoo ticker for each product I own (all in EUR on Xetra)
tickers = {
    "IE00BK5BQT80": "VWCE.DE",
    "IE00BF4RFH31": "IUSN.DE",
    "IE000J80JTL1": "GRID.DE",
    "IE000M7V94E1": "NUKL.DE",
    "IE00BM67HK77": "XDWH.DE",
    "IE00BM67HS53": "XDWM.DE",
    "IE00B579F325": "8PSG.DE",
}
targets = {"core": 75, "small": 12, "future": 13, "gold": 0}
band = 3

# Name and colour of each block in the charts
names = {"core": "Global (VWCE)", "small": "Small caps (IUSN)", "future": "Future sectors", "gold": "Gold"}
colours = {"Global (VWCE)": "#1f4e79", "Small caps (IUSN)": "#2a9d8f", "Future sectors": "#8e6cc0", "Gold": "#e9b949"}

# Pick the data: my real file (private), the public file (scaled, no euros) or the example
file = "data/portfolio/transactions.csv"
public = False
unit = "€"
if not os.path.exists(file):
    file = "data/portfolio/public/transactions.csv"
    public = True
    unit = "points"
    st.info("This is my real portfolio, scaled so that all the money I put in adds up to 100. The real amounts stay private.")
if not os.path.exists(file):
    file = "data/portfolio/example/transactions.csv"
    public = False
    unit = "€"
    st.info("Showing example data: 12 months of my plan bought at real prices.")

# Load my purchases
transactions = pd.read_csv(file, parse_dates=["date"])
if len(transactions) == 0:
    st.write("No purchases yet: fill data/portfolio/transactions.csv first")
    st.stop()

# Daily prices in euros since my first purchase
start = transactions["date"].min()
prices = yf.download(list(tickers.values()), start=start, progress=False)["Close"].ffill()

# Stop with a clear message if a ticker has no prices on Yahoo
for isin in transactions["isin"].unique():
    ticker = tickers[isin]
    if ticker not in prices.columns or prices[ticker].isna().all():
        st.error(f"No prices for {ticker} ({isin}). Fix the ticker at the top of dashboard.py")
        st.stop()

# Value of the portfolio and money invested on each day
value = pd.Series(0.0, index=prices.index)
invested = pd.Series(0.0, index=prices.index)
for _, row in transactions.iterrows():
    after = prices.index >= row["date"]
    value[after] = value[after] + row["quantity"] * prices.loc[after, tickers[row["isin"]]]
    invested[after] = invested[after] + row["amount_eur"] + row["fee_eur"]

# Top numbers
gain = value.iloc[-1] - invested.iloc[-1]
gain_pct = gain / invested.iloc[-1] * 100
months = transactions["date"].dt.strftime("%Y-%m").nunique()
col1, col2, col3, col4 = st.columns(4)
if public:
    col1.metric("Return", f"{gain_pct:+.1f}%")
    col2.metric("ETFs", transactions["isin"].nunique())
    col3.metric("Purchases", len(transactions))
    col4.metric("Months investing", months)
else:
    col1.metric("Value today", f"{value.iloc[-1]:,.0f} €")
    col2.metric("Money I put in", f"{invested.iloc[-1]:,.0f} €")
    col3.metric("Gain", f"{gain:,.0f} €", f"{gain_pct:.1f}%")
    col4.metric("Months investing", months)

st.divider()

# Chart: value vs money invested
st.subheader("Value vs money invested")
st.caption("The steps are my monthly purchases. The space between the two lines is what the market added or took away.")
history = pd.DataFrame({"Value": value, "Money invested": invested})
fig = px.line(history, color_discrete_map={"Value": "#1f4e79", "Money invested": "#9aa5b1"})
fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="", xaxis_title="", yaxis_title=unit)
st.plotly_chart(fig)

# Chart: gain or loss of each month (without the new money I put in)
st.subheader("Gain or loss per month")
st.caption("How much the market moved my money each month, without counting new purchases. Red months are normal.")
monthly_value = value.resample("ME").last()
monthly_invested = invested.resample("ME").last()
monthly_gain = (monthly_value - monthly_invested).diff()
monthly_gain.iloc[0] = monthly_value.iloc[0] - monthly_invested.iloc[0]
monthly = pd.DataFrame({"month": monthly_gain.index.strftime("%Y-%m"), "gain": monthly_gain.values})
monthly["result"] = "Gain"
monthly.loc[monthly["gain"] < 0, "result"] = "Loss"
fig = px.bar(monthly, x="month", y="gain", color="result", color_discrete_map={"Gain": "#2a9d8f", "Loss": "#e76f51"})
fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="", xaxis_title="", yaxis_title=unit)
fig.update_xaxes(type="category")
st.plotly_chart(fig)

st.divider()

# Positions: each product today
positions = transactions.groupby(["isin", "name", "block"]).agg(
    quantity=("quantity", "sum"),
    invested=("amount_eur", "sum"),
).reset_index()
positions["price"] = [prices[tickers[isin]].iloc[-1] for isin in positions["isin"]]
positions["value"] = positions["quantity"] * positions["price"]
positions["gain"] = positions["value"] - positions["invested"]
positions["gain_%"] = positions["gain"] / positions["invested"] * 100
positions["weight_%"] = positions["value"] / positions["value"].sum() * 100

# Weight of each block vs target
blocks = positions.groupby("block")["value"].sum() / positions["value"].sum() * 100
allocation = pd.DataFrame({"block": list(targets.keys())})
allocation["name"] = [names[b] for b in allocation["block"]]
allocation["Now"] = [blocks.get(b, 0) for b in allocation["block"]]
allocation["Target"] = [targets[b] for b in allocation["block"]]

# Charts: allocation donut and now vs target
st.subheader("Allocation")
st.caption("Left: how my money is split today. Right: today vs my targets. Future sectors are GRID, health care, materials and NUKL. I only fix a block in January if it is more than 3 points away.")
left, right = st.columns(2)
fig = px.pie(allocation, names="name", values="Now", hole=0.55, color="name", color_discrete_map=colours)
fig.update_traces(textinfo="percent", sort=False)
fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
left.plotly_chart(fig)
compare = allocation.melt(id_vars="name", value_vars=["Now", "Target"], var_name="series", value_name="%")
fig = px.bar(compare, x="name", y="%", color="series", barmode="group", color_discrete_map={"Now": "#1f4e79", "Target": "#c9d6e3"})
fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="", xaxis_title="")
right.plotly_chart(fig)

# Rebalance check
for _, row in allocation.iterrows():
    gap = row["Now"] - row["Target"]
    if abs(gap) > band:
        st.warning(f"{row['name']} is {gap:+.1f} points from target. Fix it in January with new money.")
if (abs(allocation["Now"] - allocation["Target"]) <= band).all():
    st.success("All blocks are within 3 points of target. Nothing to do.")

st.divider()

# Table: each product today
st.subheader("Positions")
st.caption("What I own in each ETF, how much I put in and how much it is worth today.")
columns = ["name", "block", "invested", "value", "gain", "gain_%", "weight_%"]
if public:
    columns = ["name", "block", "gain_%", "weight_%"]
st.dataframe(
    positions[columns],
    hide_index=True,
    column_config={
        "name": "Product",
        "block": "Block",
        "invested": st.column_config.NumberColumn("Invested", format="%.2f €"),
        "value": st.column_config.NumberColumn("Value", format="%.2f €"),
        "gain": st.column_config.NumberColumn("Gain", format="%.2f €"),
        "gain_%": st.column_config.NumberColumn("Gain %", format="%.1f%%"),
        "weight_%": st.column_config.ProgressColumn("Weight", format="%.1f%%", min_value=0, max_value=100),
    },
)

# Footer
st.caption("Prices from Yahoo Finance (Xetra, in EUR). Personal learning project, not investment advice.")
