import requests
import pandas as pd

API_KEY = "demo"  # Substitua por sua chave da TwelveData se quiser mais requisições

def obter_preco_atual(par="EUR/USD"):
    url = f"https://api.twelvedata.com/price?symbol={par}&apikey={API_KEY}"
    r = requests.get(url).json()
    return float(r["price"]) if "price" in r else None

def obter_historico(par="EUR/USD", intervalo="1h", qtd=50):
    url = f"https://api.twelvedata.com/time_series?symbol={par}&interval={intervalo}&apikey={API_KEY}&outputsize={qtd}"
    r = requests.get(url).json()
    
    if "values" not in r:
        return None  # Não tem dados históricos
    
    df = pd.DataFrame(r["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = df["close"].astype(float)
    return df.sort_values("datetime")
