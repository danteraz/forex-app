import requests
import pandas as pd
import yfinance as yf

API_KEY = "25f1ed33b0304894ab4d8d390f81da07"  # Substitua por sua chave da TwelveData se quiser mais requisições

def obter_preco_atual(par="EUR/USD"):
    url = f"https://api.twelvedata.com/price?symbol={par}&apikey={API_KEY}"
    try:
        r = requests.get(url).json()
        return float(r["price"]) if "price" in r else None
    except:
        return None

def obter_historico(par="EUR/USD", intervalo="1h", qtd=50):
    """Tenta obter dados da TwelveData, se falhar, usa Yahoo Finance"""
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={par}&interval={intervalo}&apikey={API_KEY}&outputsize={qtd}"
        r = requests.get(url).json()
        if "values" not in r:
            raise Exception("Sem valores")
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["close"] = df["close"].astype(float)
        return df.sort_values("datetime")
    except:
        # Fallback: usa yfinance
        simbolo = converter_para_yfinance(par)
        df_y = yf.download(simbolo, period="5d", interval="1h", progress=False, auto_adjust=False)

        if df_y.empty:
            return None
        df_y.reset_index(inplace=True)
        df_y.rename(columns={"Close": "close", "Datetime": "datetime"}, inplace=True)
        return df_y[["datetime", "close"]]

def converter_para_yfinance(par):
    """Converte par tipo EUR/USD para EURUSD=X (Yahoo padrão)"""
    return par.replace("/", "") + "=X"
