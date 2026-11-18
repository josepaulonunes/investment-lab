import json
import os
import pandas as pd
from datetime import date

# Where the private files are and where the public tables go
private = "private/"
folder = "data/"
today = date.today().isoformat()
os.makedirs(folder, exist_ok=True)


def read(name):
    return pd.DataFrame(json.load(open(private + name, encoding="utf-8"))["rows"])


# English names for the words in my system
themes = {"Chips e hardware de IA": "AI chips and hardware", "Pagamentos": "Payments", "Saúde": "Health",
          "Big tech": "Big tech", "Energia": "Energy", "Índice": "World index (VWCE)"}
signals = {"OPORTUNIDADE": "🔥 Opportunity", "Passa": "Pass", "Revisões em baixa": "⚠ Estimates falling",
           "Chumba portões": "Fails the gates"}
groups = {"AI, cloud e software": "AI, cloud and software", "Semicondutores e fotónica": "Chips and photonics",
          "Energia e eletrificação": "Energy and the grid", "Saúde": "Health", "Cibersegurança": "Cybersecurity",
          "Quantum": "Quantum", "Outras": "Others"}
products = {"FTSE All-World (VWCE)": "VWCE"}

# My 8 priority companies (in order), plus the ones I follow closely
priority = ["ASML", "TSM", "MSFT", "LLY", "NVDA", "SNPS", "KLAC", "GOOGL"]
favourites = ["AMZN", "ANT"]

# What I own: weights and returns only, never euros
positions = read("portfolio_posicoes.json")
summary = read("portfolio_resumo.json").iloc[-1]
total = summary["total"] + summary["bolsa_saldos"]
holdings = pd.DataFrame({
    "product": positions["nome"].replace(products),
    "theme": positions["tema"].map(themes),
    "weight": positions["valor"] / total,
    "return": positions["ganho_pct"],
})
reserve = pd.DataFrame([{"product": "Cash reserve", "theme": "Cash", "weight": summary["bolsa_saldos"] / total,
                         "return": None}])
holdings = pd.concat([holdings, reserve])
holdings.round(4).to_csv(folder + "holdings.csv", index=False)

# Weight of each theme against its limit
temas = read("portfolio_temas.json")
limits = pd.DataFrame({
    "theme": temas["tema"].map(themes),
    "weight": temas["peso"],
    "limit": temas["limite"],
    "of": temas["base"].replace({"das ações": "stocks", "da carteira": "portfolio"}),
})
limits.round(4).to_csv(folder + "themes.csv", index=False)

# Did my choices beat simply buying VWCE? Real money and the ghost portfolio, in % only
ghost = read("fantasma_evolucao.json").iloc[-1]
track = pd.DataFrame([{
    "date": summary["data"],
    "real": summary["valor_real"] / summary["investido_total"] - 1,
    "real_if_vwce": summary["valor_se_vwce"] / summary["investido_total"] - 1,
    "ghost": ghost["sistema"] / ghost["investido"] - 1,
    "ghost_if_vwce": ghost["so_vwce"] / ghost["investido"] - 1,
}])
if os.path.exists(folder + "track.csv"):
    old = pd.read_csv(folder + "track.csv")
    track = pd.concat([old[old["date"] != summary["data"]], track])
track.round(4).to_csv(folder + "track.csv", index=False)

# Fair value of each company from my DCF models (bear, base, bull) and the alert prices
dcf = read("dcf_detalhado.json")
valuation = pd.DataFrame({
    "company": dcf["empresa"],
    "ticker": dcf["ticker"],
    "currency": dcf["moeda"],
    "price": dcf["preco"],
    "bear": dcf["justo_pessimista"],
    "base": dcf["justo_base"],
    "bull": dcf["justo_otimista"],
    "price_vs_base": dcf["preco"] / dcf["justo_base"] - 1,
    "wacc": dcf["wacc"],
    "implied_wacc": dcf["wacc_implicito"],
    "price_eur": dcf["preco_eur"],
    "alert1_eur": dcf["alerta1_eur"],
    "alert2_eur": dcf["alerta2_eur"],
    "why": dcf["porque"],
})
valuation["priority"] = valuation["ticker"].apply(lambda t: "Top 8" if t in priority else ("Follow closely" if t in favourites else ""))
valuation.round(4).to_csv(folder + "valuation.csv", index=False)

# Weekly ranking: gates, points and analyst revisions
ranking = read("ranking.json")
table = pd.DataFrame({
    "pos": ranking["pos"],
    "ticker": ranking["ticker"],
    "company": ranking["empresa"],
    "group": ranking["grupo"].map(groups),
    "passes_gates": ranking["passa"],
    "points": ranking["pct"],
    "eps_revision_90d": ranking["rev_eps_90d"],
    "from_52w_high": ranking["dist_max"],
    "change": ranking["mudanca"],
    "signal": ranking["sinal"].map(signals),
    "chips": ranking["chips"],
    "next_results": ranking["proximos_resultados"],
})
table.round(4).to_csv(folder + "ranking.csv", index=False)

# History: price and base fair value of each company, one line per export
new = valuation[["ticker", "price", "base"]].copy()
new.insert(0, "date", today)
if os.path.exists(folder + "history.csv"):
    old = pd.read_csv(folder + "history.csv")
    new = pd.concat([old[old["date"] != today], new])
new.round(2).to_csv(folder + "history.csv", index=False)

print("Exported", len(valuation), "valuations and", len(table), "ranked companies on", today)
