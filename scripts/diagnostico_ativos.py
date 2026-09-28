# -*- coding: utf-8 -*-
"""
diagnostico_ativos.py
---------------------
Descobre POR QUE um ativo some da aba 6 (Estudo da Hipotese).

Para cada ativo o script mostra, na ordem em que a aba 6 faz:
    1. dias com noticia no CSV            (lado das noticias)
    2. linhas de preco baixadas do Yahoo  (lado dos precos)
    3. dias que sobram no cruzamento      (so vale o dia que tem os DOIS)
    4. veredito: entra ou nao entra no estudo (minimo 60 dias)

Nao altera nenhum arquivo. Rodar assim, da pasta InvestAI:
    .\\venv\\Scripts\\python scripts\\diagnostico_ativos.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd
import yfinance as yf

from modulos.caminhos import ARQ_NOTICIAS
from modulos.coleta.precos import CARTEIRA_ESTUDO
from modulos.analise.hipotese import montar_serie_diaria, MIN_OBSERVACOES

print("=" * 74)
print("  DIAGNOSTICO DOS ATIVOS DO ESTUDO")
print("=" * 74)
print(f"  yfinance          : {yf.__version__}")
print(f"  arquivo noticias  : {ARQ_NOTICIAS}")

noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
print(f"  noticias no arquivo: {len(noticias)}")

# A aba 6 usa os tickers QUE EXISTEM NO CSV (nao a carteira da barra lateral)
tickers = sorted(noticias["ticker"].dropna().unique())
print(f"  tickers no CSV     : {len(tickers)} -> {', '.join(tickers)}")
print("=" * 74)

precos, falhou = {}, []
for t in tickers:
    try:
        df = yf.Ticker(t).history(period="5y")
        if df.empty:
            falhou.append((t, "resposta vazia (sem serie de precos)"))
            continue
        df.index = pd.to_datetime(df.index).tz_localize(None)
        precos[t] = df["Close"]
    except Exception as e:
        falhou.append((t, f"{type(e).__name__}: {str(e)[:60]}"))

retornos = pd.DataFrame(precos)
import numpy as np
retornos = np.log(retornos / retornos.shift(1))          # SEM dropna geral

print(f"{'ativo':<11}{'dias c/ not.':>13}{'precos':>9}{'cruzados':>10}  veredito")
print("-" * 74)
for t in tickers:
    dias_not = noticias.loc[noticias["ticker"] == t, "data_pregao"].nunique()
    n_prec = int(retornos[t].notna().sum()) if t in retornos.columns else 0
    if t in retornos.columns:
        serie = montar_serie_diaria(noticias, retornos, t)
        n_cruz = len(serie)
    else:
        n_cruz = 0
    if n_prec == 0:
        vered = "FORA - sem preco no Yahoo"
    elif n_cruz < MIN_OBSERVACOES:
        vered = f"FORA - so {n_cruz} dias (minimo {MIN_OBSERVACOES})"
    else:
        vered = "ENTRA no estudo"
    print(f"{t:<11}{dias_not:>13}{n_prec:>9}{n_cruz:>10}  {vered}")

if falhou:
    print("-" * 74)
    print("  FALHAS NO DOWNLOAD:")
    for t, motivo in falhou:
        print(f"    {t}: {motivo}")
print("=" * 74)
