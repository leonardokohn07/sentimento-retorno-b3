# -*- coding: utf-8 -*-
"""
36_resultado_original_medida.py — R3 da Fase F.

O resultado ORIGINAL do estudo (D-1, D+0 e D+1 por ativo, exatamente como em
scripts/congelar_resultados.py), trocando só a medida de sentimento.
Roda as duas medidas lado a lado, com os mesmos dados de preço.

Uso:  python scripts/36_resultado_original_medida.py
"""
import datetime as dt
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

from modulos.analise.hipotese import montar_serie_diaria, regressao_sentimento_retorno, MIN_OBSERVACOES
from modulos.analise import modelos


def carregar_retornos():
    """Igual ao congelar_resultados.py: log-retorno do fechamento, dropna geral."""
    f = {}
    for arq in sorted((RAIZ / "dados" / "cache_precos").glob("*_1d.csv")):
        d = pd.read_csv(arq, index_col=0, parse_dates=True)
        f[arq.name.replace("_1d.csv", "")] = d["Close"]
    precos = pd.DataFrame(f)
    return np.log(precos / precos.shift(1)).dropna()


def tabela(noticias, retornos):
    linhas = []
    for t in sorted(noticias["ticker"].dropna().unique()):
        if t not in retornos.columns:
            continue
        serie = montar_serie_diaria(noticias, retornos, t)
        if len(serie) < MIN_OBSERVACOES:
            continue
        l = {"ativo": t, "n": len(serie)}
        for lag, rot in ((-1, "D-1"), (0, "D+0"), (1, "D+1")):
            reg = regressao_sentimento_retorno(serie, lag=lag)
            l[f"r {rot}"], l[f"p {rot}"] = reg.get("r", np.nan), reg.get("p_valor", np.nan)
        linhas.append(l)
    return pd.DataFrame(linhas)


base = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv", parse_dates=["data", "data_pregao"])
retornos = carregar_retornos()
saida = ["R3 (Fase F) — resultado original do estudo com cada medida de sentimento",
         f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M}. Mesmo procedimento do congelar_resultados.py.", ""]
tabs = {}
for medida in ("lexico", "finbert"):
    tab = tabela(modelos.aplicar(base, medida), retornos)
    tabs[medida] = tab
    saida.append(f"── medida: {medida} ──")
    saida.append(tab.to_string(index=False, float_format=lambda v: f"{v:+.4f}"))
    for rot in ("D-1", "D+0", "D+1"):
        sig = int((tab[f"p {rot}"] < 0.05).sum())
        saida.append(f"   {rot}: {sig} de {len(tab)} ativos com p < 0,05 | r médio {tab[f'r {rot}'].mean():+.4f}")
    saida.append("")
txt = "\n".join(saida)
print(txt)
hoje = dt.date.today().isoformat()
(RAIZ / "resultados" / f"fase_F_R3_resultado_original_{hoje}.txt").write_text(txt + "\n", encoding="utf-8")
pd.concat({k: v for k, v in tabs.items()}, names=["medida"]).to_csv(
    RAIZ / "resultados" / f"fase_F_R3_resultado_original_{hoje}.csv")
