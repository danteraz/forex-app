import requests

def obter_preco_forex(par="EUR/USD"):
    url = f"https://api.twelvedata.com/price?symbol={par}&apikey=demo"
    resposta = requests.get(url)
    dados = resposta.json()
    return float(dados["price"]) if "price" in dados else None
