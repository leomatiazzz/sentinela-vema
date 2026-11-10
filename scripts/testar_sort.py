"""
Testa a ordenação e o retorno do campo 'sort' para a VEMA na API do DataJud.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATAJUD_API_KEY")
URL = os.getenv("DATAJUD_TJCE_URL", "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search")

headers = {
    "Authorization": f"APIKey {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "size": 2,
    "query": {
        "term": {
            "orgaoJulgador.codigo": 93861
        }
    },
    "sort": [
        {"@timestamp": {"order": "asc"}}
    ]
}

response = requests.post(URL, headers=headers, json=payload, timeout=60)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    hits = data.get("hits", {}).get("hits", [])
    print(f"Retornados: {len(hits)}")
    for h in hits:
        print("Processo:", h["_source"].get("numeroProcesso"))
        print("Sort values:", h.get("sort"))
else:
    print(response.text)

