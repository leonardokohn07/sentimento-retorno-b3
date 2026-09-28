"""
modulos.coleta — De onde vêm os dados brutos.

    precos.py    Preços e retornos das ações da B3, via yfinance
    noticias.py  Notícias históricas, via Google News RSS

Atalho de importação:
    from modulos.coleta import baixar_dados, coletar_historico
"""

from .precos import (
    baixar_dados,
    calcular_retornos,
    baixar_ibovespa,
    montar_portfolio,
    info_ativo,
    CARTEIRA_PADRAO,
    IBOVESPA,
)

from .noticias import (
    coletar_historico,
    coletar_recentes,
    ajustar_data_pregao,
    TERMOS_BUSCA,
)

__all__ = [
    "baixar_dados", "calcular_retornos", "baixar_ibovespa",
    "montar_portfolio", "info_ativo", "CARTEIRA_PADRAO", "IBOVESPA",
    "coletar_historico", "coletar_recentes", "ajustar_data_pregao",
    "TERMOS_BUSCA",
]
