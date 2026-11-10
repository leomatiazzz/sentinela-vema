"""
Gerador de casos-teste sintéticos hiper-realistas (contexto ambiental do Ceará).
Permite testar e demonstrar a busca fática e semântica de processos mesmo sem os PDFs da VEMA.
"""

CASOS_TESTE = [
    {
        "id": "CASO_01_APP_SABIAGUABA",
        "titulo": "Loteamento clandestino em APP de dunas na Sabiaguaba",
        "classe_sugerida": "Ação Civil Pública",
        "assunto_sugerido": "Área de Preservação Permanente",
        "resumo_fatos": (
            "Ação civil pública ambiental com pedido de liminar decorrente de ocupação irregular "
            "e loteamento clandestino em Área de Preservação Permanente (APP) de restinga e dunas móveis "
            "na região da Sabiaguaba em Fortaleza/CE. Constatou-se desmatamento, movimentação de terra com "
            "remoção de vegetação nativa fixadora de dunas e comercialização de lotes sem licenciamento ambiental "
            "ou autorização da Semace/Município. Pedido de embargo imediato das obras, demolição das estruturas "
            "ergueram-se e condenação em indenização por dano ambiental material e moral coletivo."
        ),
        "termos_chave": ["dunas", "sabiaguaba", "área de preservação permanente", "loteamento clandestino", "demolição", "semace"]
    },
    {
        "id": "CASO_02_MULTA_SEMACE_CAATINGA",
        "titulo": "Anulação de multa da SEMACE por supressão de caatinga",
        "classe_sugerida": "Procedimento Comum Cível",
        "assunto_sugerido": "Revogação/Anulação de multa ambiental",
        "resumo_fatos": (
            "Ação anulatória de débito com pedido de tutela provisória de urgência em face da SEMACE "
            "(Superintendência Estadual do Meio Ambiente). O autor foi autuado em R$ 120.000,00 por suposta "
            "supressão não autorizada de vegetação nativa do bioma Caatinga para pastagem. Alega cerceamento "
            "de defesa no processo administrativo sancionador, ausência de motivação do valor da penalidade e "
            "prescrição intercorrente da pretensão punitiva com base na Lei Estadual do Ceará."
        ),
        "termos_chave": ["semace", "multa ambiental", "anulação", "caatinga", "supressão vegetal", "auto de infração"]
    },
    {
        "id": "CASO_03_POLUICAO_RIO_COCO",
        "titulo": "Crime de poluição e efluentes químicos no Rio Cocó",
        "classe_sugerida": "Inquérito Policial",
        "assunto_sugerido": "Poluição",
        "resumo_fatos": (
            "Inquérito policial instaurado pela Delegacia de Proteção ao Meio Ambiente (DPMA) para apurar a "
            "prática do crime previsto no art. 54 da Lei nº 9.605/98 (crime de poluição qualificada). "
            "Empresa do ramo têxtil e lavanderia industrial estaria despejando efluentes líquidos contaminados "
            "com substâncias químicas diretamente em afluente do Rio Cocó, gerando forte odor, mortandade "
            "de peixes e risco à saúde dos moradores ribeirinhos circunvizinhos."
        ),
        "termos_chave": ["poluição", "rio cocó", "efluentes", "crime ambiental", "dpma", "art 54", "mortandade"]
    },
    {
        "id": "CASO_04_FAUNA_SILVESTRE",
        "titulo": "Comércio ilegal e guarda de aves silvestres ameaçadas",
        "classe_sugerida": "Ação Penal - Procedimento Ordinário",
        "assunto_sugerido": "Crimes contra a Fauna",
        "resumo_fatos": (
            "Ação penal pública incondicionada denunciando réu reincidente pela guarda e comércio irregular "
            "de espécimes da fauna silvestre brasileira nativa da Caatinga (art. 29, § 1º, III, da Lei nº 9.605/98). "
            "Foram apreendidos mais de 40 pássaros em cativeiro sem anilhas de identificação nem autorização do "
            "IBAMA/Semace, configurando crime ambiental e indícios de maus-tratos em virtude das condições precárias das gaiolas."
        ),
        "termos_chave": ["fauna", "aves silvestres", "pássaros", "tráfico", "cativeiro", "ibama", "maus-tratos"]
    },
    {
        "id": "CASO_05_LICENCA_OBRA_POLUIDORA",
        "titulo": "Embargo de empreendimento por falta de licença de instalação",
        "classe_sugerida": "Ação Civil Pública",
        "assunto_sugerido": "Revogação/Concessão de Licença Ambiental",
        "resumo_fatos": (
            "Demanda ajuizada visando ao embargo de obra de posto de abastecimento de combustíveis e lavajato "
            "localizado próximo a recursos hídricos subterrâneos. Aponta-se irregularidade na concessão da "
            "licença prévia por órgão municipal sem anuência do órgão ambiental estadual e sem apresentação de "
            "Estudo de Impacto de Vizinhança e plano de contenção de vazamentos de hidrocarbonetos."
        ),
        "termos_chave": ["licença ambiental", "posto de combustível", "embargo", "recursos hídricos", "obra poluidora"]
    }
]

def obter_casos_teste():
    """Retorna a lista de casos sintéticos representativos da VEMA."""
    return CASOS_TESTE

def obter_caso_por_id(caso_id):
    """Localiza um caso sintético pelo identificador."""
    for c in CASOS_TESTE:
        if c["id"] == caso_id:
            return c
    return None

