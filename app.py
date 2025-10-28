import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from utils.forex_api import obter_preco_atual, obter_historico

ARQUIVO_HISTORICO = Path("data/historico.csv")
ARQUIVO_HISTORICO.parent.mkdir(parents=True, exist_ok=True)

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

    # Inicializa o histórico (sessão + CSV)
    if "historico" not in st.session_state:
        if ARQUIVO_HISTORICO.exists():
            st.session_state.historico = pd.read_csv(ARQUIVO_HISTORICO, parse_dates=["Data"]).to_dict("records")
        else:
            st.session_state.historico = []

    # Botões de simulação
    col1, col2 = st.columns(2)

    def registrar_operacao(tipo):
        nova_op = {
            "Data": pd.Timestamp.now(),
            "Par": par,
            "Preço": preco,
            "Operação": tipo
        }
        st.session_state.historico.append(nova_op)
        df_atual = pd.DataFrame(st.session_state.historico)
        df_atual.to_csv(ARQUIVO_HISTORICO, index=False)

    with col1:
        if st.button("✅ Comprar"):
            registrar_operacao("COMPRA")

    with col2:
        if st.button("❌ Vender"):
            registrar_operacao("VENDA")

    df_ops = pd.DataFrame(st.session_state.historico)

    if not df_ops.empty:
        st.dataframe(df_ops.sort_values("Data", ascending=False), use_container_width=True)

        # Cálculo de lucro/prejuízo
        lucro_total = 0
        operacoes = []
        entrada = None

        for _, row in df_ops.iterrows():
            if row["Operação"] == "COMPRA" and entrada is None:
                entrada = row  # Marca o ponto de entrada
            elif row["Operação"] == "VENDA" and entrada is not None:
                # Calcula lucro/prejuízo
                lucro = row["Preço"] - entrada["Preço"]
                resultado = f"{entrada['Par']}: COMPRA {entrada['Preço']:.2f} → VENDA {row['Preço']:.2f} = Lucro {lucro:.2f}"
                operacoes.append(resultado)
                lucro_total += lucro
                entrada = None  # Reseta para aguardar nova compra

        st.subheader("📊 Resultados das Operações Simuladas")

        if operacoes:
            for op in operacoes:
                st.write("•", op)
            st.success(f"💰 Lucro/Prejuízo acumulado: **${lucro_total:.2f}**")
        else:
            st.info("Nenhum ciclo completo de COMPRA → VENDA foi registrado ainda.")
    else:
        st.info("Nenhuma operação simulada registrada ainda.")
