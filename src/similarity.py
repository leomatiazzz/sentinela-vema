"""
Motor de Similaridade Híbrida para o Acervo da VEMA.
Combina similaridade textual (TF-IDF com n-gramas) e afinidade estruturada da TPU (classes e assuntos).
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.db import carregar_todos_processos, buscar_processo_por_numero
from src.clustering import preparar_corpus

class MotorSimilaridade:
    def __init__(self, df=None):
        if df is None:
            self.df = carregar_todos_processos()
        else:
            self.df = df.copy()

        self.corpus = preparar_corpus(self.df)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.90,
            sublinear_tf=True
        )
        self.matriz_tfidf = self.vectorizer.fit_transform(self.corpus)

    def _calcular_score_estrutural(self, p_alvo, p_candidato):
        """
        Calcula a sobreposição de metadados TPU (Classe, Assuntos e Ano).
        """
        score = 0.0
        explicacoes = []

        # 1. Correspondência de Classe Processual
        if p_alvo.get("classe_codigo") == p_candidato.get("classe_codigo"):
            score += 0.40
            explicacoes.append(f"Mesma classe processual ({p_alvo.get('classe_nome')})")

        # 2. Correspondência de Assunto Principal
        if str(p_alvo.get("assunto_principal")).strip().lower() == str(p_candidato.get("assunto_principal")).strip().lower():
            score += 0.35
            explicacoes.append(f"Mesmo assunto principal ({p_alvo.get('assunto_principal')})")
        else:
            # Overlap de outros assuntos
            assuntos_alvo = set(str(p_alvo.get("assuntos_completos", "")).lower().split(" | "))
            assuntos_cand = set(str(p_candidato.get("assuntos_completos", "")).lower().split(" | "))
            intersec = assuntos_alvo.intersection(assuntos_cand)
            if intersec and "" not in intersec:
                score += 0.20
                explicacoes.append(f"Assuntos TPU compartilhados: {', '.join(intersec)}")

        # 3. Proximidade Temporal (Mesmo ano ou consecutivo)
        ano_a = p_alvo.get("ano_ajuizamento")
        ano_c = p_candidato.get("ano_ajuizamento")
        if ano_a and ano_c and abs(ano_a - ano_c) <= 1:
            score += 0.10
            explicacoes.append(f"Período temporal similar ({ano_c})")

        # 4. Status de Movimentação análogo
        if p_alvo.get("ultimo_movimento_codigo") == p_candidato.get("ultimo_movimento_codigo"):
            score += 0.15
            explicacoes.append(f"Último ato idêntico ({p_candidato.get('ultimo_movimento_nome')})")

        return min(score, 1.0), explicacoes

    def buscar_por_processo(self, numero_processo, top_k=5):
        """
        Dado o número de um processo da VEMA, localiza os top_k processos mais semelhantes do acervo.
        """
        p_alvo = buscar_processo_por_numero(numero_processo)
        if not p_alvo:
            return None, "Processo não encontrado no acervo da VEMA."

        # Identifica o índice do processo no dataframe
        num_alvo = p_alvo["numero_processo"]
        indices = self.df.index[self.df["numero_processo"] == num_alvo].tolist()
        if not indices:
            return None, "Processo não indexado no corpus vetorial."

        idx_alvo = indices[0]
        vetor_alvo = self.matriz_tfidf[idx_alvo]

        # Similaridade de cosseno textual
        sim_textual = cosine_similarity(vetor_alvo, self.matriz_tfidf).flatten()

        resultados = []
        for idx, row in self.df.iterrows():
            if idx == idx_alvo:
                continue  # Não comparar o processo com ele mesmo

            s_text = float(sim_textual[idx])
            s_struct, explicacoes = self._calcular_score_estrutural(p_alvo, row)

            # Score Híbrido Ponderado
            score_final = (0.50 * s_text) + (0.50 * s_struct)

            if score_final > 0.15:  # Filtro mínimo de relevância
                if s_text > 0.4:
                    explicacoes.insert(0, "Forte convergência textual e temática")

                resultados.append({
                    "numero_processo": row["numero_processo"],
                    "classe_nome": row["classe_nome"],
                    "assunto_principal": row["assunto_principal"],
                    "assuntos_completos": row["assuntos_completos"],
                    "ano_ajuizamento": row["ano_ajuizamento"],
                    "total_movimentos": row["total_movimentos"],
                    "ultimo_movimento_nome": row["ultimo_movimento_nome"],
                    "score_similaridade": round(score_final * 100, 1),
                    "score_textual": round(s_text * 100, 1),
                    "score_estrutural": round(s_struct * 100, 1),
                    "explicacoes": explicacoes
                })

        # Ordena pelos maiores scores
        resultados.sort(key=lambda r: r["score_similaridade"], reverse=True)
        return p_alvo, resultados[:top_k]

    def buscar_por_texto_livre(self, texto_consulta, top_k=5, filtro_classe=None):
        """
        Permite ao servidor colar fatos, trechos de petição ou palavras-chave
        e encontrar os processos análogos no acervo da VEMA.
        """
        if not texto_consulta or not texto_consulta.strip():
            return []

        vetor_consulta = self.vectorizer.transform([texto_consulta])
        sim_textual = cosine_similarity(vetor_consulta, self.matriz_tfidf).flatten()

        candidatos = []
        for idx, row in self.df.iterrows():
            if filtro_classe and str(filtro_classe).lower() not in str(row["classe_nome"]).lower():
                continue

            s_text = float(sim_textual[idx])
            if s_text > 0.05:
                # Dedução de afinidade fática
                explicacoes = []
                assunto_princ = str(row.get("assunto_principal", "")).lower()
                if any(termo in texto_consulta.lower() for termo in assunto_princ.split()):
                    explicacoes.append(f"Afinidade temática com: {row.get('assunto_principal')}")
                if s_text > 0.35:
                    explicacoes.append("Alta similaridade terminológica com os fatos informados")

                candidatos.append({
                    "numero_processo": row["numero_processo"],
                    "classe_nome": row["classe_nome"],
                    "assunto_principal": row["assunto_principal"],
                    "assuntos_completos": row["assuntos_completos"],
                    "ano_ajuizamento": row["ano_ajuizamento"],
                    "total_movimentos": row["total_movimentos"],
                    "ultimo_movimento_nome": row["ultimo_movimento_nome"],
                    "score_similaridade": round(s_text * 100, 1),
                    "explicacoes": explicacoes if explicacoes else ["Aderência aos termos da busca"]
                })

        candidatos.sort(key=lambda r: r["score_similaridade"], reverse=True)
        return candidatos[:top_k]

