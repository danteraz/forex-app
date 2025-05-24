import streamlit as st
from utils.forex_api import obter_preco_forex

st.set_page_config(page_title="Forex App", layout="wide")

st.title("📈 Painel de Forex - App Pessoal")

par = st.selectbox("Escolha o par de moedas", ["EUR/USD", "GBP/USD", "USD/JPY"])

preco = obter_preco_forex(par)

if preco:
    st.metric(label=f"Preço atual de {par}", value=f"${preco}")
else:
    st.error("Erro ao obter o preço do par selecionado.")
