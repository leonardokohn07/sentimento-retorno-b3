# -*- coding: utf-8 -*-
"""
23_baixar_intradiario.py — SÓ COLETA (nenhum teste).

Baixa do Yahoo:
  - barras de 60 minutos dos 8 ativos e do Ibovespa (o Yahoo guarda ~730 dias)
  - Ibovespa diário com abertura (para o teste de abertura)

Salva em dados/intradiario/ e dados/mercado/ — fora do cache de preços do
estudo, para não alterar o resultado congelado.

Uso:  .\\venv\\Scripts\\python scripts\\23_baixar_intradiario.py
"""
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
import yfinance as yf

ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA", "PETR4.SA",
          "SUZB3.SA", "VALE3.SA", "WEGE3.SA", "^BVSP"]
PASTA = RAIZ / "dados" / "intradiario"
PASTA.mkdir(parents=True, exist_ok=True)


def achatar(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


for t in ATIVOS:
    try:
        df = achatar(yf.download(t, interval="60m", period="730d", progress=False,
                                 auto_adjust=False, prepost=False))
        if df.empty:
            print(f"{t:<9} VAZIO"); continue
        idx = df.index
        if idx.tz is None:
            idx = idx.tz_localize("UTC")
        df.index = idx.tz_convert("America/Sao_Paulo")
        df.index.name = "Datetime"
        nome = t.replace("^", "") + "_60m.csv"
        df[["Open", "High", "Low", "Close", "Volume"]].to_csv(PASTA / nome)
        horas = pd.Series(df.index.hour).value_counts().sort_index()
        print(f"{t:<9} {len(df):>6} barras  {df.index.min():%Y-%m-%d %H:%M} a {df.index.max():%Y-%m-%d %H:%M}"
              f"  horas: {dict(horas)}")
    except Exception as e:
        print(f"{t:<9} ERRO: {e}")

d = achatar(yf.download("^BVSP", start="2021-09-01", interval="1d", progress=False, auto_adjust=False))
d.index = pd.to_datetime(d.index).tz_localize(None) if getattr(d.index, "tz", None) else pd.to_datetime(d.index)
(RAIZ / "dados" / "mercado").mkdir(parents=True, exist_ok=True)
d[["Open", "High", "Low", "Close", "Volume"]].to_csv(RAIZ / "dados" / "mercado" / "BVSP_1d_ohlc.csv")
print(f"^BVSP diário com abertura: {len(d)} pregões, {d.index.min():%Y-%m-%d} a {d.index.max():%Y-%m-%d}")
