import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import warnings

# The same DCF math as future/fair_price.py
sys.path.append("future")
from dcf import dcf_value, expected_return

# Hide library warnings
warnings.filterwarnings("ignore")

# Page setup
st.set_page_config(page_title="My portfolio", page_icon="📈", layout="wide")

# All the style of the site in one place: the top banner, the labels, the white cards and the phone layout
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
.hero {background: linear-gradient(135deg, #0f766e, #134e4a); color: white; border-radius: 18px; padding: 28px 32px; margin-bottom: 10px;}
.hero-title {font-size: 2.2rem; font-weight: 700; line-height: 1.2;}
.hero-text {opacity: 0.9; margin: 6px 0 14px 0;}
.chip {display: inline-block; background: rgba(255,255,255,0.16); border-radius: 999px; padding: 4px 12px; margin: 0 6px 6px 0; font-size: 0.85rem;}
.pill {display: inline-block; border-radius: 999px; padding: 3px 12px; margin: 0 6px 6px 0; font-size: 0.85rem; font-weight: 600;}
div[data-testid="stMetric"] {background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
div[data-testid="stMetricLabel"] p {color: #6b7280;}
[class*="st-key-card"] {background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
@media (max-width: 640px) {
    .hero {padding: 20px;}
    .hero-title {font-size: 1.6rem;}
    [class*="st-key-kpi"] div[data-testid="stColumn"] {min-width: calc(50% - 1rem); flex: 1 1 calc(50% - 1rem);}
}
</style>
""", unsafe_allow_html=True)

# Colours used in every chart
colours = {"main": "#0f766e", "light": "#99f6e4", "grey": "#94a3b8", "gain": "#15803d", "loss": "#b91c1c", "text": "#111827", "grid": "#e5e7eb"}
palette = ["#0f766e", "#1e3a5f", "#2563eb", "#7c3aed", "#db2777", "#d97706", "#ca8a04", "#475569", "#14b8a6", "#94a3b8"]
status_colours = {
    "BUY EXTRA": "#15803d", "BUY": "#15803d", "KEEP BUYING": "#2563eb", "WAIT": "#64748b",
    "PAUSE": "#d97706", "SELL PART": "#b91c1c", "NO PRICE": "#6b7280",
    "BUY BIG": "#15803d", "START PLAN": "#2563eb", "CHEAP, NOT CONFIRMED": "#ca8a04", "WAIT RESULTS": "#ca8a04",
}
status_dots = {
    "BUY EXTRA": "🟢", "BUY": "🟢", "KEEP BUYING": "🔵", "WAIT": "⚪",
    "PAUSE": "🟠", "SELL PART": "🔴", "NO PRICE": "⚪",
    "BUY BIG": "🟢", "START PLAN": "🔵", "CHEAP, NOT CONFIRMED": "🟡", "WAIT RESULTS": "🟡",
}
alert_colours = {
    "OK": "#15803d", "BUY": "#15803d", "BUY EXTRA": "#15803d", "CLOSE": "#15803d", "KEEP": "#2563eb",
    "STOP BUYING": "#d97706", "PAUSE": "#d97706", "RESULTS": "#d97706", "REVIEW ASSUMPTION": "#d97706",
    "PRIORITY BUY BIG": "#15803d", "PRIORITY START PLAN": "#15803d", "PRIORITY CLOSE": "#2563eb",
    "NOT CONFIRMED": "#ca8a04", "WAIT RESULTS": "#ca8a04", "PRIORITY NOT CONFIRMED": "#ca8a04", "PRIORITY WAIT RESULTS": "#ca8a04",
    "REVIEW MORNINGSTAR": "#d97706", "PROFIT CUT": "#b91c1c", "ALARM": "#b91c1c",
}
sector_colours = {
    "VWCE": "#1e3a5f", "Chips and AI": "#0f766e", "Software": "#7c3aed", "Payments": "#2563eb",
    "Health": "#db2777", "Grid": "#d97706", "Power and grid": "#d97706", "Aerospace": "#475569", "Gold": "#ca8a04",
    "Payments and data": "#2563eb", "Big tech": "#14b8a6",
}


# One look for every chart: same font, soft grid, legend on top, no toolbar
def show_chart(fig, height):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(family="Inter, sans-serif", size=13, color=colours["text"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom", title_text=""),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor=colours["grid"], zeroline=False)
    st.plotly_chart(fig, config={"displayModeBar": False})


# A small coloured label, used for the states and the alerts
def pill(text, colour):
    return f'<span class="pill" style="color: {colour}; background: {colour}1a;">{text}</span>'


# My files: products, limits, my DCF assumptions and the weekly fair prices
products = pd.read_csv("data/portfolio/products.csv")
rules = pd.read_csv("data/portfolio/rules.csv").set_index("name")["value"]
inputs = pd.read_csv("data/portfolio/fair_inputs.csv")
fair = pd.read_csv("data/future/fair_prices.csv")
tickers = dict(zip(products["isin"], products["ticker"]))

# Alerts from the last check, if there is one
alerts = pd.DataFrame()
last_check = "not yet"
if os.path.exists("data/alerts/alerts.csv"):
    alerts = pd.read_csv("data/alerts/alerts.csv")
if len(alerts) > 0:
    last_check = str(alerts["date"].iloc[0])


# Yahoo prices, kept for one hour so the sliders stay fast
@st.cache_data(ttl=3600)
def load_prices(ticker_list, start):
    return yf.download(ticker_list, start=start, progress=False)["Close"].ffill()


# Euros per dollar today (1.125 if Yahoo fails)
@st.cache_data(ttl=3600)
def load_rate():
    try:
        return float(yf.download("EURUSD=X", period="10d", progress=False)["Close"].ffill().iloc[-1, 0])
    except Exception:
        return 1.125


# Sidebar: an example amount to split (my real amount stays private) and the exchange rate for the Trade Republic levels
st.sidebar.title(":material/monitoring: My portfolio")
monthly = st.sidebar.number_input("Try an amount (€)", min_value=10, max_value=5000, value=100, step=10)
rate = st.sidebar.number_input("Dollars per euro", min_value=0.80, max_value=1.60, value=round(load_rate(), 3), step=0.005, format="%.3f")
st.sidebar.caption("Trade Republic shows US stocks in euros, so every price level in dollars is divided by this rate.")
st.sidebar.divider()
st.sidebar.caption("VWCE is the base. Each stock must clearly beat its rivals and only comes in below its fair price. While a stock waits for its price, its money stays in VWCE. Plans run every month, the check every weekday, a full review every quarter.")
st.sidebar.caption("The code is on [GitHub](https://github.com/josepaulonunes/investment-lab).")

# Top banner
plan = products[products["target"] > 0]
base = plan[plan["block"] == "core"]["target"].sum()
stocks_plan = plan[plan["block"] == "stocks"]
st.markdown(f"""
<div class="hero">
    <div class="hero-title">My portfolio</div>
    <div class="hero-text">Today {base:.0f}% in the whole world (VWCE) and {100 - base:.0f}% in {len(stocks_plan)} stocks. The ideal mix is {products[products["block"] == "core"]["ideal"].sum():.0f}% VWCE: the other stocks wait for a good price.</div>
    <span class="chip">{base:.0f}% VWCE</span>
    <span class="chip">{len(stocks_plan)} stocks</span>
    <span class="chip">Last check: {last_check}</span>
</div>
""", unsafe_allow_html=True)
st.caption("Prices from Yahoo Finance. Personal learning project, not investment advice.")

tab_portfolio, tab_priority, tab_plan, tab_fair, tab_lab, tab_alerts = st.tabs([
    ":material/pie_chart: Portfolio",
    ":material/star: Top priorities",
    ":material/calendar_month: Monthly plan",
    ":material/sell: Fair prices",
    ":material/calculate: DCF lab",
    ":material/notifications: Alerts and TR levels",
])

# ---------------- Portfolio ----------------
with tab_portfolio:
    # Pick the data: my real file (private), the public file (scaled, no euros) or the example
    file = "data/portfolio/transactions.csv"
    public = False
    unit = "€"
    if not os.path.exists(file):
        file = "data/portfolio/public/transactions.csv"
        public = True
        unit = "points"
        st.info("This is my real portfolio, scaled so that all the money I put in adds up to 100. The real amounts stay private.", icon=":material/lock:")
    transactions = pd.read_csv(file, parse_dates=["date"])

    # Exchange rates: one ticker for each currency that is not the euro
    rate_tickers = []
    for currency in products["currency"].unique():
        if currency != "EUR":
            rate_tickers.append("EUR" + currency + "=X")

    # Daily prices since my first purchase, all in euros
    prices = load_prices(list(products["ticker"]) + rate_tickers, transactions["date"].min())
    prices = prices.copy()
    for _, product in products.iterrows():
        if product["currency"] != "EUR":
            prices[product["ticker"]] = prices[product["ticker"]] / prices["EUR" + product["currency"] + "=X"]

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
    with st.container(key="kpi_portfolio"):
        col1, col2, col3, col4 = st.columns(4)
        if public:
            col1.metric(":material/trending_up: Return", f"{gain_pct:+.1f}%")
            col2.metric(":material/category: Products", transactions["isin"].nunique())
            col3.metric(":material/shopping_cart: Purchases", len(transactions))
            col4.metric(":material/calendar_month: Months investing", months)
        else:
            col1.metric(":material/account_balance_wallet: Value today", f"{value.iloc[-1]:,.0f} €")
            col2.metric(":material/savings: Money I put in", f"{invested.iloc[-1]:,.0f} €")
            col3.metric(":material/trending_up: Gain", f"{gain:,.0f} €", f"{gain_pct:.1f}%")
            col4.metric(":material/calendar_month: Months investing", months)

    # Chart: value vs money invested
    with st.container(border=True, key="card_value"):
        st.subheader(":material/show_chart: Value vs money invested")
        history = pd.DataFrame({"Value": value, "Money invested": invested})
        fig = px.line(history, color_discrete_map={"Value": colours["main"], "Money invested": colours["grey"]})
        fig.update_traces(line_width=2)
        fig.update_traces(fill="tozeroy", fillcolor="rgba(15,118,110,0.10)", selector=dict(name="Value"))
        fig.update_traces(line_dash="dot", selector=dict(name="Money invested"))
        fig.update_layout(xaxis_title="", yaxis_title=unit, hovermode="x unified")
        show_chart(fig, 360)

    # Positions today
    positions = transactions.groupby(["isin", "name", "block"]).agg(
        quantity=("quantity", "sum"),
        amount=("amount_eur", "sum"),
        fees=("fee_eur", "sum"),
    ).reset_index()
    positions["invested"] = positions["amount"] + positions["fees"]
    positions["price"] = [prices[tickers[isin]].iloc[-1] for isin in positions["isin"]]
    positions["value"] = positions["quantity"] * positions["price"]
    positions["gain_%"] = (positions["value"] / positions["invested"] - 1) * 100
    positions["weight_%"] = positions["value"] / positions["value"].sum() * 100

    left, right = st.columns([1, 1.4])
    with left:
        with st.container(border=True, key="card_own"):
            st.subheader(":material/donut_small: What I own")
            fig = px.pie(positions, names="name", values="weight_%", hole=0.6, color_discrete_sequence=palette)
            fig.update_traces(textinfo="percent", textposition="inside")
            show_chart(fig, 380)
    with right:
        with st.container(border=True, key="card_gain"):
            st.subheader(":material/bar_chart: Gain or loss per product")
            bars = positions.sort_values("gain_%")
            bars["result"] = "Gain"
            bars.loc[bars["gain_%"] < 0, "result"] = "Loss"
            fig = px.bar(bars, x="gain_%", y="name", orientation="h", color="result", color_discrete_map={"Gain": colours["gain"], "Loss": colours["loss"]}, text_auto=".1f")
            fig.update_layout(showlegend=False, xaxis_title="%", yaxis_title="")
            show_chart(fig, 380)

    # Table of positions
    columns = ["name", "block", "invested", "value", "gain_%", "weight_%"]
    if public:
        columns = ["name", "block", "gain_%", "weight_%"]
    with st.container(border=True, key="card_positions"):
        st.subheader(":material/list_alt: Positions")
        st.dataframe(
            positions[columns].sort_values("weight_%", ascending=False),
            hide_index=True,
            column_config={
                "name": "Product",
                "block": "Block",
                "invested": st.column_config.NumberColumn("Invested", format="%.2f €"),
                "value": st.column_config.NumberColumn("Value", format="%.2f €"),
                "gain_%": st.column_config.NumberColumn("Gain", format="%+.1f%%"),
                "weight_%": st.column_config.ProgressColumn("Weight", format="%.1f%%", min_value=0, max_value=100),
            },
        )

    # Gain or loss of each month, without the new money I put in
    with st.container(border=True, key="card_months"):
        st.subheader(":material/date_range: Gain or loss per month")
        monthly_value = value.resample("ME").last()
        monthly_invested = invested.resample("ME").last()
        monthly_gain = (monthly_value - monthly_invested).diff()
        monthly_gain.iloc[0] = monthly_value.iloc[0] - monthly_invested.iloc[0]
        by_month = pd.DataFrame({"month": monthly_gain.index.strftime("%Y-%m"), "gain": monthly_gain.values})
        by_month["result"] = "Gain"
        by_month.loc[by_month["gain"] < 0, "result"] = "Loss"
        fig = px.bar(by_month, x="month", y="gain", color="result", color_discrete_map={"Gain": colours["gain"], "Loss": colours["loss"]})
        fig.update_layout(xaxis_title="", yaxis_title=unit)
        fig.update_xaxes(type="category")
        show_chart(fig, 280)

# ---------------- Monthly plan ----------------
with tab_plan:
    st.subheader(":material/calendar_month: How I split my money every month")
    st.caption(f"The euros show how {monthly:,.0f} € is split today. Ideal is the weight each stock gets once its price is good enough to start: until then its money stays in VWCE. Change the amount in the sidebar (on a phone, open it with the arrow at the top left).")

    # Euros per product for the amount in the sidebar
    split = products[(products["target"] > 0) | (products["ideal"] > 0)][["name", "block", "sector", "target", "ideal", "ai"]].copy()
    split["sector"] = split["sector"].fillna("VWCE")
    split["euros"] = split["target"] / 100 * monthly

    left, right = st.columns([1, 1.2])
    with left:
        with st.container(border=True, key="card_split"):
            fig = px.sunburst(split, path=["sector", "name"], values="ideal", color="sector", color_discrete_map=sector_colours)
            fig.update_traces(textinfo="label+percent root")
            show_chart(fig, 420)
    with right:
        with st.container(border=True, key="card_split_table"):
            st.dataframe(
                split[["name", "sector", "ideal", "target", "euros"]].sort_values(["target", "ideal"], ascending=False),
                hide_index=True,
                height=440,
                column_config={
                    "name": "Product",
                    "sector": "Sector",
                    "ideal": st.column_config.NumberColumn("Ideal", format="%.0f%%"),
                    "target": st.column_config.ProgressColumn("Today", format="%.0f%%", min_value=0, max_value=100),
                    "euros": st.column_config.NumberColumn(f"Out of {monthly:,.0f} €", format="%.2f €"),
                },
            )

    # Limits: each sector of my stocks (VWCE does not count) and everything that depends on AI
    st.subheader(":material/shield: Limits")
    sectors = split[split["block"] == "stocks"].groupby("sector")["ideal"].sum().reset_index()
    ai_total = split[split["ai"] == "yes"]["ideal"].sum()
    stocks_total = split[split["block"] == "stocks"]["ideal"].sum()
    st.caption("The limits are checked against the ideal weights, so the plan still fits when every stock has started.")
    with st.container(key="kpi_plan"):
        col1, col2, col3 = st.columns(3)
        col1.metric(":material/stacked_bar_chart: Stocks together", f"{stocks_total:.0f}%", f"limit {rules['max_bets']:.0f}%", delta_color="off")
        col2.metric(":material/memory: Depends on AI", f"{ai_total:.0f}%", f"limit {rules['max_ai']:.0f}%", delta_color="off")
        col3.metric(":material/checklist: Stocks in the ideal mix", len(split[(split["block"] == "stocks") & (split["ideal"] > 0)]), f"limit {rules['max_stocks']:.0f}", delta_color="off")
    with st.container(border=True, key="card_sectors"):
        fig = px.bar(sectors, x="sector", y="ideal", color="sector", color_discrete_map=sector_colours, text_auto=".0f")
        fig.add_hline(y=rules["max_sector"], line_dash="dash", line_color=colours["loss"], annotation_text=f"Sector limit {rules['max_sector']:.0f}%")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="% of the portfolio")
        show_chart(fig, 320)

# ---------------- Fair prices ----------------
with tab_fair:
    st.subheader(":material/sell: Price today vs my fair price")
    st.caption(f"My fair price mixes my own DCF ({rules['weight_dcf']:.0f}%) with the Morningstar fair value. The DCF uses the analysts' profit of the day and a rate that follows the US 10 year yield, so it moves with the business and the economy. Below 0 the stock is cheaper than my fair price. A stock of my ideal mix starts its plan when the price is at or below fair. An extra buy needs a real discount: {rules['margin_medium']:.0f}%, {rules['margin_high']:.0f}% or {rules['margin_very_high']:.0f}%, the harder the company is to value the more I ask, and two checks must agree. Up to +10%: the plan keeps going. Above +10%: pause. Above +50%: sell part.")

    # Filter: my stocks, the watchlist or both
    show = st.radio("Show", ["My stocks", "Top priorities", "Watchlist", "All"], horizontal=True)
    table = fair.copy()
    if show == "My stocks":
        table = table[table["list"] == "portfolio"]
    if show == "Top priorities":
        table = table[table["list"] == "priority"]
    if show == "Watchlist":
        table = table[table["list"] == "watchlist"]
    table = table.sort_values("gap", ascending=False)

    # How many companies are in each state
    counts = table["status"].value_counts()
    labels = ""
    for status in counts.index:
        labels = labels + pill(f"{counts[status]} {status}", status_colours.get(status, colours["grey"]))
    st.markdown(labels, unsafe_allow_html=True)

    # Chart: gap to the fair price, with the zones behind the bars
    with st.container(border=True, key="card_gap"):
        fig = px.bar(table, x="gap", y="name", orientation="h", color="status", color_discrete_map=status_colours, text_auto=".0f",
                     hover_data={"price": ":.0f", "fair": ":.0f", "return": ":.1f", "currency": True})
        fig.add_vrect(x0=10, x1=50, fillcolor=status_colours["PAUSE"], opacity=0.07, line_width=0)
        fig.add_vrect(x0=50, x1=120, fillcolor=status_colours["SELL PART"], opacity=0.07, line_width=0)
        fig.add_vline(x=0, line_color=colours["text"], line_width=1)
        fig.update_layout(xaxis_title="Price vs fair price (%)", yaxis_title="")
        fig.update_xaxes(range=[min(-30, table["gap"].min() - 5), max(40, table["gap"].max() + 5)])
        show_chart(fig, 80 + 32 * len(table))

    # Chart: what I earn a year at today's price vs the lowest rate I ask for
    with st.container(border=True, key="card_return"):
        st.subheader(":material/percent: Expected return a year at today's price")
        fig = px.scatter(table, x="gap", y="return", text="name", color="status", color_discrete_map=status_colours)
        fig.add_hline(y=fair["discount"].min(), line_dash="dash", line_color=colours["loss"], annotation_text=f"I ask for at least {fair['discount'].min():.1f}%")
        fig.update_traces(textposition="top center", marker_size=12)
        fig.update_layout(xaxis_title="Price vs fair price (%)", yaxis_title="% a year")
        show_chart(fig, 440)

    # Full table, with a coloured dot next to each state
    table["status"] = [status_dots.get(status, "⚪") + " " + status for status in table["status"]]
    with st.container(border=True, key="card_fair_table"):
        st.subheader(":material/list_alt: All the numbers")
        st.dataframe(
            table[["name", "status", "price", "fair", "gap", "dcf", "morningstar", "discount", "margin", "start", "entry", "return", "checks", "currency", "eps_used", "eps_change", "next_results"]],
            hide_index=True,
            column_config={
                "name": "Company",
                "status": "Status",
                "price": st.column_config.NumberColumn("Price", format="%.0f"),
                "fair": st.column_config.NumberColumn("Fair price", format="%.0f"),
                "gap": st.column_config.NumberColumn("vs fair", format="%+.0f%%"),
                "dcf": st.column_config.NumberColumn("My DCF", format="%.0f"),
                "morningstar": st.column_config.NumberColumn("Morningstar", format="%.0f"),
                "discount": st.column_config.NumberColumn("Rate I ask for", format="%.1f%%"),
                "margin": st.column_config.NumberColumn("Margin of safety", format="%.0f%%"),
                "start": st.column_config.NumberColumn("Start a plan at", format="%.0f"),
                "entry": st.column_config.NumberColumn("Extra buy at", format="%.0f"),
                "return": st.column_config.NumberColumn("Return a year", format="%.1f%%"),
                "checks": "Checks",
                "currency": "Currency",
                "eps_used": st.column_config.NumberColumn("Profit a share used", format="%.2f"),
                "eps_change": st.column_config.NumberColumn("Analysts in 3 months", format="%+.0f%%"),
                "next_results": "Next results",
            },
        )
    st.caption("Prices, profits and the 10 year yield come from the last daily check (every weekday after the US close). The three checks are: Morningstar above the price, my own DCF above the price, and analysts not cutting profits in the last 3 months. The Morningstar values are typed by hand, so the check tells me when one is more than 3 months old.")

# ---------------- Top priorities ----------------
with tab_priority:
    st.subheader(":material/star: The companies I want to own one day")
    st.caption(f"These are the companies I want to own one day: the Magnificent 7, chips, cybersecurity, quantum, remote work and AI leaders. At or below my fair price I start its monthly plan, if its alarm is off and analysts are not cutting profits. At its full margin of safety, and with two checks agreeing, I also buy big with the extra money (up to 200 € a month). Prices in euros, updated after every US close.")

    # My top priorities, the closest to a buy first
    top = fair[fair["list"] == "priority"].sort_values("gap")

    # How many are in each state
    counts = top["status"].value_counts()
    labels = ""
    for status in counts.index:
        labels = labels + pill(f"{counts[status]} {status}", status_colours.get(status, colours["grey"]))
    st.markdown(labels, unsafe_allow_html=True)

    # One card per company, two cards in a row
    columns = st.columns(2)
    number = 0
    for _, row in top.iterrows():
        to_euro = 1
        if row["currency"] == "USD":
            to_euro = 1 / rate
        today = row["price"] * to_euro
        start_plan = row["start"] * to_euro
        buy_big = row["entry"] * to_euro
        fall_needed = (start_plan / today - 1) * 100

        with columns[number % 2]:
            with st.container(border=True, key=f"card_priority_{number}"):
                st.markdown(f"**{row['name']}** " + pill(row["status"], status_colours.get(row["status"], colours["grey"])), unsafe_allow_html=True)
                left, middle, right = st.columns(3)
                left.metric("Today", f"{today:,.0f} €")
                middle.metric("Start plan at", f"{start_plan:,.0f} €")
                right.metric("Buy big at", f"{buy_big:,.0f} €")

                # How close the price is to the start of the plan (full bar = time to start)
                closeness = min(1.0, max(0.0, start_plan / today))
                if fall_needed < 0:
                    st.progress(closeness, text=f"Needs to fall {-fall_needed:.0f}% to start the plan")
                else:
                    st.progress(closeness, text="At my start price: start the plan if the checks agree")
        number = number + 1

    st.caption("When one of them reaches its start price, I start its plan with 3% and VWCE goes down to make room, never below 50%. No other stock has to leave. Plenty of big tech names can come in, as long as each one reaches its own price.")

# ---------------- DCF lab ----------------
with tab_lab:
    st.subheader(":material/calculate: Play with my assumptions")
    st.caption("Pick a company and move the sliders. The file data/portfolio/fair_inputs.csv does not change: I only change it in the quarterly review. Growth above 15% is cut to 15% in the daily check.")

    # Pick a company and start from my saved assumptions
    with st.container(border=True, key="card_sliders"):
        name = st.selectbox("Company", list(inputs["name"]))
        company = inputs[inputs["name"] == name].iloc[0]
        priced = fair[fair["name"] == name]
        price = float(priced["price"].iloc[0]) if len(priced) > 0 else 0.0
        ticker = company["ticker"]

        col1, col2 = st.columns(2)
        eps = col1.slider("Earnings per share, next 12 months", 0.1, float(company["eps"]) * 2, float(company["eps"]), key="eps_" + ticker)
        conversion = col1.slider("Share of earnings that becomes free cash", 0.3, 1.2, float(company["conversion"]), 0.05, key="conv_" + ticker)
        growth = col2.slider("Growth a year, years 2 to 5 (%)", 0.0, 40.0, float(company["growth"]) * 100, 0.5, key="growth_" + ticker) / 100
        saved_rate = float(priced["discount"].iloc[0]) if len(priced) > 0 else 9.0
        discount = col2.slider("Return I ask for (10 year yield plus the premium, %)", 7.0, 13.0, saved_rate, 0.05, key="disc_" + ticker) / 100

    # Results
    # With Morningstar, the fair price is the same mix as the daily check
    cash = eps * conversion
    my_dcf = dcf_value(cash, growth, discount)
    fair_value = my_dcf
    if pd.notna(company["morningstar"]):
        fair_value = rules["weight_dcf"] / 100 * my_dcf + (1 - rules["weight_dcf"] / 100) * company["morningstar"]
    safety = float(priced["margin"].iloc[0]) / 100 if len(priced) > 0 else 0.15
    yearly = expected_return(price, cash, growth) * 100 if price > 0 else 0
    gap_now = (price / fair_value - 1) * 100
    with st.container(key="kpi_lab"):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(":material/sell: Fair price", f"{fair_value:,.0f} {company['currency']}")
        col2.metric(":material/payments: Price today", f"{price:,.0f} {company['currency']}", f"{gap_now:+.0f}% vs fair", delta_color="inverse")
        col3.metric(":material/percent: Return a year at today's price", f"{yearly:.1f}%")
        col4.metric(":material/speed: P/E I am paying", f"{price / eps:.1f}")
    if pd.notna(company["morningstar"]):
        st.caption(f"My DCF alone gives {my_dcf:,.0f} and Morningstar says {company['morningstar']:,.0f}. The fair price above is {rules['weight_dcf']:.0f}% mine and the rest Morningstar. Margin of safety for this company: {safety * 100:.0f}%.")
    else:
        st.caption(f"Morningstar does not cover this company (or I have not typed its value), so the fair price is my DCF alone. Margin of safety: {safety * 100:.0f}%.")

    # The state these sliders give, with the same rules as the daily check
    if price > 0:
        state = "KEEP BUYING"
        if gap_now <= -safety * 100:
            state = "BUY EXTRA"
        elif gap_now >= 50:
            state = "SELL PART"
        elif gap_now > 10:
            state = "PAUSE"
        st.markdown("With these sliders: " + pill(state, status_colours[state]), unsafe_allow_html=True)
    if len(priced) > 0 and pd.notna(priced["analyst_eps"].iloc[0]):
        st.caption(f"Analysts expect {priced['analyst_eps'].iloc[0]:.2f} a share next year: the daily check uses that number. My saved number is {company['eps']:.2f}. Next results: {priced['next_results'].iloc[0]}")

    # Chart: the cash I expect each year and what it is worth today
    years = []
    year_cash = cash
    for year in range(1, 11):
        rate_year = 0
        if year > 1:
            rate_year = growth
        if year > 5:
            rate_year = growth + (0.04 - growth) * (year - 5) / 5
        year_cash = year_cash * (1 + rate_year)
        years.append([year, year_cash, year_cash / (1 + discount) ** year])
    years = pd.DataFrame(years, columns=["year", "Cash that year", "Worth today"])
    left, right = st.columns(2)
    with left:
        with st.container(border=True, key="card_cash"):
            st.markdown("**Cash per share for the next 10 years**")
            fig = px.bar(years, x="year", y=["Cash that year", "Worth today"], barmode="group", color_discrete_sequence=[colours["main"], colours["light"]])
            fig.update_layout(xaxis_title="Year", yaxis_title=company["currency"])
            show_chart(fig, 340)

    # Heat map: fair price for other growth and discount rates
    with right:
        with st.container(border=True, key="card_heat"):
            st.markdown("**Fair price if I am wrong on growth or on the rate**")
            growth_list = [growth - 0.06, growth - 0.03, growth, growth + 0.03, growth + 0.06]
            discount_list = [discount - 0.01, discount, discount + 0.01]
            grid = []
            for d in discount_list:
                line = []
                for g in growth_list:
                    value = dcf_value(cash, g, d)
                    if pd.notna(company["morningstar"]):
                        value = rules["weight_dcf"] / 100 * value + (1 - rules["weight_dcf"] / 100) * company["morningstar"]
                    line.append(value)
                grid.append(line)
            grid = pd.DataFrame(grid, index=[f"rate {d * 100:.1f}%" for d in discount_list], columns=[f"growth {g * 100:.0f}%" for g in growth_list])
            fig = px.imshow(grid, text_auto=".0f", color_continuous_scale="RdYlGn", aspect="auto", zmin=price * 0.5, zmax=price * 1.5)
            fig.update_layout(coloraxis_showscale=False)
            show_chart(fig, 340)
            st.caption("Green: fair price above today's price. Red: below.")

    # Where today's price sits among my zones
    with st.container(border=True, key="card_zones"):
        st.markdown("**My zones for this company**")
        fig = go.Figure()
        fig.add_vrect(x0=0, x1=fair_value * (1 - safety), fillcolor=status_colours["BUY EXTRA"], opacity=0.18, line_width=0, annotation_text="Buy extra", annotation_position="top left")
        fig.add_vrect(x0=fair_value * (1 - safety), x1=fair_value * 1.10, fillcolor=status_colours["KEEP BUYING"], opacity=0.12, line_width=0, annotation_text="Keep buying", annotation_position="top left")
        fig.add_vrect(x0=fair_value * 1.10, x1=fair_value * 1.5, fillcolor=status_colours["PAUSE"], opacity=0.15, line_width=0, annotation_text="Pause", annotation_position="top left")
        fig.add_vrect(x0=fair_value * 1.5, x1=fair_value * 2, fillcolor=status_colours["SELL PART"], opacity=0.15, line_width=0, annotation_text="Sell part", annotation_position="top left")
        fig.add_trace(go.Scatter(x=[price], y=[0.5], mode="markers+text", text=[f"Today {price:,.0f}"], textposition="bottom center", marker=dict(size=16, color=colours["text"])))
        fig.update_layout(showlegend=False, yaxis_visible=False, xaxis_range=[fair_value * 0.5, fair_value * 1.7], xaxis_title=company["currency"])
        show_chart(fig, 180)

# ---------------- Alerts and Trade Republic levels ----------------
with tab_alerts:
    # Alerts from the weekly check
    st.subheader(":material/notifications_active: This week's alerts")
    if len(alerts) > 0:
        st.caption("Last check: " + last_check + ". I never sell just because the price fell.")

        # How many alerts of each type
        counts = alerts["type"].value_counts()
        labels = ""
        for kind in counts.index:
            labels = labels + pill(f"{counts[kind]} {kind}", alert_colours.get(kind, colours["loss"]))
        st.markdown(labels, unsafe_allow_html=True)

        # One box per alert: green is good news, yellow is something to do, red is a warning
        for _, alert in alerts.iterrows():
            text = f"**{alert['type']}** · {alert['product']}: {alert['message']}"
            if alert["type"] in ["OK", "BUY", "BUY EXTRA", "CLOSE", "PRIORITY BUY BIG", "PRIORITY START PLAN", "PRIORITY CLOSE"]:
                st.success(text, icon=":material/check_circle:")
            elif alert["type"] == "KEEP":
                with st.expander(f"KEEP · {alert['product']}", icon=":material/thumb_up:"):
                    st.write(alert["message"])
            elif alert["type"] in ["STOP BUYING", "PAUSE", "RESULTS", "REVIEW ASSUMPTION", "REVIEW MORNINGSTAR"]:
                st.warning(text, icon=":material/schedule:")
            else:
                st.error(text, icon=":material/warning:")
    else:
        st.write("No check yet: run python future/alerts.py")

    # Calendar: next results of my stocks and the watchlist
    st.subheader(":material/event: Next results")
    calendar = fair.dropna(subset=["next_results"]).sort_values("next_results")
    if len(calendar) > 0:
        with st.container(border=True, key="card_calendar"):
            st.dataframe(calendar[["next_results", "name", "list"]], hide_index=True, column_config={"next_results": "Date", "name": "Company", "list": "List"})
    else:
        st.write("No dates from Yahoo yet.")

    # Price alerts to set on Trade Republic, in euros
    st.subheader(":material/notifications: Price alerts for Trade Republic (in euros)")
    st.caption("Set them with the bell on each stock page. Cheap: buy extra with a limit order (my stocks) or start the full analysis (watchlist). Expensive: pause the monthly plan, never sell on this alert alone.")
    levels = []
    for _, row in fair.iterrows():
        to_euro = 1
        if row["currency"] == "USD":
            to_euro = 1 / rate
        if row["list"] == "portfolio":
            levels.append([row["name"], "My stock", row["entry"] * to_euro, row["fair"] * 1.10 * to_euro, row["fair"] * 1.5 * to_euro, row["price"] * to_euro])
        elif row["list"] == "priority":
            levels.append([row["name"], "Top priority", row["start"] * to_euro, None, None, row["price"] * to_euro])
        else:
            levels.append([row["name"], "Watchlist", row["start"] * to_euro, None, None, row["price"] * to_euro])
    levels = pd.DataFrame(levels, columns=["name", "list", "cheap", "pause", "sell_part", "today"])
    levels["distance"] = (levels["cheap"] / levels["today"] - 1) * 100
    with st.container(border=True, key="card_levels"):
        st.dataframe(
            levels.sort_values(["list", "distance"], ascending=[True, False]),
            hide_index=True,
            column_config={
                "name": "Company",
                "list": "List",
                "today": st.column_config.NumberColumn("Price today", format="%.0f €"),
                "cheap": st.column_config.NumberColumn("Alert: cheap", format="%.0f €"),
                "distance": st.column_config.NumberColumn("Fall needed", format="%+.0f%%"),
                "pause": st.column_config.NumberColumn("Alert: pause plan", format="%.0f €"),
                "sell_part": st.column_config.NumberColumn("Sell part above", format="%.0f €"),
            },
        )
    st.download_button("Download the levels (CSV)", levels.round(0).to_csv(index=False), "tr_alerts.csv", icon=":material/download:")
