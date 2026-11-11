"""
Módulo de formatação numérica e textual no padrão brasileiro (pt-BR).
Centraliza a lógica de apresentação de milhares, decimais e percentuais.
"""

def formatar_numero(valor) -> str:
    """
    Formata números inteiros ou decimais no padrão brasileiro (pt-BR):
    - Separador de milhares: ponto (.)
    - Separador decimal: vírgula (,)
    - Preserva números inteiros sem acrescentar casas decimais (.0)

    Exemplos:
        formatar_numero(1030)   -> '1.030'
        formatar_numero(91994)  -> '91.994'
        formatar_numero(265)    -> '265'
        formatar_numero(1000)   -> '1.000'
        formatar_numero(89.3)   -> '89,3'
    """
    if valor is None or valor == "":
        return ""
    try:
        # Se for string numérica
        if isinstance(valor, str):
            v_str = valor.strip().replace(" ", "")
            if not v_str:
                return ""
            if "." in v_str or "," in v_str:
                valor = float(v_str.replace(",", "."))
            else:
                valor = int(v_str)

        # Se for inteiro ou float com valor inteiro exato
        if isinstance(valor, int) or (isinstance(valor, float) and valor.is_integer()):
            return f"{int(valor):,}".replace(",", ".")

        # Se for float com casas decimais
        s = f"{valor:.4f}".rstrip("0").rstrip(".")
        if "." in s:
            inteira, decimal = s.split(".")
            inteira_fmt = f"{int(inteira):,}".replace(",", ".")
            return f"{inteira_fmt},{decimal}"
        else:
            return f"{int(s):,}".replace(",", ".")
    except Exception:
        return str(valor)


def formatar_percentual(valor, incluir_simbolo: bool = True) -> str:
    """
    Formata percentuais no padrão brasileiro (pt-BR):
    - Utiliza vírgula (,) como separador decimal;
    - Preserva números inteiros sem acrescentar casas decimais desnecessárias (.0);
    - Elimina zeros à direita desnecessários na parte decimal;
    - Não arredonda artificialmente os dados.

    Exemplos:
        formatar_percentual(25.7)   -> '25,7%'
        formatar_percentual(25.75)  -> '25,75%'
        formatar_percentual(27.0)   -> '27%'
        formatar_percentual(17)     -> '17%'
        formatar_percentual(100.0)  -> '100%'
    """
    if valor is None or valor == "":
        return ""
    try:
        if isinstance(valor, str):
            v_limpo = valor.strip().replace("%", "").replace(" ", "").replace(",", ".")
            v = float(v_limpo)
        else:
            v = float(valor)

        # Se for número inteiro exato (ex: 27.0, 17.0, 100.0)
        if v.is_integer():
            res = str(int(v))
        else:
            # Preserva a precisão original até 4 casas sem zeros excedentes
            s = f"{v:.4f}".rstrip("0").rstrip(".")
            res = s.replace(".", ",")

        return f"{res}%" if incluir_simbolo else res
    except Exception:
        return f"{valor}%" if incluir_simbolo and not str(valor).endswith("%") else str(valor)

