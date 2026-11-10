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
st.caption("60% global stocks, 10% small companies and 30% in bets on the future: 5 stocks with little competition and 4 theme ETFs (health, power grid, quantum, nuclear). Automatic plans every month, checked every Monday, reviewed every January.")

# My products: isin, name, block, Yahoo ticker, currency and target %
products = pd.read_csv("data/portfolio/products.csv")
tickers = dict(zip(products["isin"], products["ticker"]))
targets = products.groupby("block")["target"].sum().to_dict()
band = 3

# Name and colour of each block in the charts
names = {"core": "Global (VWCE)", "small": "Small caps (IUSN)", "themes": "Theme ETFs", "stocks": "Stocks", "gold": "Gold"}
colours = {"Global (VWCE)": "#1f4e79", "Small caps (IUSN)": "#2a9d8f", "Theme ETFs": "#8e6cc0", "Stocks": "#e76f51", "Gold": "#e9b949"}

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

# Daily prices since my first purchase, all in euros (US stocks are converted with the EUR/USD rate)
start = transactions["date"].min()
prices = yf.download(list(products["ticker"]) + ["EURUSD=X"], start=start, progress=False)["Close"].ffill()
for _, product in products.iterrows():
    if product["currency"] == "USD":
        prices[product["ticker"]] = prices[product["ticker"]] / prices["EURUSD=X"]

# Stop with a clear message if a product has no prices on Yahoo
for isin in transactions["isin"].unique():
    if isin not in tickers:
        st.error(f"{isin} is not in data/portfolio/products.csv. Add it there")
        st.stop()
    ticker = tickers[isin]
    if ticker not in prices.columns or prices[ticker].isna().all():
        st.error(f"No prices for {ticker} ({isin}). Fix the ticker in data/portfolio/products.csv")
        st.stop()

# Value of the portfolio and money invested on each day
value = pd.Series(0.0, index=prices.index)
invested = pd.Series(0.0, index=prices.index)
for _, row in transactions.iterrows():
    after = prices.index >= row["date"]
    value[after] = value[after] + row["quantity"] * prices.loc[after, tickers[row["isin"]]].fillna(0)
    invested[after] = invested[after] + row["amount_eur"] + row["fee_eur"]

# Top numbers
gain = value.iloc[-1] - invested.iloc[-1]
gain_pct = gain / invested.iloc[-1] * 100
months = transactions["date"].dt.strftime("%Y-%m").nunique()
col1, col2, col3, col4 = st.columns(4)
if public:
    col1.metric("Return", f"{gain_pct:+.1f}%")
    col2.metric("Products", transactions["isin"].nunique())
    col3.metric("Purchases", len(transactions))
    col4.metric("Months investing", months)
else:
    col1.metric("Value today", f"{value.iloc[-1]:,.0f} €")
    col2.metric("Money I put in", f"{invested.iloc[-1]:,.0f} €")
    col3.metric("Gain", f"{gain:,.0f} €", f"{gain_pct:.1f}%")
    col4.metric("Months investing", months)

st.divider()

# Alerts from the weekly check
st.subheader("Alerts")
st.caption("Checked automatically every Monday. Green: a chance to buy. Yellow: stop buying for now. Red: check if the business got worse. I never sell just because the price fell.")
if os.path.exists("data/alerts/alerts.csv"):
    alerts = pd.read_csv("data/alerts/alerts.csv")
    st.write("Last check:", alerts["date"].iloc[0])
    for _, alert in alerts.iterrows():
        text = f"**{alert['type']}** · {alert['product']}: {alert['message']}"
        if alert["type"] == "OK":
            st.success(alert["message"])
        elif alert["type"] in ["BUY", "BUY EXTRA"]:
            st.success(text)
        elif alert["type"] == "STOP BUYING":
            st.warning(text)
        else:
            st.error(text)
else:
    st.write("No check yet: run python future/alerts.py")

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
st.caption("Left: how my money is split today. Right: today vs my targets. The first months look off because I started the stocks with a one-off buy; the monthly plans fix it over time.")
left, right = st.columns(2)
fig = px.pie(allocation, names="name", values="Now", hole=0.55, color="name", color_discrete_map=colours)
fig.update_traces(textinfo="percent", sort=False)
fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
left.plotly_chart(fig)
compare = allocation.melt(id_vars="name", value_vars=["Now", "Target"], var_name="series", value_name="%")
fig = px.bar(compare, x="name", y="%", color="series", barmode="group", color_discrete_map={"Now": "#1f4e79", "Target": "#c9d6e3"})
fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="", xaxis_title="")
right.plotly_chart(fig)

# Rebalance check (only after 6 months, gold is kept on purpose so it is left out)
if months < 6:
    st.info(f"Targets are checked after 6 months of monthly plans. Now: {months}.")
else:
    blocks_to_check = allocation[allocation["block"] != "gold"]
    for _, row in blocks_to_check.iterrows():
        gap = row["Now"] - row["Target"]
        if abs(gap) > band:
            st.warning(f"{row['name']} is {gap:+.1f} points from target. Fix it with new money, never by selling.")
    if (abs(blocks_to_check["Now"] - blocks_to_check["Target"]) <= band).all():
        st.success("All blocks are within 3 points of target. Nothing to do.")

st.divider()

# Table: each product today
st.subheader("Positions")
st.caption("What I own in each product and how much it is worth today.")
columns = ["name", "block", "invested", "value", "gain", "gain_%", "weight_%"]
if public:
    columns = ["name", "block", "gain_%", "weight_%"]
st.dataframe(
    positions[columns].sort_values("weight_%", ascending=False),
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

st.divider()

# Stocks: health check and watchlist from the screener
screen = pd.read_csv("data/future/future_screen.csv")
if "ticker" in screen.columns:
    screen["vs_fair_%"] = (screen["price"] / screen["buy_below"] - 1) * 100
    table_config = {
        "name": "Company",
        "price": st.column_config.NumberColumn("Price", format="%.2f"),
        "buy_below": st.column_config.NumberColumn("Fair price", format="%.2f"),
        "vs_fair_%": st.column_config.NumberColumn("Price vs fair", format="%+.0f%%"),
        "quality": "Quality /5",
        "edge": "Moat and future /4",
        "score": "Score /11",
        "verdict": "Verdict",
    }
    show = ["name", "price", "buy_below", "vs_fair_%", "quality", "edge", "score", "verdict"]

    st.subheader("My stocks: health check")
    st.caption("From the screener, in each company's own currency. Fair price comes from a DCF with growth capped at 25%. Below 0% means cheaper than fair.")
    my_stocks = products[products["block"] == "stocks"]["name"]
    st.dataframe(screen[screen["name"].isin(my_stocks)][show], hide_index=True, column_config=table_config)

    st.subheader("Watchlist")
    st.caption("Great companies I don't own yet because they were too expensive. They become candidates when the price goes below fair.")
    watchlist = pd.read_csv("data/future/watchlist.csv")
    waiting = screen[screen["ticker"].isin(watchlist["ticker"])].sort_values("vs_fair_%")
    st.dataframe(waiting[show], hide_index=True, column_config=table_config)

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

# Footer
st.caption("Prices from Yahoo Finance, US stocks converted to euros. Personal learning project, not investment advice.")