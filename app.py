"""
Sentinela-VEMA: sistema inteligente de manejo do acervo processual.
I Hackathon TJCE + UFC 2026 — Desafio 3: Vara Estadual do Meio Ambiente.
Interface web interativa e institucional desenvolvida com Streamlit e Plotly.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

from src.db import (
    carregar_todos_processos, 
    buscar_processo_por_numero, 
    obter_estatisticas_gerais
)
from src.clustering import executar_clustering
from src.similarity import MotorSimilaridade
from src.synthesizer import obter_casos_teste, obter_caso_por_id

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sentinela-VEMA | TJCE",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO VISUAL AVANÇADA (CSS INSTITUCIONAL TJCE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Tipografia global */
    html, body, [class*="css"], .stMarkdown, .stText, [data-testid="stAppViewContainer"], 
    .stSelectbox, .stButton, [data-baseweb="tab"], p, div, span, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Preservação de ícones nativos do Streamlit */
    [data-testid="stIconMaterial"], 
    .material-icons, 
    .material-symbols-outlined, 
    .material-symbols-rounded, 
    .material-symbols-sharp {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
    }

    /* Cores de fundo e estrutura */
    [data-testid="stAppViewContainer"] {
        background-color: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Cabeçalho Hero */
    .hero-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 4px 18px rgba(21, 62, 113, 0.05);
        display: flex;
        align-items: center;
        gap: 24px;
        border-left: 5px solid #153e71;
    }
    .hero-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #153e71;
        letter-spacing: -0.5px;
        line-height: 1.15;
        margin-bottom: 4px;
    }
    .hero-sub {
        font-size: 1.0rem;
        color: #475569;
        font-weight: 500;
        line-height: 1.4;
        margin-bottom: 12px;
    }
    .badge-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        display: inline-flex;
        align-items: center;
    }
    .badge-navy {
        background-color: #e9eff7;
        color: #153e71;
        border: 1px solid #c8d9ed;
    }
    .badge-gold {
        background-color: #fef6e9;
        color: #a86c0c;
        border: 1px solid #f9dfb6;
    }
    .badge-green {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
    }

    /* Cards de métricas */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
        box-shadow: 0 3px 12px rgba(21, 62, 113, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(21, 62, 113, 0.08);
    }
    .metric-card.navy { border-top: 4px solid #153e71; }
    .metric-card.gold { border-top: 4px solid #d19730; }
    .metric-card.green { border-top: 4px solid #166534; }
    .metric-card.slate { border-top: 4px solid #475569; }

    .metric-title {
        font-size: 0.78rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* Abas customizadas */
    div[data-testid="stTabs"] {
        margin-top: 8px;
        margin-bottom: 24px;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"],
    div[data-testid="stTabs"] > div:first-child {
        gap: 8px !important;
        border-bottom: 2px solid #e2e8f0 !important;
        background-color: transparent !important;
        padding-bottom: 0px !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 0.96rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-bottom: none !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 18px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: #153e71 !important;
        background-color: #f1f5f9 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: #153e71 !important;
        color: #ffffff !important;
        border-color: #153e71 !important;
        box-shadow: 0 4px 12px rgba(21, 62, 113, 0.15) !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span {
        color: #ffffff !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: #153e71 !important;
    }

    /* Caixas de conteúdo e agrupamentos */
    .content-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .cluster-header {
        border-left: 4px solid #153e71;
        padding-left: 14px;
        margin-bottom: 14px;
    }
    .similarity-badge {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        color: #166534;
        border: 1px solid #86efac;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.88rem;
        display: inline-block;
    }

    /* Botão primário customizado */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #153e71 0%, #0d284d 100%) !important;
        color: #ffffff !important;
        border: 1px solid #153e71 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 12px rgba(21, 62, 113, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4d8c 0%, #153e71 100%) !important;
        box-shadow: 0 6px 16px rgba(21, 62, 113, 0.32) !important;
        transform: translateY(-1px);
    }
    
    /* Tabelas e visualizadores */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CACHE DE DADOS E MOTORES DE INTELIGÊNCIA
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados():
    df = carregar_todos_processos()
    stats = obter_estatisticas_gerais()
    return df, stats

@st.cache_resource
def inicializar_motores():
    df_clustered, clusters_info, vectorizer, kmeans, X = executar_clustering(n_clusters=7)
    motor_sim = MotorSimilaridade(df_clustered)
    return df_clustered, clusters_info, motor_sim

df_processos, stats_gerais = carregar_dados()
df_clustered, clusters_info, motor_sim = inicializar_motores()

# Paleta de cores oficial nos gráficos
TJCE_BLUE = "#153e71"
TJCE_GOLD = "#d19730"
TJCE_GREEN = "#166534"
TJCE_LIGHT_BLUE = "#2563eb"
TJCE_SLATE = "#64748b"

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR INSTITUCIONAL)
# -----------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", use_container_width=True)
    else:
        st.markdown("### ⚖️ **TJCE**")

    st.markdown("""
    <div style="text-align: center; margin-top: -6px; margin-bottom: 14px;">
        <span style="font-size: 0.82rem; font-weight: 700; color: #153e71; letter-spacing: 0.6px;">Gabinete inteligente</span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("**Unidade jurisdicional:**")
    st.markdown("🏛️ **Vara Estadual do Meio Ambiente (VEMA)**")
    st.caption("Comarca de Fortaleza • Cód. órgão: `93861`")
    
    st.markdown("**Fonte oficial dos dados:**")
    st.markdown("📡 **API Pública DataJud / CNJ**")
    st.caption("Metadados estruturados de processos e movimentações públicas do TJCE.")

    st.divider()
    st.markdown("### 📌 Indicadores do acervo")
    st.metric("Processos no acervo", f"{stats_gerais['total_processos']:,}")
    st.metric("Atos processuais", f"{stats_gerais['total_movimentos']:,}")
    st.metric("Classes TPU mapeadas", stats_gerais['total_classes'])
    st.metric("Assuntos materiais TPU", stats_gerais['total_assuntos'])

    st.divider()
    st.markdown("### 🏆 Projeto no hackathon")
    st.markdown("**I Hackathon TJCE + UFC 2026**")
    st.caption("Desafio 3: *Manejo do acervo processual para melhoria da análise de processos*")
    st.caption("Autor: **Léo Matias Araújo**")

