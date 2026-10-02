# -*- coding: utf-8 -*-
"""
painel.py — teste agrupado (os 8 ativos juntos) com permutação em blocos de data.

Usado pelos testes de direção (scripts 19 a 21) e pelo de fim de semana (17).

Ideia: cada linha é um par (ativo, dia). O sentimento é padronizado dentro do
ativo; o retorno também. A correlação de Pearson é calculada sobre o painel.
O p-valor vem de sortear qual DIA recebe os retornos de qual, levando todos os
ativos juntos — isso preserva o fato de que as ações sobem e caem juntas no
mesmo dia (permutar linha a linha subestimaria o p-valor).

Calibrado em 02/10/2026: com sentimento embaralhado, 4% a 7% de falso
positivo em 100 rodadas (nominal 5%).
"""
import numpy as np
import pandas as pd

N_PERM = 10_000
SEMENTE = 42


def _pearson(x, y):
    x = x - x.mean(); y = y - y.mean()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def teste_agrupado(linhas: pd.DataFrame, R: pd.DataFrame,
                   n_perm: int = N_PERM, semente: int = SEMENTE) -> dict:
    """
    linhas: colunas data, ticker, sentimento (uma linha por ativo-dia)
    R: retornos (índice = data, colunas = tickers), já com a defasagem
       desejada aplicada (ex.: R.shift(1) para o pregão anterior)
    """
    L = linhas.dropna(subset=["sentimento"]).copy()
    L["data"] = pd.to_datetime(L["data"]).dt.normalize()
    L = L[L["ticker"].isin(R.columns)]
    datas_ok = R.index[R.notna().all(axis=1)]
    L = L[L["data"].isin(datas_ok)]
    dp = L.groupby("ticker")["sentimento"].transform("std")
    L = L[dp > 0]
    if len(L) < 10:
        return {"erro": "amostra pequena demais", "n": len(L)}

    datas = np.array(sorted(L["data"].unique()))
    tick = sorted(L["ticker"].unique())
    M = R.loc[datas, tick].to_numpy(dtype=float)
    Mz = (M - M.mean(axis=0)) / M.std(axis=0, ddof=1)
    i_d = np.searchsorted(datas, L["data"].to_numpy())
    i_a = L["ticker"].map({t: k for k, t in enumerate(tick)}).to_numpy()
    x = L.groupby("ticker")["sentimento"].transform(
        lambda v: (v - v.mean()) / v.std(ddof=1)).to_numpy()

    r = _pearson(x, Mz[i_d, i_a])
    rng = np.random.default_rng(semente)
    k = 0
    for _ in range(n_perm):
        perm = rng.permutation(len(datas))
        if abs(_pearson(x, Mz[perm[i_d], i_a])) >= abs(r):
            k += 1
    n = len(x)
    from scipy import stats
    mde = float(np.tanh((stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) / np.sqrt(n - 3)))
    return {"r": r, "p": (k + 1) / (n_perm + 1), "n": n, "n_datas": len(datas), "mde": mde}
