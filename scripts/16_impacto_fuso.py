# -*- coding: utf-8 -*-
"""
16_impacto_fuso.py
------------------
Mede o efeito do bug de fuso horário (ver modulos/analise/fuso.py) sobre o
resultado do estudo. Mesmo procedimento usado no bug de alinhamento:
medir ANTES de corrigir.

Roda D-1, D+0 e D+1 duas vezes, com o MESMO cache de preços:
  - original : data_pregao como está gravada no arquivo
  - corrigido: data_pregao recalculada no horário de Brasília

Não altera o arquivo de notícias nem o resultado congelado.

Uso, da pasta InvestAI:
    .\\venv\\Scripts\\python scripts\\16_impacto_fuso.py
"""
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.analise.hipotese import (montar_serie_diaria,
                                      regressao_sentimento_retorno,
                                      MIN_OBSERVACOES)
from modulos.analise.fuso import ajustar_pregao_brasilia

ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"
ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA",
          "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]


def carregar_retornos() -> pd.DataFrame:
    fech = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        fech[arq.name.replace("_1d.csv", "")] = pd.read_csv(
            arq, index_col=0, parse_dates=True)["Close"]
    precos = pd.DataFrame(fech)
    return np.log(precos / precos.shift(1)).dropna()


def rodar(noticias, retornos):
    out = {}
    for t in ATIVOS:
        s = montar_serie_diaria(noticias, retornos, t)
        if len(s) < MIN_OBSERVACOES:
            continue
        for lag in (-1, 0, 1):
            reg = regressao_sentimento_retorno(s, lag=lag)
            if "erro" not in reg:
                out[(t, lag)] = (reg["n_observacoes"], reg["r"], reg["p_valor"],
                                 reg["significativo_5pct"])
    return out


def main():
    linhas = []
    p = lambda s="": (print(s), linhas.append(s))

    orig = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
    orig = orig[orig["ticker"].isin(ATIVOS)].copy()
    corr = ajustar_pregao_brasilia(orig)

    mudou = orig["data_pregao"].dt.normalize() != corr["data_pregao"]
    p("=" * 78)
    p("  IMPACTO DO BUG DE FUSO HORÁRIO")
    p("=" * 78)
    p(f"  Notícias dos 8 ativos           : {len(orig)}")
    p(f"  Com hora real (não 07h/08h UTC) : {int(corr['hora_real'].sum())}")
    p(f"  Com data_pregao alterada        : {int(mudou.sum())} "
      f"({mudou.mean():.2%} do total)")
    if mudou.any():
        dif = (corr.loc[mudou, "data_pregao"]
               - orig.loc[mudou, "data_pregao"].dt.normalize()).dt.days
        p("  Deslocamento (dias, corrigido - original):")
        for k, v in dif.value_counts().sort_index().items():
            p(f"      {k:+d} dia(s): {v}")

    retornos = carregar_retornos()
    a, b = rodar(orig, retornos), rodar(corr, retornos)

    p("")
    p(f"  {'ativo':<9} {'lag':>4} | {'n':>4} {'r orig':>8} {'p orig':>8} | "
      f"{'n':>4} {'r corr':>8} {'p corr':>8} | muda veredito?")
    p("  " + "-" * 76)
    resumo = {lag: [0, 0] for lag in (-1, 0, 1)}
    for t in ATIVOS:
        for lag in (-1, 0, 1):
            if (t, lag) not in a or (t, lag) not in b:
                continue
            na, ra, pa, sa = a[(t, lag)]
            nb, rb, pb, sb = b[(t, lag)]
            resumo[lag][0] += sa
            resumo[lag][1] += sb
            nome = {-1: "D-1", 0: "D+0", 1: "D+1"}[lag]
            p(f"  {t:<9} {nome:>4} | {na:>4} {ra:>8.4f} {pa:>8.4f} | "
              f"{nb:>4} {rb:>8.4f} {pb:>8.4f} | {'SIM' if sa != sb else 'não'}")
    p("")
    for lag, (sa, sb) in resumo.items():
        nome = {-1: "D-1", 0: "D+0", 1: "D+1"}[lag]
        p(f"  {nome}: original {sa} de 8 rejeitam H0  ->  corrigido {sb} de 8")
    p("=" * 78)

    PASTA_RES.mkdir(exist_ok=True)
    arq = PASTA_RES / f"impacto_fuso_{date.today().isoformat()}.txt"
    arq.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nsalvo em: resultados/{arq.name}")


if __name__ == "__main__":
    main()
