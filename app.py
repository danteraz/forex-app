import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.forex_api import obter_preco_atual, obter_historico

st.set_page_config(page_title="📈 Forex App", layout="wide")
st.title("📊 Painel de Forex - App Pessoal")

# Par de moedas disponíveis
pares = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
    "NZD/USD", "USD/CAD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
]
par = st.selectbox("Escolha o par de moedas", pares)

# Exibir preço atual
preco = obter_preco_atual(par)
if preco:
    st.metric(label=f"💰 Preço atual de {par}", value=f"${preco}")
else:
    st.error("Erro ao obter o preço do par.")

# Histórico + Média Móvel
df = obter_historico(par)

if df is None or df.empty:
    st.warning("⚠️ Dados históricos não disponíveis para este par de moedas.")
    st.stop()

# Cálculo de média móvel
df["SMA9"] = df["close"].rolling(window=9).mean()
df["SMA21"] = df["close"].rolling(window=21).mean()

# Plotando gráfico
st.subheader("📈 Gráfico de Preços e Médias Móveis")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["datetime"], df["close"], label="Preço", color="black")
ax.plot(df["datetime"], df["SMA9"], label="Média Móvel 9", linestyle="--")
ax.plot(df["datetime"], df["SMA21"], label="Média Móvel 21", linestyle=":")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Alerta Simples de Sinal de Compra/Venda
if df["SMA9"].iloc[-2] < df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] > df["SMA21"].iloc[-1]:
    st.success("🔔 SINAL DE **COMPRA** detectado (SMA9 cruzou para cima a SMA21)")
elif df["SMA9"].iloc[-2] > df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] < df["SMA21"].iloc[-1]:
    st.error("🔔 SINAL DE **VENDA** detectado (SMA9 cruzou para baixo a SMA21)")
else:
    st.info("⏳ Nenhum sinal claro no momento.")
