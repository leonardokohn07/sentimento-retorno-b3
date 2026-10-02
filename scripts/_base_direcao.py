# -*- coding: utf-8 -*-
"""Leitura comum aos testes de direção (scripts 19 a 22)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.analise.fuso import ajustar_pregao_brasilia

ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"
ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA",
          "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
SETOR = {"PETR4.SA": "petroleo", "VALE3.SA": "mineracao", "ITUB4.SA": "bancos",
         "BBDC4.SA": "bancos", "WEGE3.SA": "bens de capital", "MGLU3.SA": "varejo",
         "ABEV3.SA": "bebidas", "SUZB3.SA": "papel e celulose"}


def carregar_retornos() -> pd.DataFrame:
    fech = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        fech[arq.name.replace("_1d.csv", "")] = pd.read_csv(
            arq, index_col=0, parse_dates=True)["Close"]
    precos = pd.DataFrame(fech)
    ret = np.log(precos / precos.shift(1)).dropna()
    ret.index = pd.to_datetime(ret.index).normalize()
    return ret


def carregar_noticias(embaralhar: bool = False, semente: int = 0) -> pd.DataFrame:
    n = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
    n = n[n["ticker"].isin(ATIVOS)].copy()
    n = ajustar_pregao_brasilia(n)
    if embaralhar:   # SÓ para testar o código: destrói a relação real
        n["score_polaridade"] = np.random.default_rng(semente).permutation(
            n["score_polaridade"].to_numpy())
    return n


def sentimento_diario(noticias: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Uma linha por dia de pregão com notícia: data, ticker, sentimento, n."""
    q = noticias[noticias["ticker"] == ticker]
    g = q.groupby(q["data_pregao"].dt.normalize())["score_polaridade"].agg(["mean", "size"])
    return pd.DataFrame({"data": g.index, "ticker": ticker,
                         "sentimento": g["mean"].to_numpy(), "n_noticias": g["size"].to_numpy()})


class Saida:
    """Imprime e guarda as linhas para salvar em resultados/."""
    def __init__(self):
        self.linhas = []
    def __call__(self, s=""):
        print(s); self.linhas.append(str(s))
    def salvar(self, nome):
        from datetime import date
        PASTA_RES.mkdir(exist_ok=True)
        arq = PASTA_RES / f"{nome}_{date.today().isoformat()}.txt"
        arq.write_text("\n".join(self.linhas), encoding="utf-8")
        print(f"\nsalvo em: resultados/{arq.name}")
