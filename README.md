# ⚖️ Sentinela-VEMA

> **Sistema inteligente de triagem, agrupamento proativo e manejo do acervo processual**  
> *I Hackathon TJCE + UFC 2026 — Desafio 3: Manejo do acervo processual para melhoria da análise de processos*  
> **Unidade-alvo:** Vara Estadual do Meio Ambiente (VEMA) — Tribunal de Justiça do Estado do Ceará (TJCE)  
> **Desenvolvedor:** Léo Matias Araújo

---

## 📌 1. Visão geral do projeto

O **Sentinela-VEMA** é uma plataforma analítica desenvolvida para solucionar o gargalo do acervo crescente da Vara Estadual do Meio Ambiente do TJCE. Consumindo dados 100% reais diretamente da **API Pública do DataJud (CNJ)**, o sistema diagnostica a litigância, identifica famílias de processos irmãos via **agrupamento não supervisionado (clustering)** e disponibiliza um **motor de similaridade híbrida** para análise e julgamento em bloco.

### 🎯 O problema resolvido:
* **Explosão da demanda:** Os ajuizamentos na VEMA saltaram de 78 ações em 2021 para **206 ações em 2026 (+164% em 3 anos)**.
* **Ciclo processual denso:** O acervo acumula mais de **91.990 atos processuais**, com média de **89,3 movimentações por processo**.
* **Retrabalho cognitivo:** Mais de **65% do acervo** está concentrado em apenas 7 núcleos repetitivos (ex.: ações civis públicas de dano ambiental, inquéritos de poluição, crimes contra a fauna e ações anulatórias de multas da SEMACE).

---

## 🚀 2. Principais funcionalidades

1. **📊 Panorama executivo do acervo:**
   * Painel interativo com evolução histórica de ajuizamentos, repartição cível/penal e ranking de assuntos da Tabela Processual Unificada (TPU/CNJ).
2. **🧩 Triagem e julgamento em bloco (clustering K-Means):**
   * Agrupamento automático dos 1.030 processos da VEMA em 7 blocos homogêneos, permitindo despacho unificado em lote e eliminação de retrabalho de gabinete.
3. **🔍 Motor de similaridade híbrida explicável:**
   * Combina similaridade textual (TF-IDF com unigramas/bigramas) e afinidade estrutural de metadados TPU (classes e assuntos).
   * Suporta busca por número de processo do acervo ou por texto livre de novos fatos/petições.
   * Gera justificativas textuais explícitas (*"Por que estes casos são similares?"*).
4. **📄 Gerador de minutas padronizadas:**
   * Sugestão imediata de despacho padrão de saneamento e diligência para os lotes agrupados.

---

## 💡 3. Diferenciais frente ao "Gestão de Acervo" do TJCE

| Critério | Gestão de Acervo institucional (TJCE) | Sentinela-VEMA |
| :--- | :--- | :--- |
| **Abordagem** | Reativa (espera o usuário formular uma busca) | **Proativa** (agrupa automaticamente o acervo em blocos homogêneos) |
| **Especialização** | Genérico para todas as varas do tribunal | **Especializado na taxonomia ambiental da VEMA** |
| **Critério de similaridade** | Busca semântica puramente textual | **Similaridade híbrida:** Metadados TPU (classes/assuntos) + semântica fática |
| **Fluxo de trabalho** | Consulta pontual de processos | **Triagem e minutas em bloco para lotes inteiros** |
| **Infraestrutura** | Restrito a redes internas e acessos específicos | **Leve, independente, local em SQLite** e 100% alimentado pelo DataJud |

---

## 🛠️ 4. Arquitetura tecnológica

* **Linguagem:** Python 3.12
* **Coleta e ingestão:** `requests` com paginação estável `search_after` via API Pública do DataJud TJCE
* **Banco de dados local:** SQLite relacional com índices estruturados (`vema.db`)
* **Processamento e análise:** `pandas`
* **Inteligência e agrupamento:** `scikit-learn` (TF-IDF, Cosine Similarity, K-Means Clustering)
* **Visualização e cockpit:** `streamlit` e `plotly`

---

## 💻 5. Como executar o projeto localmente

### Pré-requisitos:
* Python 3.12 instalado
* Git

### Passo a passo no terminal:

```powershell
# 1. Clone o repositório ou acesse a pasta do projeto
cd C:\Users\Leo\tjce-hackathon

# 2. Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# (Opcional se já estiver instalado)
pip install -r requirements.txt

# 3. Executar os scripts do pipeline de dados (se desejar inspecionar):
python scripts/testar_api.py
python scripts/analisar_acervo.py
python scripts/testar_similaridade_clustering.py

# 4. Iniciar a interface web do Sentinela-VEMA:
streamlit run app.py
```

Abra o navegador no endereço: **http://localhost:8501**

---

## ⚖️ 6. Conformidade e ética (LGPD e Resolução CNJ nº 332/2020)

* **Supervisão humana:** O sistema apoia a análise do servidor e do magistrado, sem automação de decisões de mérito.
* **Transparência e explicabilidade:** Toda recomendação exibe as razões de similitude (indicadores de classe, assunto e termos convergentes).
* **Privacidade:** Utiliza exclusivamente metadados públicos disponibilizados pelo CNJ, respeitando o sigilo processual e as diretrizes da LGPD.
