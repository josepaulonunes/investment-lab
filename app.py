import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Investment Lab", page_icon="📈", layout="wide")

# Read the tables that export.py made
holdings = pd.read_csv("data/holdings.csv")
themes = pd.read_csv("data/themes.csv")
track = pd.read_csv("data/track.csv")
valuation = pd.read_csv("data/valuation.csv")
ranking = pd.read_csv("data/ranking.csv")
history = pd.read_csv("data/history.csv")
updated = history["date"].max()

# Title
st.title("Investment Lab")
st.caption(f"How I invest every month and how I value the companies I follow. Data from {updated}. "
           "The decisions come from my rules and models; this site only shows them. Not investment advice.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Portfolio", "Ranking", "Fair value", "Am I beating VWCE?", "Method"])

# Portfolio: weights and returns, never euros
with tab1:
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

    st.subheader("Each theme against its limit")
    limits = go.Figure()
    limits.add_trace(go.Bar(y=themes["theme"], x=themes["weight"], orientation="h", name="Weight today",
                            marker_color=["#b91c1c" if w > l else "#0f766e" for w, l in zip(themes["weight"], themes["limit"])]))
    limits.add_trace(go.Scatter(y=themes["theme"], x=themes["limit"], mode="markers", name="Limit",
                                marker=dict(symbol="line-ns", size=24, line=dict(width=3, color="#111827"))))
    limits.update_layout(xaxis_tickformat=".0%", height=350, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(limits, width="stretch")
    st.caption("Themes are a share of the money in stocks; the index is a share of the whole portfolio. "
               "Chips may go above 60% until 31 March 2027 while the portfolio is still small.")

# Ranking: gates, points and analyst revisions
with tab2:
    st.write("Every Monday 64 companies go through five gates (size, liquidity, analysts, profit and cash). "
             "The ones that pass are ranked by 18 criteria, with analyst estimate revisions weighing the most. "
             "🔥 means a big opportunity, ⚠ means analysts are cutting their estimates.")
    show = ranking[["pos", "company", "group", "points", "eps_revision_90d", "from_52w_high", "change", "signal", "next_results"]]
    st.dataframe(show.rename(columns={"pos": "#", "company": "Company", "group": "Group", "points": "Points",
                                      "eps_revision_90d": "EPS revision 90d", "from_52w_high": "From 52w high",
                                      "change": "Places moved", "signal": "Signal", "next_results": "Next results"}),
                 hide_index=True, width="stretch", height=600,
                 column_config={"Points": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
                                "EPS revision 90d": st.column_config.NumberColumn(format="percent"),
                                "From 52w high": st.column_config.NumberColumn(format="percent")})

# Fair value: price against the bear, base and bull values of each company
with tab3:
    st.write("Each company has its own 10 year DCF with three scenarios. The bar goes from the bear to the bull value, "
             "the line is the base value and the dot is today's price, all as a % of the base value.")
    only = st.radio("Show", ["All", "Top 8 and followed closely"], horizontal=True)
    data = valuation if only == "All" else valuation[valuation["priority"].notna()]
    data = data.sort_values("price_vs_base", ascending=False)
    field = go.Figure()
    field.add_trace(go.Bar(y=data["company"], x=data["bull"] / data["base"] - data["bear"] / data["base"],
                           base=data["bear"] / data["base"] - 1, orientation="h", marker_color="#cbd5e1",
                           name="Bear to bull"))
    field.add_trace(go.Scatter(y=data["company"], x=data["price_vs_base"], mode="markers", name="Price today",
                               marker=dict(size=11, color=["#15803d" if p <= 0 else "#b91c1c" for p in data["price_vs_base"]])))
    field.add_vline(x=0, line_color="#111827", line_width=2)
    field.update_layout(xaxis_tickformat="+.0%", height=max(400, 28 * len(data)), xaxis_title="Compared with the base value",
                        legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(field, width="stretch")

    table = data[["company", "priority", "currency", "price", "bear", "base", "bull", "price_vs_base", "wacc",
                  "implied_wacc", "alert1_eur", "alert2_eur", "why"]]
    st.dataframe(table.rename(columns={"company": "Company", "priority": "Priority", "currency": "Currency",
                                       "price": "Price", "bear": "Bear", "base": "Base", "bull": "Bull",
                                       "price_vs_base": "Price vs base", "wacc": "WACC", "implied_wacc": "WACC the price implies",
                                       "alert1_eur": "Alert 1 (€)", "alert2_eur": "Alert 2 (€)", "why": "Why I follow it"}),
                 hide_index=True, width="stretch",
                 column_config={"Price vs base": st.column_config.NumberColumn(format="percent"),
                                "WACC": st.column_config.NumberColumn(format="percent"),
                                "WACC the price implies": st.column_config.NumberColumn(format="percent")})
    st.caption("WACC the price implies: the discount rate at which my base case equals today's price. "
               "Below my WACC means the market expects more than my base case.")

    st.subheader("Price and base value over time")
    pick = st.selectbox("Company", valuation["company"])
    ticker = valuation[valuation["company"] == pick]["ticker"].iloc[0]
    line = px.line(history[history["ticker"] == ticker], x="date", y=["price", "base"], markers=True)
    line.update_layout(xaxis_title="", yaxis_title="", legend_title="")
    st.plotly_chart(line, width="stretch")

# Am I beating VWCE? Real portfolio and ghost portfolio, in % only
with tab4:
    last = track.iloc[-1]
    st.write("Two tests. The real one: my portfolio against putting every euro in VWCE on the same days. "
             "The ghost one: a paper portfolio that follows my rules strictly every month, against the same money only in VWCE.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("My portfolio", f"{last['real']:.1%}")
    col2.metric("Same money in VWCE", f"{last['real_if_vwce']:.1%}", f"{last['real'] - last['real_if_vwce']:+.1%} for me")
    col3.metric("Ghost portfolio", f"{last['ghost']:.1%}")
    col4.metric("Ghost money in VWCE", f"{last['ghost_if_vwce']:.1%}", f"{last['ghost'] - last['ghost_if_vwce']:+.1%} for the rules")
    if len(track) > 1:
        lines = px.line(track, x="date", y=["real", "real_if_vwce", "ghost", "ghost_if_vwce"], markers=True)
        lines.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="", legend_title="")
        st.plotly_chart(lines, width="stretch")
    st.caption("If my stocks do worse than VWCE for long, the honest answer is to put more in VWCE.")

# Method: the same text as METHOD.md
with tab5:
    st.markdown(open("METHOD.md", encoding="utf-8").read())
