"""
Motor de Agrupamento Proativo (Clustering) do Acervo da VEMA.
Agrupa os 1.030 processos em blocos temáticos coerentes para análise conjunta e julgamento em bloco.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from src.db import carregar_todos_processos

def preparar_corpus(df):
    """
    Cria uma representação textual enriquecida combinando classe, assuntos e movimentos.
    """
    corpus = []
    for _, row in df.iterrows():
        classe = str(row.get("classe_nome", "")).strip()
        assunto_princ = str(row.get("assunto_principal", "")).strip()
        assuntos = str(row.get("assuntos_completos", "")).replace("|", " ").strip()
        ult_mov = str(row.get("ultimo_movimento_nome", "")).strip()
        
        # Ponderação textual: o assunto principal e a classe são repetidos para ganho de peso semântico
        texto = f"{classe} {classe} {assunto_princ} {assunto_princ} {assuntos} {ult_mov}"
        corpus.append(texto)
    return corpus

def executar_clustering(n_clusters=7, random_state=42):
    """
    Executa agrupamento K-Means sobre os processos da VEMA.
    Retorna o DataFrame enriquecido com cluster_id e um dicionário com o perfil dos clusters.
    """
    df = carregar_todos_processos()
    corpus = preparar_corpus(df)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        sublinear_tf=True
    )
    X = vectorizer.fit_transform(corpus)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    df["cluster_id"] = labels

    # Mapeamento e titulação inteligente dos clusters
    feature_names = np.array(vectorizer.get_feature_names_out())
    clusters_info = {}

    for i in range(n_clusters):
        subset = df[df["cluster_id"] == i]
        tam = len(subset)
        pct = (tam / len(df) * 100)
        
        # Palavras-chave dominantes do centróide
        top_indices = kmeans.cluster_centers_[i].argsort()[::-1][:6]
        top_terms = [feature_names[idx] for idx in top_indices]
        
        # Classe e Assunto mais comuns no cluster
        top_classe = subset["classe_nome"].mode().iloc[0] if not subset.empty else "N/A"
        top_assunto = subset["assunto_principal"].mode().iloc[0] if not subset.empty else "N/A"
        
        # Título descritivo profissional para o cluster
        titulo = f"{top_classe} — {top_assunto}"
        
        clusters_info[i] = {
            "cluster_id": i,
            "titulo": titulo,
            "tamanho": tam,
            "porcentagem": round(pct, 1),
            "classe_dominante": top_classe,
            "assunto_dominante": top_assunto,
            "termos_chave": top_terms,
            "exemplos_processos": subset["numero_processo"].head(3).tolist()
        }

    # Atribui o título amigável diretamente na coluna do DataFrame
    df["cluster_nome"] = df["cluster_id"].map(lambda cid: clusters_info[cid]["titulo"])

    return df, clusters_info, vectorizer, kmeans, X

