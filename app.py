import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Investment Lab", page_icon="📈", layout="wide")

# Read the tables that export.py made from my Excel
valuation = pd.read_csv("data/valuation.csv")
plan = pd.read_csv("data/plan.csv")
holdings = pd.read_csv("data/holdings.csv")
watch = pd.read_csv("data/watch.csv")
history = pd.read_csv("data/history.csv")
updated = history["date"].max()

# Colours for each verdict
colours = {"Strong buy": "#15803d", "Buy": "#22c55e", "Fair price": "#2563eb", "Expensive": "#d97706",
           "Very expensive": "#b91c1c", "Wait (alarm)": "#6b7280", "Waiting list": "#6b7280"}

# Title
st.title("Investment Lab")
st.caption(f"How I invest every month and how I value the companies I follow. Data from {updated}. "
           "All the maths is in my Excel model; this site only shows the results. Not investment advice.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Portfolio", "Monthly plan", "Fair value", "Watchlist", "Method"])

# Portfolio: weights and returns, never euros
with tab1:
    stocks = holdings[holdings["type"].isin(["Stock in the plan", "Stock on the watchlist", "Old stock"])]["weight"].sum()
    vwce = holdings[holdings["product"] == "VWCE"]["weight"].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("VWCE (core)", f"{vwce:.0%}")
    col2.metric("Stocks", f"{stocks:.0%}")
    col3.metric("Products", len(holdings))

    col1, col2 = st.columns(2)
    pie = px.pie(holdings, names="product", values="weight", hole=0.55, title="What I own")
    pie.update_traces(textinfo="label+percent")
    pie.update_layout(showlegend=False)
    col1.plotly_chart(pie, width="stretch")

    gains = holdings.dropna(subset=["return"]).sort_values("return")
    bars = px.bar(gains, x="return", y="product", orientation="h", title="Return since I bought")
    bars.update_traces(marker_color=["#15803d" if r >= 0 else "#b91c1c" for r in gains["return"]])
    bars.update_layout(xaxis_tickformat=".0%", xaxis_title="", yaxis_title="")
    col2.plotly_chart(bars, width="stretch")

# Monthly plan: where each euro goes this month
with tab2:
    st.write("Every month the same amount goes in on the 2nd. A fixed part goes to VWCE and a small part to Bitcoin. "
             "Each stock gets its share only if its price is within its limit; what it does not use waits in cash "
             "for a day when a company I trust gets really cheap.")
    chart = px.bar(plan.sort_values("share"), x="share", y="product", orientation="h", text="share",
                   title="Share of this month's money")
    chart.update_traces(texttemplate="%{text:.0%}", marker_color="#0f766e")
    chart.update_layout(xaxis_tickformat=".0%", xaxis_title="", yaxis_title="", height=450)
    st.plotly_chart(chart, width="stretch")

    paused = plan.merge(valuation, left_on="product", right_on="company")
    paused = paused[paused["share"] == 0][["company", "price_vs_fair", "strictness", "verdict"]]
    if len(paused) > 0:
        st.subheader("Paused this month")
        st.dataframe(paused.rename(columns={"company": "Company", "price_vs_fair": "Price vs fair",
                                            "strictness": "Strictness", "verdict": "Verdict"}),
                     hide_index=True, column_config={"Price vs fair": st.column_config.NumberColumn(format="percent")})

# Fair value: price against the bear, base and bull values of each company
with tab3:
    st.write("Each company has its own DCF with three scenarios. The bar goes from the bear to the bull value, "
             "the line is the fair value (the weighted average) and the dot is today's price. "
             "Everything is shown as a % of the fair value, so all companies fit on one chart.")
    data = valuation.sort_values("price_vs_fair", ascending=False)
    field = go.Figure()
    field.add_trace(go.Bar(y=data["company"], x=data["bull"] / data["fair"] - data["bear"] / data["fair"],
                           base=data["bear"] / data["fair"] - 1, orientation="h", marker_color="#cbd5e1",
                           name="Bear to bull"))
    field.add_trace(go.Scatter(y=data["company"], x=data["price_vs_fair"], mode="markers", name="Price today",
                               marker=dict(size=12, color=[colours[v] for v in data["verdict"]])))
    field.add_vline(x=0, line_color="#111827", line_width=2)
    field.update_layout(xaxis_tickformat="+.0%", height=560, xaxis_title="Compared with the fair value",
                        legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(field, width="stretch")

    table = valuation[["company", "group", "sector", "currency", "price", "fair", "price_vs_fair", "return_if_base",
                       "wacc", "strictness", "quality", "verdict"]]
    st.dataframe(table.rename(columns={"company": "Company", "group": "Group", "sector": "Sector", "currency": "Currency",
                                       "price": "Price", "fair": "Fair value", "price_vs_fair": "Price vs fair",
                                       "return_if_base": "Return if base", "wacc": "WACC", "strictness": "Strictness",
                                       "quality": "Quality", "verdict": "Verdict"}),
                 hide_index=True, width="stretch",
                 column_config={"Price": st.column_config.NumberColumn(format="%.2f"),
                                "Fair value": st.column_config.NumberColumn(format="%.2f"),
                                "Price vs fair": st.column_config.NumberColumn(format="percent"),
                                "Return if base": st.column_config.NumberColumn(format="percent"),
                                "WACC": st.column_config.NumberColumn(format="percent")})

    st.subheader("Price and fair value over time")
    pick = st.selectbox("Company", valuation["company"])
    ticker = valuation[valuation["company"] == pick]["ticker"].iloc[0]
    one = history[history["ticker"] == ticker]
    line = px.line(one, x="date", y=["price", "fair"], markers=True)
    line.update_layout(xaxis_title="", yaxis_title="", legend_title="")
    st.plotly_chart(line, width="stretch")
    st.caption("One point per month. The fair value only moves when the business or the rates change, not with the price.")

# Watchlist: the prices that trigger an extra buy
with tab4:
    st.write("An extra buy happens on any day a company falls below its trigger: far below fair value, or a big fall "
             "from its 52 week high while below fair value. I check these prices against Trade Republic.")
    table = watch.sort_values("priority")[["company", "currency", "price", "trigger", "trigger_eur", "distance", "state"]]
    st.dataframe(table.rename(columns={"company": "Company", "currency": "Currency", "price": "Price",
                                       "trigger": "Buy below", "trigger_eur": "Buy below (€)",
                                       "distance": "Fall needed", "state": "State"}),
                 hide_index=True, width="stretch",
                 column_config={"Price": st.column_config.NumberColumn(format="%.2f"),
                                "Buy below": st.column_config.NumberColumn(format="%.2f"),
                                "Buy below (€)": st.column_config.NumberColumn(format="%.2f €"),
                                "Fall needed": st.column_config.NumberColumn(format="percent")})
    st.caption("Fall needed: how much the price still has to drop. Positive means it is already below the trigger.")

# Method: the same text as METHOD.md
with tab5:
    st.markdown(open("METHOD.md", encoding="utf-8").read())
