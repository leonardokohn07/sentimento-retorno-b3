"""
modulos.analise — O que e calculado a partir dos dados coletados.

    sentimento.py         Medida do tom das noticias — motor unico do
                          projeto. Trata negacao e intensificadores e
                          devolve score continuo de -1 a +1.

    hipotese.py           Testes estatisticos do estudo (correlacao com
                          defasagem, teste t, event study, regressao).

    avaliacao.py          Retorno acumulado, drawdown e Sharpe — usados
                          para avaliar estrategias no backtest.

Em 28/09/2026 o modulo risco.py (volatilidade, beta, VaR, Markowitz,
classificador de perfil) saiu do projeto junto com a analise de carteiras.
Esta no historico do git, na tag feicit-2026.
"""

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
    MIN_OBSERVACOES,
)

from .avaliacao import (
    retorno_acumulado,
    calcular_sharpe,
    calcular_max_drawdown,
)

__all__ = [
    # sentimento
    "AnalisadorV2", "analisar_lexico", "normalizar",
    "agregar_sentimento_por_ativo", "gerar_alertas", "LEXICO",
    # hipotese
    "montar_serie_diaria", "montar_serie_completa",
    "testar_correlacao_defasada", "testar_diferenca_medias",
    "calcular_retorno_anormal", "event_study",
    "regressao_sentimento_retorno", "gerar_relatorio", "imprimir_relatorio",
    "MIN_OBSERVACOES",
    # avaliacao
    "retorno_acumulado", "calcular_sharpe", "calcular_max_drawdown",
]
