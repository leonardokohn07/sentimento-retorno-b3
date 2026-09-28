"""
modulos.analise — O que é calculado a partir dos dados coletados.

    risco.py              Métricas quantitativas de risco
                          (volatilidade, beta, VaR, Sharpe, drawdown, Markowitz)

    sentimento.py         Análise de sentimento das notícias — motor ÚNICO
                          do projeto, usado tanto pela tela quanto pelo
                          estudo da hipótese. Trata negação, intensificadores
                          e devolve score contínuo de -1 a +1. Também agrega
                          por ativo e gera os alertas.

                          A versão 1 do analisador saiu do projeto em
                          18/09/2026. O que ela fazia de diferente está
                          documentado no cabeçalho de sentimento.py.

    hipotese.py           Testes estatísticos que validam a hipótese central
                          (correlação, teste t, event study, regressão).

Atalho de importação:
    from modulos.analise import calcular_metricas_carteira, AnalisadorV2
"""

from .risco import (
    calcular_volatilidade,
    calcular_beta,
    calcular_var,
    calcular_sharpe,
    calcular_max_drawdown,
    calcular_metricas_carteira,
    calcular_metricas_individuais,
    otimizar_carteira,
    extrair_features_risco,
    classificar_risco,
)

from .sentimento import (
    AnalisadorV2,
    analisar_lexico,
    normalizar,
    agregar_sentimento_por_ativo,
    gerar_alertas,
    LEXICO,
)

from .hipotese import (
    montar_serie_diaria,
    montar_serie_completa,
    testar_correlacao_defasada,
    testar_diferenca_medias,
    calcular_retorno_anormal,
    event_study,
    regressao_sentimento_retorno,
    gerar_relatorio,
    imprimir_relatorio,
)

__all__ = [
    # risco
    "calcular_volatilidade", "calcular_beta", "calcular_var",
    "calcular_sharpe", "calcular_max_drawdown",
    "calcular_metricas_carteira", "calcular_metricas_individuais",
    "otimizar_carteira", "extrair_features_risco", "classificar_risco",
    # sentimento
    "AnalisadorV2", "analisar_lexico", "normalizar",
    "agregar_sentimento_por_ativo", "gerar_alertas", "LEXICO",
    # hipótese
    "montar_serie_diaria", "montar_serie_completa",
    "testar_correlacao_defasada", "testar_diferenca_medias",
    "calcular_retorno_anormal", "event_study",
    "regressao_sentimento_retorno", "gerar_relatorio", "imprimir_relatorio",
]
