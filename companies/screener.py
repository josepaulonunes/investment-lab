import yfinance as yf
import pandas as pd
import warnings

# Hide library warnings and show wide tables
warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)

# Same DCF as analyse_company.py: 10 years of free cash flow plus a terminal value
def dcf_value(fcf, growth, terminal, discount):
    value = 0
    cash = fcf
    for year in range(1, 11):
        cash = cash * (1 + growth)
        value = value + cash / (1 + discount) ** year
    terminal_value = cash * (1 + terminal) / (discount - terminal)
    value = value + terminal_value / (1 + discount) ** 10
    return value

# Companies I find interesting (add a line to the csv to add a company)
watchlist = pd.read_csv("data/companies/watchlist.csv")

# Get the main numbers of each company from yfinance
rows = []
for _, company in watchlist.iterrows():
    print("Loading", company["name"])
    stock = yf.Ticker(company["ticker"])
    info = stock.info
    if not info.get("marketCap"):
        print("No data for", company["name"], "- check the ticker")
        continue
    roe = info.get("returnOnEquity")
    debt = info.get("totalDebt") or 0
    cash = info.get("totalCash") or 0
    ebitda = info.get("ebitda")
    growth = info.get("revenueGrowth")
    pe_forward = info.get("forwardPE")
    market_cap = info.get("marketCap")

    # Free cash flow from the last annual cash flow statement (closer to the company's own figure)
    fcf = None
    cashflow = stock.cashflow
    if "Free Cash Flow" in cashflow.index:
        values = cashflow.loc["Free Cash Flow"].dropna()
        if len(values) > 0:
            fcf = values.iloc[0]

    net_debt_to_ebitda = None
    if ebitda:
        net_debt_to_ebitda = (debt - cash) / ebitda

    # Quick reverse DCF: FCF growth per year the price already assumes (9% discount, 2.5% terminal)
    same_currency = info.get("financialCurrency") == info.get("currency")
    implied_growth = None
    if fcf and fcf > 0 and market_cap and same_currency:
        for step in range(-50, 401):
            g = step / 1000
            if dcf_value(fcf, g, 0.025, 0.09) >= market_cap:
                implied_growth = g
                break

    # Quick version of my criteria (only a first filter, not a decision)
    checks = [
        roe is not None and roe > 0.15,
        net_debt_to_ebitda is not None and net_debt_to_ebitda < 2.5,
        fcf is not None and fcf > 0,
        growth is not None and growth > 0.05,
        pe_forward is not None and 0 < pe_forward < 25,
    ]

    # Warnings: regulated sectors, cycle peaks and mixed currencies
    sector = info.get("sector")
    warning = ""
    if not same_currency:
        warning = "Reports and trades in different currencies"
    if growth is not None and growth > 0.5:
        warning = "Cycle peak?"
    if sector in ["Utilities", "Energy"]:
        warning = "Regulated sector: check conflicts of interest"

    rows.append({
        "name": company["name"],
        "region": company["region"],
        "sector": sector,
        "roe": roe,
        "net_debt_to_ebitda": net_debt_to_ebitda,
        "revenue_growth": growth,
        "pe_forward": pe_forward,
        "implied_growth": implied_growth,
        "score": checks.count(True),
        "warning": warning,
    })

# Rank by score, then by the lowest growth the price assumes (cheapest first)
screen = pd.DataFrame(rows)
screen = screen.sort_values(["score", "implied_growth"], ascending=[False, True])
screen["next_step"] = "skip"
screen.loc[(screen["score"] >= 4) & (screen["warning"] == ""), "next_step"] = "full analysis"
screen.to_csv("data/companies/screen.csv", index=False)
print()
print("SCREEN (score out of 5)")
print(screen.round(2).to_string(index=False))