# -----------------------------------------------------------------------------
# CABEÇALHO HERO COM IDENTIDADE VISUAL DO TJCE
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-card">
    <div style="display: flex; flex-direction: column; width: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 8px;">
            <div>
                <div style="font-size: 0.8rem; font-weight: 700; color: #d19730; letter-spacing: 0.8px; text-transform: uppercase;">
                    Tribunal de Justiça do Estado do Ceará • Gabinete Ambiental
                </div>
                <div class="hero-title">Sentinela-VEMA</div>
            </div>
            <div class="badge-row">
                <span class="badge badge-navy">Vara Estadual do Meio Ambiente • Cód. 93861</span>
                <span class="badge badge-gold">I Hackathon TJCE + UFC 2026</span>
                <span class="badge badge-green">Base DataJud • CNJ</span>
            </div>
        </div>
        <div class="hero-sub">
            Plataforma institucional de diagnóstico de acervo, triagem proativa de demandas repetitivas e identificação de casos similares para apoio à decisão jurídica.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ABAS DE NAVEGAÇÃO
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Panorama do acervo",
    "🧩 Triagem e julgamento em bloco",
    "🔍 Investigador de similaridade",
    "💡 Diferenciais e arquitetura"
])

# =============================================================================
# ABA 1: PANORAMA DO ACERVO (VISÃO EXECUTIVA)
# =============================================================================
with tab1:
    st.markdown("### Raio-X do acervo judicial da VEMA")
    st.write(
        "Diagnóstico estatístico completo extraído em tempo real diretamente da "
        "Base Nacional de Dados do Poder Judiciário (DataJud/CNJ)."
    )

    # Cards de Destaque com Cores Institucionais
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="metric-card navy">
            <div class="metric-title">Volume total</div>
            <div class="metric-value">1.030</div>
            <div class="metric-sub" style="color: #166534;">100% do acervo indexado</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card gold">
            <div class="metric-title">Média de atos/proc</div>
            <div class="metric-value">89,3</div>
            <div class="metric-sub" style="color: #64748b;">91.994 movimentações</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card slate">
            <div class="metric-title">Crescimento recente</div>
            <div class="metric-value">+164%</div>
            <div class="metric-sub" style="color: #dc2626;">Salto de 2021 para 2026</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="metric-card green">
            <div class="metric-title">Núcleos repetitivos</div>
            <div class="metric-value">7 clusters</div>
            <div class="metric-sub" style="color: #153e71;">Concentram >65% do acervo</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos da Primeira Linha
    col_chart1, col_chart2 = st.columns([6, 4])

    with col_chart1:
        st.markdown("##### 📈 Evolução histórica de ajuizamentos (1994 a 2026)")
        df_anos = (
            df_processos["ano_ajuizamento"]
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
            .reset_index()
        )
        df_anos.columns = ["Ano", "Ajuizamentos"]
        df_anos_recente = df_anos[df_anos["Ano"] >= 2010]
        
        fig_anos = px.bar(
            df_anos_recente, 
            x="Ano", 
            y="Ajuizamentos",
            text="Ajuizamentos",
            color_discrete_sequence=[TJCE_BLUE],
            labels={"Ajuizamentos": "Processos distribuídos", "Ano": "Ano de distribuição"}
        )
        fig_anos.update_traces(
            textposition="outside",
            marker=dict(line=dict(color="#0d284d", width=1))
        )
        fig_anos.update_layout(
            margin=dict(l=20, r=20, t=25, b=60),
            height=340,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#334155")
        )
        fig_anos.update_xaxes(showgrid=False)
        fig_anos.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
        st.plotly_chart(fig_anos, use_container_width=True)
        st.caption("Nota: observa-se aceleração de ajuizamentos a partir de 2024, atingindo 206 novos casos em 2026.")

    with col_chart2:
        st.markdown("##### 🏛️ Perfil de classes judiciais")
        df_classes = (
            df_processos["classe_nome"]
            .value_counts()
            .head(6)
            .reset_index()
        )
        df_classes.columns = ["Classe", "Total"]
        fig_classes = px.pie(
            df_classes, 
            values="Total", 
            names="Classe", 
            hole=0.50,
            color_discrete_sequence=[TJCE_BLUE, TJCE_GOLD, TJCE_GREEN, TJCE_LIGHT_BLUE, "#0d9488", "#94a3b8"]
        )
        fig_classes.update_traces(
            textinfo="percent",
            textposition="inside",
            insidetextorientation="horizontal",
            marker=dict(line=dict(color="#ffffff", width=2))
        )
        fig_classes.update_layout(
            margin=dict(l=10, r=10, t=10, b=60),
            height=340,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#334155"),
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.08, 
                xanchor="center", 
                x=0.5,
                font=dict(size=11)
            )
        )
        st.plotly_chart(fig_classes, use_container_width=True)

    # Gráfico de Assuntos TPU
    st.markdown("##### 🌿 Top 10 assuntos TPU de maior incidência na VEMA")
    df_assuntos_top = (
        df_processos["assunto_principal"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    df_assuntos_top.columns = ["Assunto TPU", "Quantidade"]
    fig_assuntos = px.bar(
        df_assuntos_top,
        x="Quantidade",
        y="Assunto TPU",
        orientation="h",
        text="Quantidade",
        color_discrete_sequence=[TJCE_GREEN]
    )
    fig_assuntos.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=330,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#334155")
    )
    fig_assuntos.update_traces(
        textposition="outside",
        marker=dict(line=dict(color="#0f4422", width=1))
    )
    fig_assuntos.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig_assuntos.update_yaxes(showgrid=False)
    st.plotly_chart(fig_assuntos, use_container_width=True)

    # Explorador Interativo de Dados
    with st.expander("🔎 Explorar tabela completa de processos (com filtros)", expanded=False):
        filtro_classe = st.selectbox("Filtrar por classe:", ["Todas"] + sorted(df_processos["classe_nome"].unique().tolist()))
        df_filtrado = df_processos if filtro_classe == "Todas" else df_processos[df_processos["classe_nome"] == filtro_classe]
        
        st.dataframe(
            df_filtrado[[
                "numero_processo", "classe_nome", "assunto_principal", 
                "ano_ajuizamento", "total_movimentos", "ultimo_movimento_nome"
            ]],
            use_container_width=True,
            height=300
        )

# =============================================================================
# ABA 2: TRIAGEM E JULGAMENTO EM BLOCO (CLUSTERS TEMÁTICOS)
# =============================================================================
with tab2:
    st.markdown("### 🧩 Triagem proativa e julgamento em bloco")
    st.info(
        "💡 **Inovação de negócio:** Diferente das ferramentas tradicionais onde o servidor precisa "
        "adivinhar o que buscar, o **Sentinela-VEMA** varre todo o acervo e agrupa automaticamente "
        "as ações que tratam da mesma matéria fática e jurídica, prontas para análise e despacho em lote."
    )

    lista_clusters_labels = [
        f"Cluster {cid}: {info['titulo']} ({info['tamanho']} processos - {info['porcentagem']}%)"
        for cid, info in sorted(clusters_info.items(), key=lambda x: x[1]["tamanho"], reverse=True)
    ]
    
    escolha_cluster_label = st.selectbox("Selecione um núcleo temático para gerenciamento em bloco:", lista_clusters_labels)
    cid_selecionado = int(escolha_cluster_label.split(":")[0].replace("Cluster", "").strip())
    cluster_dados = clusters_info[cid_selecionado]

    # Painel de Informações do Bloco
    st.markdown(f"""
    <div class="content-card" style="border-left: 5px solid {TJCE_GOLD};">
        <div style="font-size: 1.15rem; font-weight: 700; color: #153e71; margin-bottom: 8px;">
            Núcleo temático selecionado: {cluster_dados['titulo']}
        </div>
        <div style="display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 10px;">
            <div><strong style="color: #64748b; font-size: 0.85rem;">Classe dominante</strong><br><span style="font-weight: 600;">{cluster_dados['classe_dominante']}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem;">Assunto principal</strong><br><span style="font-weight: 600;">{cluster_dados['assunto_dominante']}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem;">Total no lote</strong><br><span style="font-weight: 700; color: #153e71;">{cluster_dados['tamanho']} processos</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem;">Representatividade</strong><br><span style="font-weight: 700; color: #d19730;">{cluster_dados['porcentagem']}% do acervo</span></div>
        </div>
        <div>
            <strong style="color: #64748b; font-size: 0.85rem;">Termos-chave do bloco:</strong>
            <span style="color: #334155; font-size: 0.9rem;"> {', '.join(cluster_dados['termos_chave'])}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Lista de Processos do Cluster
    processos_no_cluster = df_clustered[df_clustered["cluster_id"] == cid_selecionado]
    
    st.markdown(f"##### 📋 Processos agrupados no bloco ({len(processos_no_cluster)} registros)")
    st.dataframe(
        processos_no_cluster[[
            "numero_processo", "classe_nome", "assunto_principal", 
            "ano_ajuizamento", "total_movimentos", "ultimo_movimento_nome"
        ]],
        use_container_width=True,
        height=260
    )

    # Ação de Gabinete: Minuta em Bloco
    st.markdown("##### ⚡ Ação produtiva de gabinete:")
    c_btn1, c_btn2 = st.columns([4, 8])
    with c_btn1:
        if st.button("📄 Gerar minuta de despacho padronizado em lote", type="primary", use_container_width=True):
            st.session_state["minuta_gerada"] = True
            
    if st.session_state.get("minuta_gerada", False):
        st.success(f"Minuta padronizada gerada para os {cluster_dados['tamanho']} processos do cluster {cid_selecionado}!")
        st.markdown(f"""
        ```text
        PODER JUDICIÁRIO DO ESTADO DO CEARÁ
        COMARCA DE FORTALEZA - VARA ESTADUAL DO MEIO AMBIENTE (VEMA)
        
        PROCESSO-PARADIGMA / LOTE: CLUSTER {cid_selecionado} ({cluster_dados['titulo']})
        MATÉRIA: {cluster_dados['assunto_dominante']}
        
        DESPACHO-TIPO EM BLOCO:
        
        Vistos etc.
        Compulsando os autos do presente lote de demandas que versam especificamente sobre 
        '{cluster_dados['assunto_dominante']}', verifica-se a identidade da causa de pedir e a regularidade 
        formal dos atos processuais.
        
        1. Intime-se o órgão ambiental competente (SEMACE/Município) para juntada dos relatórios de 
           fiscalização atualizados no prazo de 15 (quinze) dias.
        2. Após, dê-se vista ao Ministério Público Estadual para manifestação conclusiva.
        
        Fortaleza/CE, data da assinatura digital.
        Magistrado(a) de Direito da Vara Estadual do Meio Ambiente
        ```
        """)

# =============================================================================
# ABA 3: INVESTIGADOR DE SIMILARIDADE (CASO A CASO)
# =============================================================================
with tab3:
    st.markdown("### 🔍 Motor de similaridade híbrida e pesquisa inteligente")
    st.write(
        "Consulte um processo do acervo ou insira o texto de um novo caso fático para localizar "
        "precedentes e processos análogos da VEMA com cálculo de pontuação explicável."
    )

    modo_busca = st.radio(
        "Modo de análise:",
        ["📌 Consultar por processo existente da VEMA", "📝 Analisar nova demanda / fatos livres (simulação realista)"],
        horizontal=True
    )

    st.markdown("---")

    # MODO A: POR PROCESSO DO ACERVO
    if modo_busca == "📌 Consultar por processo existente da VEMA":
        col_input1, col_input2 = st.columns([8, 4])
        with col_input1:
            sugestoes_cnj = [
                "30018129220268060512",
                "30008480220268060512",
                "01672733720158060001",
                "02001727420238060303",
                "30215051420248060001"
            ]
            numero_busca = st.selectbox(
                "Selecione um processo do acervo (ou digite abaixo):",
                sugestoes_cnj,
                help="Selecione um número de exemplo ou utilize a busca personalizada."
            )
            numero_digitado = st.text_input("Ou digite qualquer outro número CNJ da VEMA:", "")
            if numero_digitado.strip():
                numero_busca = numero_digitado.strip()

        with col_input2:
            st.markdown("<br>", unsafe_allow_html=True)
            top_k_slider = st.slider("Quantidade de processos similares:", 2, 8, 4)

        if st.button("🔎 Buscar processos similares", type="primary"):
            alvo, similares = motor_sim.buscar_por_processo(numero_busca, top_k=top_k_slider)

            if not alvo:
                st.error("Processo não localizado no banco da VEMA. Verifique a digitação.")
            else:
                st.markdown("#### 🎯 Processo consultado (alvo da análise):")
                st.markdown(f"""
                <div class="content-card" style="border-left: 5px solid {TJCE_BLUE};">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #153e71;">
                        Processo nº {alvo['numero_processo']}
                    </div>
                    <div style="display: flex; gap: 24px; flex-wrap: wrap; margin-top: 8px;">
                        <div><strong style="color: #64748b; font-size: 0.85rem;">Classe:</strong> {alvo['classe_nome']}</div>
                        <div><strong style="color: #64748b; font-size: 0.85rem;">Assunto:</strong> {alvo['assunto_principal']}</div>
                        <div><strong style="color: #64748b; font-size: 0.85rem;">Ano:</strong> {alvo['ano_ajuizamento']}</div>
                        <div><strong style="color: #64748b; font-size: 0.85rem;">Total de atos:</strong> {alvo['total_movimentos']}</div>
                        <div><strong style="color: #64748b; font-size: 0.85rem;">Último ato:</strong> {alvo['ultimo_movimento_nome']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"#### 🔗 Processos irmãos identificados ({len(similares)} encontrados):")

                if not similares:
                    st.warning("Nenhum processo atingiu o limiar de similaridade.")
                else:
                    for idx, sim in enumerate(similares, 1):
                        score = sim["score_similaridade"]
                        with st.container():
                            st.markdown(f"""
                            <div class="content-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <div style="font-size: 1.1rem; font-weight: 700; color: #153e71;">
                                        #{idx} Processo nº {sim['numero_processo']}
                                    </div>
                                    <span class="similarity-badge">Afinidade: {score}%</span>
                                </div>
                                <div style="font-size: 0.95rem; color: #334155; margin-bottom: 6px;">
                                    <strong>Classe:</strong> {sim['classe_nome']} &nbsp;|&nbsp; 
                                    <strong>Ano:</strong> {sim['ano_ajuizamento']} &nbsp;|&nbsp; 
                                    <strong>Assunto:</strong> {sim['assunto_principal']}
                                </div>
                                <div style="font-size: 0.88rem; color: #64748b; margin-bottom: 8px;">
                                    <strong>Última movimentação:</strong> {sim['ultimo_movimento_nome']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            c_det1, c_det2 = st.columns([7, 5])
                            with c_det1:
                                st.caption(f"**Todos os assuntos:** {sim['assuntos_completos']}")
                            with c_det2:
                                st.markdown("**Por que este processo foi recomendado?**")
                                for exp in sim["explicacoes"]:
                                    st.markdown(f"✓ {exp}")
                                st.progress(int(score))
                                st.caption(f"Decomposição: Textual {sim['score_textual']}% | Estrutural {sim['score_estrutural']}%")

                            with st.expander(f"Ver movimentações históricas do processo {sim['numero_processo']}"):
                                proc_completo = buscar_processo_por_numero(sim["numero_processo"])
                                if proc_completo and proc_completo.get("lista_movimentos"):
                                    df_m = pd.DataFrame(proc_completo["lista_movimentos"])
                                    st.dataframe(df_m.head(10), use_container_width=True)
                                else:
                                    st.write("Sem movimentações detalhadas registradas.")

                            st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px dashed #e2e8f0;'>", unsafe_allow_html=True)

    # MODO B: POR FATOS / CASO SINTÉTICO REALISTA
    else:
        st.markdown("##### 🧪 Teste com cenários fáticos típicos do Ceará")
        casos_teste = obter_casos_teste()
        titulos_casos = [f"{c['id']}: {c['titulo']}" for c in casos_teste]
        
        caso_escolhido_id = st.selectbox(
            "Selecione um caso simulado de alta relevância ambiental no Ceará:",
            ["[Personalizado - digitar fatos manualmente]"] + titulos_casos
        )

        texto_busca = ""
        if caso_escolhido_id != "[Personalizado - digitar fatos manualmente]":
            id_real = caso_escolhido_id.split(":")[0]
            obj_caso = obter_caso_por_id(id_real)
            texto_busca = obj_caso["resumo_fatos"]
            st.caption(f"Classe sugerida: `{obj_caso['classe_sugerida']}` | Assunto: `{obj_caso['assunto_sugerido']}`")
        
        texto_input = st.text_area(
            "Narrativa fática / resumo da petição a ser confrontada com o acervo:", 
            value=texto_busca,
            height=140
        )

        if st.button("🔎 Buscar precedentes semelhantes na VEMA", type="primary"):
            if not texto_input.strip():
                st.warning("Por favor, informe um texto para consulta.")
            else:
                resultados_texto = motor_sim.buscar_por_texto_livre(texto_input, top_k=5)
                st.markdown(f"#### 🔗 Processos mais aderentes aos fatos ({len(resultados_texto)} encontrados):")
                
                if not resultados_texto:
                    st.warning("Nenhum processo no acervo atingiu relevância suficiente com este texto.")
                else:
                    for idx, res in enumerate(resultados_texto, 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="content-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <div style="font-size: 1.05rem; font-weight: 700; color: #153e71;">
                                        #{idx} Processo nº {res['numero_processo']}
                                    </div>
                                    <span class="similarity-badge">Aderência: {res['score_similaridade']}%</span>
                                </div>
                                <div style="font-size: 0.95rem; color: #334155; margin-bottom: 4px;">
                                    <strong>Classe:</strong> {res['classe_nome']} &nbsp;|&nbsp; 
                                    <strong>Ano:</strong> {res['ano_ajuizamento']} &nbsp;|&nbsp; 
                                    <strong>Assunto principal:</strong> {res['assunto_principal']}
                                </div>
                                <div style="font-size: 0.85rem; color: #64748b;">
                                    <strong>Assuntos completos:</strong> {res['assuntos_completos']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c_t1, c_t2 = st.columns([6, 6])
                            with c_t2:
                                st.markdown("**Justificativa:**")
                                for exp in res["explicacoes"]:
                                    st.markdown(f"✓ {exp}")
                            st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px dashed #e2e8f0;'>", unsafe_allow_html=True)

# =============================================================================
# ABA 4: DIFERENCIAIS E ARQUITETURA
# =============================================================================
with tab4:
    st.markdown("### 💡 Diferenciais estratégicos e arquitetura técnica")

    st.markdown("#### 1. Como o Sentinela-VEMA se diferencia do 'Gestão de Acervo' do TJCE?")
    st.write(
        "O TJCE já disponibiliza a ferramenta institucional 'Gestão de Acervo' no seu Hub Digital. "
        "A tabela abaixo demonstra a proposta de valor complementar do **Sentinela-VEMA** voltada à matéria ambiental:"
    )

    tabela_diferencial = pd.DataFrame([
        {
            "Critério": "Modo de atuação",
            "Gestão de Acervo institucional (TJCE)": "Reativo (o usuário precisa pesquisar termos)",
            "Sentinela-VEMA": "Proativo (agrupa o acervo inteiro em clusters sem depender de busca prévia)"
        },
        {
            "Critério": "Especialização jurídica",
            "Gestão de Acervo institucional (TJCE)": "Genérico para todas as varas do tribunal",
            "Sentinela-VEMA": "Especializado na taxonomia ambiental da VEMA (flora, fauna, poluição, APP, multas)"
        },
        {
            "Critério": "Similaridade híbrida",
            "Gestão de Acervo institucional (TJCE)": "Busca semântica em texto do PJe",
            "Sentinela-VEMA": "Combina similaridade textual TF-IDF/embeddings com afinidade estrutural de classes e assuntos TPU"
        },
        {
            "Critério": "Suporte a decisão em bloco",
            "Gestão de Acervo institucional (TJCE)": "Focado em visualização unitária de documentos",
            "Sentinela-VEMA": "Gera minutas de despacho e triagem para lotes inteiros de processos conexos"
        },
        {
            "Critério": "Infraestrutura e custo",
            "Gestão de Acervo institucional (TJCE)": "Requer infraestrutura interna restrita e login no PJe",
            "Sentinela-VEMA": "Executa 100% local ou em nuvem com SQLite e consumo direto da API Pública DataJud"
        }
    ])
    st.dataframe(tabela_diferencial, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 2. Arquitetura da solução")
    
    if os.path.exists("assets/arquitetura.png"):
        st.image(
            "assets/arquitetura.png", 
            caption="Diagrama de arquitetura técnica da solução Sentinela-VEMA", 
            use_container_width=True
        )
    else:
        st.info("Imagem da arquitetura não encontrada em assets/arquitetura.png.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 3. Conformidade com a LGPD e a Resolução CNJ nº 332/2020")
    st.markdown("""
    * **Auditabilidade e supervisão humana:** O sistema atua como apoio à análise. Toda recomendação de similaridade possui justificativa explícita e o servidor é quem valida as minutas.
    * **Privacidade por design (LGPD):** A alimentação pública utiliza metadados autorizados do DataJud, sem exposição indevida de dados pessoais sensíveis ou processos em segredo de justiça.
    * **Independência operacional:** Totalmente reproduzível com tecnologias abertas em Python, sem aprisionamento a fornecedores externos de nuvem paga.
    """)
