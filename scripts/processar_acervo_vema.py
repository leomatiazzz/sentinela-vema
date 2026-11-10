"""
Normalizador do acervo da VEMA.
Lê o JSON bruto da coleta, estrutura em banco relacional SQLite e exporta CSV.
"""
import os
import json
import sqlite3
import pandas as pd
from datetime import datetime

INPUT_JSON = "data/raw/acervo_vema_bruto.json"
OUTPUT_DB = "data/processed/vema.db"
OUTPUT_CSV = "data/processed/acervo_vema.csv"

def formatar_data(data_str):
    """Converte formato YYYYMMDDHHMMSS ou YYYYMMDD para ISO YYYY-MM-DD HH:MM:SS"""
    if not data_str:
        return None, None
    s = str(data_str).strip()
    try:
        if len(s) >= 14:
            dt = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.year
        elif len(s) >= 8:
            dt = datetime.strptime(s[:8], "%Y%m%d")
            return dt.strftime("%Y-%m-%d"), dt.year
    except Exception:
        pass
    return s, None

def processar_acervo():
    if not os.path.exists(INPUT_JSON):
        print(f"Arquivo não encontrado: {INPUT_JSON}. Execute primeiro o coletor.")
        return

    print("=" * 65)
    print("Normalizando dados do acervo da VEMA...")
    print(f"Lendo: {INPUT_JSON}")
    print("=" * 65)

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        processos_raw = json.load(f)

    print(f"Total de processos brutos carregados: {len(processos_raw)}")

    os.makedirs(os.path.dirname(OUTPUT_DB), exist_ok=True)
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()

    # Criação das tabelas relacionais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processos (
        id TEXT PRIMARY KEY,
        numero_processo TEXT UNIQUE,
        grau TEXT,
        classe_codigo INTEGER,
        classe_nome TEXT,
        orgao_codigo INTEGER,
        orgao_nome TEXT,
        municipio_ibge INTEGER,
        data_ajuizamento TEXT,
        ano_ajuizamento INTEGER,
        data_ultima_atualizacao TEXT,
        nivel_sigilo INTEGER,
        sistema TEXT,
        formato TEXT,
        total_movimentos INTEGER,
        ultimo_movimento_data TEXT,
        ultimo_movimento_nome TEXT,
        ultimo_movimento_codigo INTEGER,
        assunto_principal TEXT,
        assuntos_completos TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assuntos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id TEXT,
        numero_processo TEXT,
        codigo INTEGER,
        nome TEXT,
        principal INTEGER,
        FOREIGN KEY(processo_id) REFERENCES processos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id TEXT,
        numero_processo TEXT,
        data_hora TEXT,
        codigo INTEGER,
        nome TEXT,
        FOREIGN KEY(processo_id) REFERENCES processos(id)
    )
    """)

    # Índices para consultas ultra-rápidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proc_numero ON processos(numero_processo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proc_classe ON processos(classe_nome)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proc_ano ON processos(ano_ajuizamento)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assuntos_proc ON assuntos(processo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assuntos_nome ON assuntos(nome)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mov_proc ON movimentos(processo_id)")

    # Limpa dados anteriores para reconstrução limpa
    cursor.execute("DELETE FROM movimentos")
    cursor.execute("DELETE FROM assuntos")
    cursor.execute("DELETE FROM processos")

    registros_tabular = []
    
    for p in processos_raw:
        doc_id = p.get("id") or p.get("numeroProcesso")
        num_proc = p.get("numeroProcesso")
        grau = p.get("grau")
        
        classe = p.get("classe", {})
        classe_cod = classe.get("codigo")
        classe_nome = classe.get("nome")
        
        orgao = p.get("orgaoJulgador", {})
        orgao_cod = orgao.get("codigo")
        orgao_nome = orgao.get("nome")
        municipio_ibge = orgao.get("codigoMunicipioIBGE")
        
        data_aj_iso, ano_aj = formatar_data(p.get("dataAjuizamento"))
        data_atualizacao = p.get("dataHoraUltimaAtualizacao")
        nivel_sigilo = p.get("nivelSigilo")
        
        sistema = p.get("sistema")
        if isinstance(sistema, dict):
            sistema = sistema.get("nome")
            
        formato = p.get("formato")
        if isinstance(formato, dict):
            formato = formato.get("nome")
            
        # Movimentações
        movs = p.get("movimentos", [])
        total_movs = len(movs)
        ult_mov_data, ult_mov_nome, ult_mov_cod = None, None, None
        
        if movs:
            # Ordena por dataHora se disponível
            movs_ordenados = sorted(
                movs, 
                key=lambda m: str(m.get("dataHora", "")), 
                reverse=True
            )
            ult = movs_ordenados[0]
            ult_mov_data, _ = formatar_data(ult.get("dataHora"))
            ult_mov_nome = ult.get("nome")
            ult_mov_cod = ult.get("codigo")
            
            # Insere no banco os movimentos
            for m in movs:
                m_data, _ = formatar_data(m.get("dataHora"))
                cursor.execute("""
                INSERT INTO movimentos (processo_id, numero_processo, data_hora, codigo, nome)
                VALUES (?, ?, ?, ?, ?)
                """, (doc_id, num_proc, m_data, m.get("codigo"), m.get("nome")))
                
        # Assuntos
        assuntos_list = p.get("assuntos", [])
        nomes_assuntos = []
        assunto_principal = None
        
        for idx, a in enumerate(assuntos_list):
            if isinstance(a, dict):
                a_cod = a.get("codigo")
                a_nome = a.get("nome", "").strip()
                is_principal = 1 if (a.get("principal") is True or idx == 0) else 0
                if is_principal and not assunto_principal:
                    assunto_principal = a_nome
                if a_nome:
                    nomes_assuntos.append(a_nome)
                cursor.execute("""
                INSERT INTO assuntos (processo_id, numero_processo, codigo, nome, principal)
                VALUES (?, ?, ?, ?, ?)
                """, (doc_id, num_proc, a_cod, a_nome, is_principal))
                
        assuntos_completos = " | ".join(nomes_assuntos)
        if not assunto_principal and nomes_assuntos:
            assunto_principal = nomes_assuntos[0]
            
        # Insere processo
        cursor.execute("""
        INSERT INTO processos (
            id, numero_processo, grau, classe_codigo, classe_nome,
            orgao_codigo, orgao_nome, municipio_ibge, data_ajuizamento,
            ano_ajuizamento, data_ultima_atualizacao, nivel_sigilo,
            sistema, formato, total_movimentos, ultimo_movimento_data,
            ultimo_movimento_nome, ultimo_movimento_codigo,
            assunto_principal, assuntos_completos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, num_proc, grau, classe_cod, classe_nome,
            orgao_cod, orgao_nome, municipio_ibge, data_aj_iso,
            ano_aj, data_atualizacao, nivel_sigilo,
            sistema, formato, total_movs, ult_mov_data,
            ult_mov_nome, ult_mov_cod,
            assunto_principal, assuntos_completos
        ))
        
        registros_tabular.append({
            "numero_processo": num_proc,
            "classe_nome": classe_nome,
            "classe_codigo": classe_cod,
            "assunto_principal": assunto_principal,
            "assuntos_completos": assuntos_completos,
            "ano_ajuizamento": ano_aj,
            "data_ajuizamento": data_aj_iso,
            "total_movimentos": total_movs,
            "ultimo_movimento_data": ult_mov_data,
            "ultimo_movimento_nome": ult_mov_nome,
            "grau": grau,
            "sistema": sistema,
            "formato": formato,
            "nivel_sigilo": nivel_sigilo
        })

    conn.commit()
    conn.close()
    print(f"Banco SQLite atualizado com sucesso: {OUTPUT_DB}")

    # Exportação para CSV
    df = pd.DataFrame(registros_tabular)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Planilha CSV exportada com sucesso: {OUTPUT_CSV}")
    print(f"Total de registros processados: {len(df)}")

if __name__ == "__main__":
    processar_acervo()

