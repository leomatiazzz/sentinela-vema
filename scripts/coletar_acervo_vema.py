"""
Coletor paginado do acervo da Vara Estadual do Meio Ambiente (VEMA) - TJCE.
Utiliza a API Pública do DataJud (CNJ) com paginação search_after.
"""
import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATAJUD_API_KEY")
URL = os.getenv(
    "DATAJUD_TJCE_URL", 
    "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search"
)

CODIGO_VEMA = 93861
PAGE_SIZE = 100
OUTPUT_PATH = "data/raw/acervo_vema_bruto.json"

if not API_KEY:
    raise ValueError("DATAJUD_API_KEY não configurada no arquivo .env!")

headers = {
    "Authorization": f"APIKey {API_KEY}",
    "Content-Type": "application/json"
}

def coletar_acervo_completo():
    print("=" * 65)
    print("Iniciando coleta paginada do acervo da VEMA (Cód: 93861)...")
    print(f"Endpoint: {URL}")
    print(f"Tamanho do lote por página: {PAGE_SIZE}")
    print("=" * 65)
    
    processos_coletados = []
    ids_vistos = set()
    search_after = None
    pagina = 1
    total_estimado = None
    
    while True:
        payload = {
            "size": PAGE_SIZE,
            "track_total_hits": True,
            "query": {
                "term": {
                    "orgaoJulgador.codigo": CODIGO_VEMA
                }
            },
            "sort": [
                {"@timestamp": {"order": "asc"}},
                {"id.keyword": {"order": "asc"}}
            ]
        }
        
        if search_after:
            payload["search_after"] = search_after
            
        print(f"\n[Página {pagina}] Requisitando lote...", end=" ", flush=True)
        inicio_req = time.time()
        
        try:
            resp = requests.post(URL, headers=headers, json=payload, timeout=90)
            tempo_req = time.time() - inicio_req
            
            if resp.status_code != 200:
                print(f"\n[ERRO] Status {resp.status_code}: {resp.text}")
                print("Aguardando 5 segundos para nova tentativa...")
                time.sleep(5)
                continue
                
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            
            if total_estimado is None:
                total_estimado = data.get("hits", {}).get("total", {}).get("value", 0)
                print(f"\n[Total estimado no acervo]: {total_estimado} processos.")
                
            if not hits:
                print("Nenhum registro retornado. Fim da paginação.")
                break
                
            novos_na_pagina = 0
            for h in hits:
                doc_id = h.get("_id") or h["_source"].get("id") or h["_source"].get("numeroProcesso")
                if doc_id not in ids_vistos:
                    ids_vistos.add(doc_id)
                    processos_coletados.append(h["_source"])
                    novos_na_pagina += 1
                    
            print(f"Recebidos {len(hits)} registros ({novos_na_pagina} novos) em {tempo_req:.1f}s.")
            print(f"Progresso acumulado: {len(processos_coletados)} / {total_estimado} processos.")
            
            # Atualiza o ponteiro search_after com o sort do último registro
            search_after = hits[-1].get("sort")
            pagina += 1
            
            # Se recebemos menos do que o page_size, chegamos ao final
            if len(hits) < PAGE_SIZE:
                print("Último lote incompleto recebido. Coleta finalizada com sucesso.")
                break
                
            # Intervalo respeitoso entre requisições para evitar rate-limit
            time.sleep(1.0)
            
        except requests.exceptions.Timeout:
            print("\n[TIMEOUT] A requisição excedeu 90s. Tentando novamente...")
            time.sleep(3)
        except Exception as e:
            print(f"\n[EXCEÇÃO] Falha na requisição: {e}")
            time.sleep(3)
            
    print("\n" + "=" * 65)
    print(f"Coleta concluída! Total de processos únicos capturados: {len(processos_coletados)}")
    print("=" * 65)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(processos_coletados, f, ensure_ascii=False, indent=2)
        
    print(f"Arquivo bruto salvo com sucesso em: {OUTPUT_PATH}")
    return processos_coletados

if __name__ == "__main__":
    coletar_acervo_completo()

