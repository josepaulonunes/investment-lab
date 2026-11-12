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

# My products: isin, name, block, Yahoo ticker, currency, target % and sector
products = pd.read_csv("data/portfolio/products.csv")

# One line that describes the plan, built from the products file so it is never out of date
plan = products[products["target"] > 0]
base = plan[plan["block"] == "core"]["target"].sum()
stocks = plan[plan["block"] == "stocks"]
st.caption(f"{base:.0f}% in the whole market and {100 - base:.0f}% in {len(stocks)} stocks that clearly beat their rivals, bought only at a fair price or below. Automatic plans every month, checked every Monday, reviewed every quarter.")
tickers = dict(zip(products["isin"], products["ticker"]))
targets = products.groupby("block")["target"].sum().to_dict()
band = 3

# Name and colour of each block in the charts
names = {"core": "Global (VWCE)", "stocks": "Stocks", "gold": "Gold"}
colours = {"Global (VWCE)": "#1f4e79", "Stocks": "#e76f51", "Gold": "#e9b949"}

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

# Exchange rates: one ticker for each currency that is not the euro (EURUSD=X, EURJPY=X...)
rate_tickers = []
for currency in products["currency"].unique():
    if currency != "EUR":
        rate_tickers.append("EUR" + currency + "=X")

# Daily prices since my first purchase, all in euros
start = transactions["date"].min()
prices = yf.download(list(products["ticker"]) + rate_tickers, start=start, progress=False)["Close"].ffill()
for _, product in products.iterrows():
    if product["currency"] != "EUR":
        prices[product["ticker"]] = prices[product["ticker"]] / prices["EUR" + product["currency"] + "=X"]

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
st.caption("Checked automatically every Monday. Green: a chance to buy. Blue: keep the plan going. Yellow: pause or stop buying. Red: the price is far too high or the business got worse, so I review or sell. I never sell just because the price fell.")
if os.path.exists("data/alerts/alerts.csv"):
    alerts = pd.read_csv("data/alerts/alerts.csv")
    st.write("Last check:", alerts["date"].iloc[0])
    for _, alert in alerts.iterrows():
        text = f"**{alert['type']}** · {alert['product']}: {alert['message']}"
        if alert["type"] == "OK":
            st.success(alert["message"])
        elif alert["type"] in ["BUY", "BUY EXTRA"]:
            st.success(text)
        elif alert["type"] == "KEEP":
            st.info(text)
        elif alert["type"] in ["STOP BUYING", "PAUSE"]:
            st.warning(text)
        else:
            st.error(text)
else:
    st.write("No check yet: run python future/alerts.py")

st.divider()

# Positions: each product today (money invested includes fees, like the chart below)
positions = transactions.groupby(["isin", "name", "block"]).agg(
    quantity=("quantity", "sum"),
    amount=("amount_eur", "sum"),
    fees=("fee_eur", "sum"),
).reset_index()
positions["invested"] = positions["amount"] + positions["fees"]
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

# Fair price of my stocks and of the watchlist (from future/fair_price.py)
if os.path.exists("data/future/fair_prices.csv"):
    fair = pd.read_csv("data/future/fair_prices.csv")
    fair_config = {
        "name": "Company",
        "price": st.column_config.NumberColumn("Price", format="%.0f"),
        "fair": st.column_config.NumberColumn("Fair price", format="%.0f"),
        "gap": st.column_config.NumberColumn("Price vs fair", format="%+.0f%%"),
        "return": st.column_config.NumberColumn("Expected return a year", format="%.1f%%"),
        "entry": st.column_config.NumberColumn("Buy at or below", format="%.0f"),
        "currency": "Currency",
        "status": "Status",
        "alarm": "I sell or replace it if",
    }

    st.subheader("My stocks: fair price and what to do")
    st.caption("My own DCF, in each company's currency. BUY EXTRA: 15% or more below fair. KEEP BUYING: up to 10% above fair. PAUSE: more than 10% above fair, so its monthly plan goes to VWCE and I keep the shares. SELL PART: 50% or more above fair, I sell up to half. The expected return is what I earn a year if the base case happens. I ask for at least 9%.")
    mine = fair[fair["list"] == "portfolio"]
    st.dataframe(mine[["name", "status", "price", "fair", "gap", "return", "entry", "currency", "alarm"]], hide_index=True, column_config=fair_config)

    st.subheader("Watchlist: good companies waiting for a good price")
    st.caption("Sorted from the closest to its fair price to the furthest. One becomes BUY when the price reaches my entry price. Then I write the full analysis before buying.")
    waiting = fair[fair["list"] == "watchlist"]
    st.dataframe(waiting[["name", "status", "price", "fair", "gap", "return", "entry", "currency"]], hide_index=True, column_config=fair_config)
else:
    st.write("No fair prices yet: run python future/fair_price.py")

# Business health of my stocks (from the screener)
screen = pd.read_csv("data/future/future_screen.csv")
st.subheader("My stocks: business health")
st.caption("From the screener. Quality looks at growth, margin, cash, debt and return on equity. Moat and future are my own scores. If quality falls below 4 the weekly check tells me to review the stock.")
my_stocks = products[products["block"] == "stocks"]["name"]
health = screen[screen["name"].isin(my_stocks)][["name", "quality", "edge", "score"]]
st.dataframe(health, hide_index=True, column_config={"name": "Company", "quality": "Quality /5", "edge": "Moat and future /4", "score": "Score /11"})

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