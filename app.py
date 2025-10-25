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
else:
    # Cálculo de médias e gráfico
    df["SMA9"] = df["close"].rolling(window=9).mean()
    df["SMA21"] = df["close"].rolling(window=21).mean()

    st.subheader("📈 Gráfico de Preços e Médias Móveis")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["datetime"], df["close"], label="Preço", color="black")
    ax.plot(df["datetime"], df["SMA9"], label="Média Móvel 9", linestyle="--")
    ax.plot(df["datetime"], df["SMA21"], label="Média Móvel 21", linestyle=":")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Alerta de sinal
    if df["SMA9"].iloc[-2] < df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] > df["SMA21"].iloc[-1]:
        st.success("🔔 SINAL DE **COMPRA** detectado (SMA9 cruzou para cima a SMA21)")
    elif df["SMA9"].iloc[-2] > df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] < df["SMA21"].iloc[-1]:
        st.error("🔔 SINAL DE **VENDA** detectado (SMA9 cruzou para baixo a SMA21)")
    else:
        st.info("⏳ Nenhum sinal claro no momento.")

    # ====================
    # Simulação de operações
    # ====================
    st.subheader("🛒 Operações Simuladas")

    if "historico" not in st.session_state:
        st.session_state.historico = []

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Comprar"):
            st.session_state.historico.append({
                "Data": pd.Timestamp.now(),
                "Par": par,
                "Preço": preco,
                "Operação": "COMPRA"
            })

    with col2:
        if st.button("❌ Vender"):
            st.session_state.historico.append({
                "Data": pd.Timestamp.now(),
                "Par": par,
                "Preço": preco,
                "Operação": "VENDA"
            })

    df_ops = pd.DataFrame(st.session_state.historico)

    if not df_ops.empty:
        st.dataframe(df_ops.sort_values("Data", ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma operação simulada registrada ainda.")
