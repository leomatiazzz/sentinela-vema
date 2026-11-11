"""
Demonstração e validação do motor da etapa 3:
1. Agrupamento temático do acervo (clustering K-Means)
2. Busca de similaridade híbrida entre processos reais da VEMA
3. Busca semântica por fatos / petição livre (usando casos ambientais do Ceará)
"""
import sys
import os

# Garante que o diretório raiz está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import obter_estatisticas_gerais
from src.clustering import executar_clustering
from src.similarity import MotorSimilaridade
from src.synthesizer import obter_casos_teste
from src.formatters import formatar_numero, formatar_percentual

def testar_tudo():
    print("=" * 70)
    print("      Sentinela-VEMA: teste do motor de inteligência (etapa 3)")
    print("=" * 70)

    stats = obter_estatisticas_gerais()
    print(f"\n[Base de dados] {formatar_numero(stats['total_processos'])} processos | {formatar_numero(stats['total_movimentos'])} atos | {formatar_numero(stats['total_classes'])} classes | {formatar_numero(stats['total_assuntos'])} assuntos.")

    # 1. Teste de clustering (agrupamento proativo)
    print("\n" + "#" * 70)
    print("1. Teste de clustering: agrupando o acervo em blocos temáticos...")
    print("#" * 70)
    
    df_clustered, clusters_info, vectorizer, kmeans, X = executar_clustering(n_clusters=7)

    for cid, info in sorted(clusters_info.items(), key=lambda x: x[0]):
        print(f"\n[Cluster {cid}] {info['titulo']}")
        print(f"  Volume: {formatar_numero(info['tamanho'])} processos ({formatar_percentual(info['porcentagem'])} do acervo)")
        print(f"  Termos-chave: {', '.join(info['termos_chave'])}")
        print(f"  Processos de exemplo: {', '.join(info['exemplos_processos'][:2])}")

    # 2. Teste de similaridade processo a processo
    print("\n" + "#" * 70)
    print("2. Teste de similaridade entre processos: buscando casos irmãos...")
    print("#" * 70)

    motor = MotorSimilaridade(df_clustered)

    # Escolhe um processo representativo de Ação Civil Pública para o teste
    exemplo_acp = df_clustered[df_clustered["classe_nome"] == "Ação Civil Pública"].iloc[0]
    num_teste = exemplo_acp["numero_processo"]

    print(f"\n>> Processo-alvo consultado: {num_teste}")
    print(f"   Classe: {exemplo_acp['classe_nome']}")
    print(f"   Assunto principal: {exemplo_acp['assunto_principal']}")
    print(f"   Todos os assuntos: {exemplo_acp['assuntos_completos']}")
    print(f"   Ano: {exemplo_acp['ano_ajuizamento']}")

    alvo, similares = motor.buscar_por_processo(num_teste, top_k=3)
    print(f"\n>> Top {len(similares)} processos mais similares no acervo:")
    for rank, sim in enumerate(similares, 1):
        print(f"\n  #{rank} Processo: {sim['numero_processo']} | Relevância geral: {formatar_percentual(sim['score_similaridade'])}")
        print(f"     Classe: {sim['classe_nome']} | Ano: {sim['ano_ajuizamento']}")
        print(f"     Assunto: {sim['assunto_principal']}")
        print(f"     Afinidade textual: {formatar_percentual(sim['score_textual'])} | Estrutural TPU: {formatar_percentual(sim['score_estrutural'])}")
        print(f"     Por que são similares? {'; '.join(sim['explicacoes'])}")

    # 3. Teste de busca semântica por texto livre (fatos / petição)
    print("\n" + "#" * 70)
    print("3. Teste de busca semântica: consulta por fatos/narrativa jurídica...")
    print("#" * 70)

    casos = obter_casos_teste()
    caso_semace = casos[1]
    print(f"\n>> Fatos da consulta: '{caso_semace['titulo']}'")
    print(f"   Trecho fático pesquisado: {caso_semace['resumo_fatos'][:160]}...")

    matches = motor.buscar_por_texto_livre(caso_semace["resumo_fatos"], top_k=3)
    print(f"\n>> Resultados retornados pelo motor para este caso fático:")
    for rank, m in enumerate(matches, 1):
        print(f"\n  #{rank} Processo: {m['numero_processo']} (Aderência: {formatar_percentual(m['score_similaridade'])})")
        print(f"     Classe: {m['classe_nome']} | Assunto: {m['assunto_principal']}")
        print(f"     Assuntos completos: {m['assuntos_completos']}")
        print(f"     Justificativa: {'; '.join(m['explicacoes'])}")

    print("\n" + "=" * 70)
    print("Motor de similaridade e clustering validado com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    testar_tudo()

