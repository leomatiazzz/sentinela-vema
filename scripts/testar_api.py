"""
Script para teste de conectividade e inspeção de esquema da API Pública do DataJud (TJCE).
"""
import os
import json
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

API_KEY = os.getenv("DATAJUD_API_KEY")
URL = os.getenv(
    "DATAJUD_TJCE_URL", 
    "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search"
)

if not API_KEY:
    raise ValueError("DATAJUD_API_KEY não foi encontrada no arquivo .env!")

headers = {
    "Authorization": f"APIKey {API_KEY}",
    "Content-Type": "application/json"
}

# Consulta teste buscando apenas 3 registros
payload = {
    "size": 2,
    "query": {
        "match_all": {}
    }
}

print("=" * 60)
print("Conectando à API Pública do DataJud - TJCE...")
print(f"Endpoint: {URL}")
print("Aguardando resposta do cluster do CNJ (timeout=60s)...")
print("=" * 60)

try:
    response = requests.post(URL, headers=headers, json=payload, timeout=60)
    print(f"Código de status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        hits = data.get("hits", {}).get("hits", [])
        
        print(f"Conexão bem-sucedida! Total de processos estimados: {total}")
        print(f"Registros retornados nesta consulta: {len(hits)}\n")
        
        if hits:
            primeiro = hits[0]["_source"]
            print("--- Estrutura do 1º processo retornado ---")
            print(f"Número do processo: {primeiro.get('numeroProcesso')}")
            print(f"Classe: {primeiro.get('classe')}")
            print(f"Órgão julgador: {primeiro.get('orgaoJulgador')}")
            print(f"Assuntos: {primeiro.get('assuntos')}")
            print(f"Data de ajuizamento: {primeiro.get('dataAjuizamento')}")
            print(f"Grau: {primeiro.get('grau')}")
            print(f"Qtd movimentações: {len(primeiro.get('movimentos', []))}")
            print(f"Chaves disponíveis no _source: {list(primeiro.keys())}")
            
            # Salvar amostra para análise detalhada de campos
            os.makedirs("data/raw", exist_ok=True)
            with open("data/raw/amostra_estrutura.json", "w", encoding="utf-8") as f:
                json.dump(hits, f, ensure_ascii=False, indent=2)
            print("\nAmostra completa salva em: data/raw/amostra_estrutura.json")
    else:
        print(f"Erro na requisição ({response.status_code}):")
        print(response.text)

except Exception as e:
    print(f"Falha ao conectar: {e}")
