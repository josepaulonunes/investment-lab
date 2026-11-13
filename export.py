import pandas as pd
import os
from datetime import date

# Where the Excel is and where the tables go
excel = "private/Carteira_DCF.xlsx"
folder = "data/"
today = date.today().isoformat()

# English names for the words in the Excel
sectors = {"Big tech e IA": "Big tech and AI", "Chips e IA": "Chips and AI", "Pagamentos": "Payments",
           "Software de gestão": "Business software", "Rede elétrica": "Power grid", "Saúde": "Health", "Energia": "Power"}
verdicts = {"Compra forte": "Strong buy", "Compra": "Buy", "Preço justo": "Fair price", "Cara": "Expensive",
            "Muito cara": "Very expensive", "Esperar (alarme)": "Wait (alarm)", "Lista de espera": "Waiting list"}
groups = {"Plano": "Monthly plan", "Observação": "Watchlist"}
strictness = {"Núcleo": "Core", "Normal": "Normal", "Exigente": "Strict"}
quality = {"Passa": "Pass", "Passa com reserva": "Pass with caveat", "Lista de espera": "Fail"}
types = {"ETF": "Core ETF", "Ação do plano": "Stock in the plan", "Ação em observação": "Stock on the watchlist",
         "Ação antiga": "Old stock", "Outro": "Gold", "Cripto": "Bitcoin", "Reserva": "Cash reserve"}
products = {"Ouro": "Gold", "Reserva para ações (dinheiro, em €)": "Cash reserve"}
states = {"Compra extra já": "Extra buy now", "Perto: ver todos os dias": "Close: check daily",
          "Ver 1 vez por semana": "Check weekly", "Longe: ver no dia 1": "Far: check monthly",
          "Não acompanhar: falha a qualidade": "Not watched: fails quality", "Não acompanhar: alarme": "Not watched: alarm"}

# Valuation of each company (sheet Painel)
panel = pd.read_excel(excel, sheet_name="Painel", header=4, nrows=15)
tests = pd.read_excel(excel, sheet_name="Painel", header=37, nrows=15, usecols="A:H")
valuation = pd.DataFrame({
    "company": panel["Empresa"],
    "ticker": panel["Folha"],
    "sector": panel["Setor"].map(sectors),
    "group": panel["Grupo"].map(groups),
    "currency": panel["Moeda"],
    "price": panel["Preço"],
    "bear": panel["Pessimista"],
    "base": panel["Base"],
    "bull": panel["Otimista"],
    "fair": panel["Valor justo"],
    "price_vs_fair": panel["Preço face ao justo"],
    "return_if_base": panel["Retorno se o base acontecer"],
    "wacc": panel["WACC"],
    "uncertainty": panel["Incerteza do valor"],
    "strictness": panel["Exigência"].map(strictness),
    "verdict": panel["Veredicto"].map(verdicts),
    "quality": tests["Qualidade"].map(quality),
})
valuation.round(4).to_csv(folder + "valuation.csv", index=False)

# Where the money of the month goes, as a share of the monthly amount
plan_rows = pd.read_excel(excel, sheet_name="Painel", header=23, nrows=5, usecols="A:C")
monthly = plan_rows["€ por mês"].iloc[-1]
plan = [["VWCE", plan_rows["€ por mês"].iloc[0] / monthly]]
for i in range(len(panel)):
    if panel["Grupo"][i] == "Plano":
        plan.append([panel["Empresa"][i], panel["€ por mês"][i] / monthly])
plan.append(["Cash reserve", plan_rows["€ por mês"].iloc[2] / monthly])
plan.append(["Bitcoin", plan_rows["€ por mês"].iloc[3] / monthly])
plan = pd.DataFrame(plan, columns=["product", "share"])
plan["share"] = plan["share"].round(4)
plan.to_csv(folder + "plan.csv", index=False)

# What I own: weights and returns only, never euros
book = pd.read_excel(excel, sheet_name="Carteira", header=3, nrows=20)
book = book[book["Valor (€)"] > 0]
holdings = pd.DataFrame({
    "product": book["Produto"].replace(products),
    "type": book["Tipo"].map(types),
    "weight": book["Valor (€)"] / book["Valor (€)"].sum(),
    "return": book["Valor (€)"] / book["Investido (€)"] - 1,
})
holdings.loc[holdings["type"] == "Cash reserve", "return"] = None
holdings.round(4).to_csv(folder + "holdings.csv", index=False)

# Prices that trigger an extra buy (sheet Acompanhar)
watch = pd.read_excel(excel, sheet_name="Acompanhar", header=3, nrows=15)
watch = pd.DataFrame({
    "company": watch["Empresa"],
    "currency": watch["Moeda"],
    "price": watch["Preço (Painel)"],
    "trigger": watch["Dispara abaixo de"],
    "trigger_eur": watch["Dispara abaixo de (€)"],
    "distance": watch["Quanto tem de cair"],
    "state": watch["Estado"].map(states),
    "priority": watch["Prioridade"],
})
watch.round(4).to_csv(folder + "watch.csv", index=False)

# History: one line per company per export, replacing today's lines if I export twice
new = valuation[["ticker", "price", "fair", "verdict"]].copy()
new.insert(0, "date", today)
if os.path.exists(folder + "history.csv"):
    old = pd.read_csv(folder + "history.csv")
    old = old[old["date"] != today]
    new = pd.concat([old, new])
new.round(2).to_csv(folder + "history.csv", index=False)

print("Exported", len(valuation), "companies on", today)
