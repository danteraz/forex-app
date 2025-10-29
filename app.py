import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from utils.forex_api import obter_preco_atual, obter_historico

ARQUIVO_HISTORICO = Path("data/historico.csv")
ARQUIVO_HISTORICO.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="📈 Forex App", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("📌 Navegação")
pagina = st.sidebar.radio("Escolha a página:", ["🏠 Tela Principal", "🔔 Painel de Sinais"])

if "historico" not in st.session_state:
    if ARQUIVO_HISTORICO.exists():
        st.session_state.historico = pd.read_csv(ARQUIVO_HISTORICO, parse_dates=["Data"]).to_dict("records")
    else:
        st.session_state.historico = []

if pagina == "🏠 Tela Principal":
    st.title("📊 Painel de Forex - App Pessoal")

    pares = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
        "NZD/USD", "USD/CAD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
    ]
    par = st.selectbox("Escolha o par de moedas", pares)

    preco = obter_preco_atual(par)

    if isinstance(preco, (float, int)):
        st.metric(label=f"💰 Preço atual de {par}", value=f"${preco}")
    else:
        st.warning("⚠️ Preço indisponível no momento. Pode ser uma falha temporária da API.")
        preco = None

    df = obter_historico(par)

    if df is None or df.empty:
        st.warning("⚠️ Dados históricos não disponíveis para este par de moedas.")
    else:
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

        if df["SMA9"].iloc[-2] < df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] > df["SMA21"].iloc[-1]:
            st.success("🔔 SINAL DE **COMPRA** detectado (SMA9 cruzou para cima a SMA21)")
        elif df["SMA9"].iloc[-2] > df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] < df["SMA21"].iloc[-1]:
            st.error("🔔 SINAL DE **VENDA** detectado (SMA9 cruzou para baixo a SMA21)")
        else:
            st.info("⏳ Nenhum sinal claro no momento.")

        st.subheader("🛒 Operações Simuladas")
        col1, col2 = st.columns(2)

        def registrar_operacao(tipo):
            if isinstance(preco, (float, int)):
                nova_op = {
                    "Data": pd.Timestamp.now(),
                    "Par": par,
                    "Preço": preco,
                    "Operação": tipo
                }
                st.session_state.historico.append(nova_op)
                df_atual = pd.DataFrame(st.session_state.historico)
                df_atual.to_csv(ARQUIVO_HISTORICO, index=False)
            else:
                st.warning("⚠️ Preço inválido. Operação não registrada.")

        with col1:
            if st.button("✅ Comprar"):
                registrar_operacao("COMPRA")

        with col2:
            if st.button("❌ Vender"):
                registrar_operacao("VENDA")

        df_ops = pd.DataFrame(st.session_state.historico)

        if not df_ops.empty:
            st.dataframe(df_ops.sort_values("Data", ascending=False), use_container_width=True)

            lucro_total = 0
            operacoes = []
            entrada = None

            for _, row in df_ops.iterrows():
                if row["Operação"] == "COMPRA" and entrada is None:
                    entrada = row
                elif row["Operação"] == "VENDA" and entrada is not None:
                    lucro = row["Preço"] - entrada["Preço"]
                    resultado = f"{entrada['Par']}: COMPRA {entrada['Preço']:.2f} → VENDA {row['Preço']:.2f} = Lucro {lucro:.2f}"
                    operacoes.append(resultado)
                    lucro_total += lucro
                    entrada = None

            st.subheader("📊 Resultados das Operações Simuladas")

            if operacoes:
                for op in operacoes:
                    st.write("•", op)
                st.success(f"💰 Lucro/Prejuízo acumulado: **${lucro_total:.2f}**")
            else:
                st.info("Nenhum ciclo completo de COMPRA → VENDA foi registrado ainda.")
        else:
            st.info("Nenhuma operação simulada registrada ainda.")

elif pagina == "🔔 Painel de Sinais":
    st.title("🔔 Painel de Sinais de Forex - Monitoramento Ativo")

    pares = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP"]
    resultados = []

    for par in pares:
        preco = obter_preco_atual(par)
        df = obter_historico(par)

        sinal = "Indefinido"
        pode_comprar = True
        pode_vender = False

        if df is not None and not df.empty:
            df["SMA9"] = df["close"].rolling(window=9).mean()
            df["SMA21"] = df["close"].rolling(window=21).mean()

            if df["SMA9"].iloc[-2] < df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] > df["SMA21"].iloc[-1]:
                sinal = "COMPRA"
            elif df["SMA9"].iloc[-2] > df["SMA21"].iloc[-2] and df["SMA9"].iloc[-1] < df["SMA21"].iloc[-1]:
                sinal = "VENDA"
            else:
                sinal = "NEUTRO"

        df_hist = pd.DataFrame(st.session_state.historico)

        if "Par" in df_hist.columns and "Operação" in df_hist.columns:
            posicoes_abertas = df_hist[(df_hist["Par"] == par) & (df_hist["Operação"] == "COMPRA")]
            posicao_ativa = not posicoes_abertas.empty
        else:
            posicao_ativa = False

        if posicao_ativa:
            pode_comprar = False
            pode_vender = True

        resultados.append({
            "Par": par,
            "Preço Atual": preco,
            "Sinal": sinal,
            "Posição Atual": "Compra aberta" if posicao_ativa else "-",
            "Pode Comprar": pode_comprar,
            "Pode Vender": pode_vender
        })

    df_resultado = pd.DataFrame(resultados)
    st.dataframe(df_resultado[["Par", "Preço Atual", "Sinal", "Posição Atual"]], use_container_width=True)

    st.markdown("### 📌 Ações Recomendadas")

    for row in resultados:
        col1, col2, col3 = st.columns([2, 2, 2])
        preco_formatado = f"{row['Preço Atual']:.5f}" if isinstance(row['Preço Atual'], (float, int)) else "N/A"
        col1.markdown(f"**{row['Par']}** — {row['Sinal']} — Preço: {preco_formatado}")

        if row["Pode Comprar"] and row["Sinal"] == "COMPRA":
            if col2.button(f"✅ Comprar {row['Par']}", key=f"comprar_{row['Par']}"):
                if isinstance(row["Preço Atual"], (float, int)):
                    st.session_state.historico.append({
                        "Data": pd.Timestamp.now(),
                        "Par": row["Par"],
                        "Preço": row["Preço Atual"],
                        "Operação": "COMPRA"
                    })
                    pd.DataFrame(st.session_state.historico).to_csv(ARQUIVO_HISTORICO, index=False)
                else:
                    st.warning(f"⚠️ Preço inválido para {row['Par']}. Operação ignorada.")

        if row["Pode Vender"] and row["Sinal"] == "VENDA":
            if col3.button(f"❌ Vender {row['Par']}", key=f"vender_{row['Par']}"):
                if isinstance(row["Preço Atual"], (float, int)):
                    st.session_state.historico.append({
                        "Data": pd.Timestamp.now(),
                        "Par": row["Par"],
                        "Preço": row["Preço Atual"],
                        "Operação": "VENDA"
                    })
                    pd.DataFrame(st.session_state.historico).to_csv(ARQUIVO_HISTORICO, index=False)
                else:
                    st.warning(f"⚠️ Preço inválido para {row['Par']}. Operação ignorada.")
