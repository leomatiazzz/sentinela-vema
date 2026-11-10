"""
Verifica o acervo total da VEMA (Código 93861) no DataJud do TJCE.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATAJUD_API_KEY")
URL = os.getenv("DATAJUD_TJCE_URL", "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search")

headers = {
    "Authorization": f"APIKey {API_KEY}",
    "Content-Type": "application/json"
}

consulta = {
    "size": 1,
    "track_total_hits": True,
    "query": {
        "term": {
            "orgaoJulgador.codigo": 93861
        }
    }
}

try:
    resp = requests.post(URL, headers=headers, json=consulta, timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        print(f"Acervo total de processos da VEMA (Código 93861) no TJCE: {total}")
    else:
        print(f"Erro: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Erro: {e}")

