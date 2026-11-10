"""
Camada de acesso a dados (DAO) do acervo da VEMA.
Gerencia consultas ao banco de dados relacional SQLite local.
"""
import os
import sqlite3
import pandas as pd

DEFAULT_DB_PATH = "data/processed/vema.db"

def get_connection(db_path=DEFAULT_DB_PATH):
    """Retorna uma conexão ativa com o banco SQLite."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Banco de dados não encontrado em {db_path}. Execute processar_acervo_vema.py.")
    return sqlite3.connect(db_path)

def carregar_todos_processos(db_path=DEFAULT_DB_PATH):
    """Carrega todos os 1.030 processos da VEMA em um DataFrame."""
    conn = get_connection(db_path)
    query = """
    SELECT 
        id, numero_processo, grau, classe_codigo, classe_nome,
        orgao_codigo, orgao_nome, municipio_ibge, data_ajuizamento,
        ano_ajuizamento, data_ultima_atualizacao, nivel_sigilo,
        sistema, formato, total_movimentos, ultimo_movimento_data,
        ultimo_movimento_nome, ultimo_movimento_codigo,
        assunto_principal, assuntos_completos
    FROM processos
    ORDER BY ano_ajuizamento DESC, data_ajuizamento DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def buscar_processo_por_numero(numero_processo, db_path=DEFAULT_DB_PATH):
    """Localiza um processo específico pelo número CNJ (com ou sem máscara)."""
    # Remove caracteres não numéricos para comparação
    num_limpo = "".join(filter(str.isdigit, str(numero_processo)))
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM processos 
    WHERE numero_processo = ? OR REPLACE(REPLACE(REPLACE(REPLACE(numero_processo, '.', ''), '-', ''), '/', ''), ' ', '') = ?
    """, (numero_processo, num_limpo))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    col_names = [desc[0] for desc in cursor.description]
    proc_dict = dict(zip(col_names, row))
    
    # Carrega assuntos do processo
    cursor.execute("SELECT codigo, nome, principal FROM assuntos WHERE processo_id = ?", (proc_dict["id"],))
    assuntos = [{"codigo": r[0], "nome": r[1], "principal": bool(r[2])} for r in cursor.fetchall()]
    proc_dict["lista_assuntos"] = assuntos
    
    # Carrega movimentações do processo
    cursor.execute("SELECT data_hora, codigo, nome FROM movimentos WHERE processo_id = ? ORDER BY data_hora DESC", (proc_dict["id"],))
    movimentos = [{"data_hora": r[0], "codigo": r[1], "nome": r[2]} for r in cursor.fetchall()]
    proc_dict["lista_movimentos"] = movimentos
    
    conn.close()
    return proc_dict

def obter_estatisticas_gerais(db_path=DEFAULT_DB_PATH):
    """Retorna métricas chave do acervo da VEMA para exibição rápida."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM processos")
    total_processos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM movimentos")
    total_movimentos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT classe_nome) FROM processos")
    total_classes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT nome) FROM assuntos WHERE nome != ''")
    total_assuntos = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_processos": total_processos,
        "total_movimentos": total_movimentos,
        "total_classes": total_classes,
        "total_assuntos": total_assuntos
    }

