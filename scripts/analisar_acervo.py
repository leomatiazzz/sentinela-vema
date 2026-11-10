"""
Analisador Exploratório do Acervo da VEMA.
Gera diagnósticos estatísticos, identifica temas repetitivos e produz relatório analítico.
"""
import os
import sqlite3
import pandas as pd

DB_PATH = "data/processed/vema.db"
OUTPUT_REPORT = "data/processed/diagnostico_acervo_vema.md"

def df_to_markdown_simple(df):
    """Converte DataFrame para markdown sem depender do tabulate."""
    headers = [str(col) for col in df.columns]
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_lines = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(val) for val in row.values) + " |"
        data_lines.append(row_str)
    return "\n".join([header_line, separator_line] + data_lines)

def analisar():
    if not os.path.exists(DB_PATH):
        print(f"Banco não encontrado: {DB_PATH}. Execute primeiro processar_acervo_vema.py.")
        return

    conn = sqlite3.connect(DB_PATH)

    # 1. Indicadores Globais
    df_proc = pd.read_sql_query("SELECT * FROM processos", conn)
    df_assuntos = pd.read_sql_query("SELECT * FROM assuntos", conn)
    df_movs = pd.read_sql_query("SELECT * FROM movimentos", conn)

    total_processos = len(df_proc)
    total_movimentos = len(df_movs)
    media_movs = df_proc["total_movimentos"].mean() if total_processos > 0 else 0
    ano_min = df_proc["ano_ajuizamento"].dropna().min()
    ano_max = df_proc["ano_ajuizamento"].dropna().max()

    # 2. Top Classes Processuais
    top_classes = (
        df_proc["classe_nome"]
        .value_counts()
        .reset_index()
    )
    top_classes.columns = ["Classe processual", "Qtd processos"]
    top_classes["% do acervo"] = (top_classes["Qtd processos"] / total_processos * 100).round(1)

    # 3. Top Assuntos (Geral)
    top_assuntos = (
        df_assuntos[df_assuntos["nome"] != ""]
        ["nome"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    top_assuntos.columns = ["Assunto TPU", "Frequência"]
    top_assuntos["% de incidência"] = (top_assuntos["Frequência"] / total_processos * 100).round(1)

    # 4. Famílias de Ações Repetitivas (Mesma Classe + Mesmo Assunto Principal)
    df_repetitivos = (
        df_proc.groupby(["classe_nome", "assunto_principal"])
        .size()
        .reset_index(name="Qtd processos semelhantes")
        .sort_values(by="Qtd processos semelhantes", ascending=False)
        .head(10)
    )
    df_repetitivos.columns = ["Classe processual", "Assunto principal", "Qtd processos semelhantes"]

    # 5. Distribuição por Ano de Ajuizamento
    dist_anos = (
        df_proc["ano_ajuizamento"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    dist_anos.columns = ["Ano", "Processos ajuizados"]

    conn.close()

    # Construção do Relatório em Markdown
    md_content = f"""# Diagnóstico e raio-X do acervo da Vara Estadual do Meio Ambiente (VEMA)
*TJCE - Dados extraídos diretamente da Base Nacional de Dados do Poder Judiciário (DataJud)*

---

## 1. Visão geral do acervo
* **Total de processos mapeados:** {total_processos:,}
* **Período histórico de ajuizamento:** {int(ano_min) if pd.notnull(ano_min) else "N/A"} até {int(ano_max) if pd.notnull(ano_max) else "N/A"}
* **Total de eventos processuais (movimentações):** {total_movimentos:,}
* **Média de movimentações por processo:** {media_movs:.1f} atos por processo

---

## 2. Top 10 classes processuais mais recorrentes
As classes abaixo concentram a maior parte do esforço jurisdicional da VEMA:

{df_to_markdown_simple(top_classes.head(10))}

---

## 3. Top 15 assuntos TPU mais frequentes
Mapeamento dos temas de direito material e infrações ambientais que mais impactam a unidade:

{df_to_markdown_simple(top_assuntos)}

---

## 4. Núcleos de demandas repetitivas identificados (candidatos a julgamento em bloco)
Cruzamento entre **classe** e **assunto principal**, revelando grupos de ações com alta probabilidade de causas de pedir idênticas:

{df_to_markdown_simple(df_repetitivos)}

---

## 5. Distribuição histórica de ajuizamentos por ano
Série temporal de distribuição de ações na VEMA:

{df_to_markdown_simple(dist_anos)}

---

> [!NOTE]
> Este relatório foi gerado automaticamente a partir dos metadados normalizados da VEMA.
> Ele comprova a viabilidade técnica de triagem automática e agrupamento (clustering) de casos semelhantes.
"""

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("=" * 65)
    print("Análise do acervo da VEMA concluída com sucesso!")
    print(f"Relatório gerado em: {OUTPUT_REPORT}")
    print("=" * 65)
    print("\n--- Resumo de destaques ---")
    print(f"Total de processos: {total_processos}")
    print("\nTop 3 classes:")
    for _, r in top_classes.head(3).iterrows():
        print(f"  - {r['Classe processual']}: {r['Qtd processos']} ({r['% do acervo']}%)")
    print("\nTop 3 assuntos:")
    for _, r in top_assuntos.head(3).iterrows():
        print(f"  - {r['Assunto TPU']}: {r['Frequência']} ({r['% de incidência']}%)")
    print("\nTop 3 grupos repetitivos:")
    for _, r in df_repetitivos.head(3).iterrows():
        print(f"  - {r['Classe processual']} + {r['Assunto principal']}: {r['Qtd processos semelhantes']} processos")

if __name__ == "__main__":
    analisar()

