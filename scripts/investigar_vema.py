"""
Script para descobrir como a Vara Estadual do Meio Ambiente (VEMA)
e os assuntos de Direito Ambiental estão indexados no DataJud do TJCE.
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

# 1. Busca por Órgão Julgador contendo termos como 'Ambiente' ou 'Ambiental'
print("=" * 60)
print("1. Buscando órgãos julgadores com 'Ambiente' ou 'Ambiental' no TJCE...")
print("=" * 60)

consulta_orgao = {
    "size": 50,
    "query": {
        "bool": {
            "should": [
                {"match_phrase": {"orgaoJulgador.nome": "Ambiente"}},
                {"match_phrase": {"orgaoJulgador.nome": "Ambiental"}},
                {"match_phrase": {"orgaoJulgador.nome": "Meio Ambiente"}},
                {"match_phrase": {"orgaoJulgador.nome": "Vema"}}
            ],
            "minimum_should_match": 1
        }
    }
}

try:
    resp = requests.post(URL, headers=headers, json=consulta_orgao, timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        print(f"Total encontrado por órgão: {total}")
        
        orgaos_encontrados = {}
        for h in hits:
            oj = h["_source"].get("orgaoJulgador", {})
            cod = oj.get("codigo")
            nome = oj.get("nome")
            if cod and nome:
                orgaos_encontrados[cod] = nome
        
        print("\nÓrgãos julgadores identificados:")
        for cod, nome in orgaos_encontrados.items():
            print(f"  - Código: {cod} | Nome: {nome}")
            
    else:
        print(f"Erro na busca por órgão: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Falha na busca por órgão: {e}")

# 2. Busca por Assuntos relacionados a Direito Ambiental no 1º Grau (G1)
print("\n" + "=" * 60)
print("2. Buscando processos de 1º grau (G1) com assuntos ambientais...")
print("=" * 60)

consulta_assunto = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"match": {"grau": "G1"}}
            ],
            "should": [
                {"match_phrase": {"assuntos.nome": "Direito Ambiental"}},
                {"match_phrase": {"assuntos.nome": "Dano Ambiental"}},
                {"match_phrase": {"assuntos.nome": "Meio Ambiente"}},
                {"match_phrase": {"assuntos.nome": "Poluição"}},
                {"match_phrase": {"assuntos.nome": "Revogação/Anulação de multa ambiental"}},
                {"match_phrase": {"assuntos.nome": "Flora"}},
                {"match_phrase": {"assuntos.nome": "Fauna"}}
            ],
            "minimum_should_match": 1
        }
    }
}

try:
    resp = requests.post(URL, headers=headers, json=consulta_assunto, timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        print(f"Total de processos ambientais G1 encontrados: {total}")
        
        for idx, h in enumerate(hits[:5], 1):
            src = h["_source"]
            print(f"\n[Exemplo {idx}]")
            print(f"  Número: {src.get('numeroProcesso')}")
            print(f"  Classe: {src.get('classe', {}).get('nome')} (Cód: {src.get('classe', {}).get('codigo')})")
            print(f"  Órgão: {src.get('orgaoJulgador', {}).get('nome')} (Cód: {src.get('orgaoJulgador', {}).get('codigo')})")
            print(f"  Assuntos: {[a.get('nome') for a in src.get('assuntos', [])]}")
            print(f"  Ajuizamento: {src.get('dataAjuizamento')}")
    else:
        print(f"Erro na busca por assunto: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Falha na busca por assunto: {e}")

