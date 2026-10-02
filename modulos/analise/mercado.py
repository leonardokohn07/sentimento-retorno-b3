# -*- coding: utf-8 -*-
"""
mercado.py — Ibovespa e retorno anormal.

O Ibovespa fica em dados/mercado/, FORA de dados/cache_precos/, porque os
scripts do estudo leem todos os CSVs do cache de preços: se o índice entrasse
lá, mudaria o alinhamento de datas e, com isso, o resultado congelado.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from modulos.analise.hipotese import calcular_retorno_anormal

RAIZ = Path(__file__).resolve().parent.parent.parent
ARQ_IBOV = RAIZ / "dados" / "mercado" / "BVSP_1d.csv"
INICIO_NOTICIAS = "2024-01-02"
JANELA_ESTIMACAO = 250   # pregões antes da primeira notícia


def carregar_ibovespa(baixar_se_faltar: bool = True) -> pd.Series:
    """Retorno logarítmico diário do Ibovespa (^BVSP)."""
    if not ARQ_IBOV.exists():
        if not baixar_se_faltar:
            raise FileNotFoundError(ARQ_IBOV)
        import yfinance as yf
        df = yf.download("^BVSP", start="2021-09-01", progress=False, auto_adjust=True)
        if df is None or df.empty:
            raise RuntimeError("não consegui baixar o ^BVSP do Yahoo")
        fech = df["Close"]
        if isinstance(fech, pd.DataFrame):
            fech = fech.iloc[:, 0]
        ARQ_IBOV.parent.mkdir(parents=True, exist_ok=True)
        fech.rename("Close").to_frame().to_csv(ARQ_IBOV)
    fech = pd.read_csv(ARQ_IBOV, index_col=0, parse_dates=True)["Close"]
    fech.index = pd.to_datetime(fech.index).normalize()
    return np.log(fech / fech.shift(1)).dropna().rename("IBOV")


def matriz_retorno_anormal(R: pd.DataFrame, mercado: pd.Series,
                           inicio: str = INICIO_NOTICIAS,
                           janela: int = JANELA_ESTIMACAO):
    """
    Retorno anormal de cada ativo pelo modelo de mercado, com alfa e beta
    estimados nos `janela` pregões ANTERIORES a `inicio` (antes de qualquer
    notícia da amostra). Devolve (AR, tabela de alfa/beta).
    """
    comum = R.index.intersection(mercado.index)
    R, m = R.loc[comum], mercado.loc[comum]
    pos = int(np.searchsorted(R.index, pd.Timestamp(inicio)))
    if pos < janela:
        raise ValueError(f"só há {pos} pregões antes de {inicio}; precisa de {janela}")
    AR = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
    params = []
    for t in R.columns:
        df = calcular_retorno_anormal(R[t].iloc[pos - janela:], m.iloc[pos - janela:],
                                      janela_estimacao=janela)
        AR.loc[df.index, t] = df["retorno_anormal"]
        params.append({"ativo": t, "alfa": df.attrs["alfa"], "beta": df.attrs["beta"],
                       "r2_modelo": df.attrs["r2_modelo"]})
    return AR, pd.DataFrame(params)
