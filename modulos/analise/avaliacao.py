"""
avaliacao.py
------------
Metricas para avaliar o desempenho de uma ESTRATEGIA ao longo do tempo:
retorno acumulado, drawdown maximo e indice de Sharpe.

Por que este arquivo existe
    Em 28/09/2026 a analise de risco de carteiras saiu do projeto: os pesos
    do score 60/40 nao tinham referencia, e o recorte de carteiras nao era o
    objeto do estudo. Tres funcoes foram preservadas porque tem uso
    justificado no proximo passo do trabalho: o backtest da estrategia
    baseada no sentimento (comparar com buy-and-hold exige exatamente estas
    tres medidas).

    O restante (VaR, beta, Markowitz, classificador de perfil) esta no
    historico do git, na tag feicit-2026.

Referencias
    Sharpe, W. F. Mutual Fund Performance. Journal of Business, 1966.
"""

import numpy as np
import pandas as pd
from typing import Dict

# Taxa livre de risco anual usada como referencia (Selic aproximada no
# periodo do estudo). Fica explicita aqui porque muda o Sharpe.
TAXA_LIVRE_RISCO_ANUAL = 0.14


def retorno_acumulado(retornos: pd.Series) -> pd.Series:
    """Curva de capital a partir de retornos diarios (base 1,0)."""
    return (1 + retornos.fillna(0)).cumprod()


def calcular_sharpe(retornos: pd.Series,
                    taxa_livre_risco_anual: float = TAXA_LIVRE_RISCO_ANUAL) -> float:
    """
    Indice Sharpe: retorno ajustado pelo risco, anualizado.
    Sharpe > 1 e considerado bom.
    """
    taxa_diaria = taxa_livre_risco_anual / 252
    excesso = retornos - taxa_diaria
    if excesso.std() == 0:
        return 0.0
    return round((excesso.mean() / excesso.std()) * np.sqrt(252), 3)


def calcular_max_drawdown(precos: pd.Series) -> Dict:
    """Maxima queda do pico ate o vale."""
    pico = precos.cummax()
    drawdown = (precos - pico) / pico
    max_dd = drawdown.min()
    data_pico = precos[:drawdown.idxmin()].idxmax()
    data_vale = drawdown.idxmin()
    return {
        "max_drawdown_pct": round(max_dd * 100, 2),
        "data_pico": str(data_pico)[:10],
        "data_vale": str(data_vale)[:10],
    }
