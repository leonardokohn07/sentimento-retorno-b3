# -*- coding: utf-8 -*-
"""
31_baixar_minuto.py — barras de 1 e de 5 minutos do Yahoo (Fase G). SÓ COLETA.

Pré-registro: docs/pre-registro_2026-10-02_fase-G_minuto.md

O que o Yahoo guarda:
    5 minutos : ~60 dias
    1 minuto  : ~30 dias, em pedidos de até 7 dias
Por isso o arquivo de cada ativo CRESCE a cada execução: as barras novas são
acrescentadas e as antigas nunca são apagadas. Rodando pelo menos uma vez por
semana (o coletor diário faz isso), não se perde nenhum minuto.

Saída: dados/minuto/<ATIVO>_5m.csv e dados/minuto/<ATIVO>_1m.csv
Uso:   .\\venv\\Scripts\\python scripts\\31_baixar_minuto.py
"""
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd

ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA", "PETR4.SA",
          "SUZB3.SA", "VALE3.SA", "WEGE3.SA", "^BVSP"]
PASTA = RAIZ / "dados" / "minuto"
STATUS = RAIZ / "dados" / "execucao" / "status.txt"
FUSO = "America/Sao_Paulo"
COLUNAS = ["Open", "High", "Low", "Close", "Volume"]


def marcar(texto):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"{texto} {datetime.now():%Y-%m-%d %H:%M:%S}\n")


def ler(arq):
    d = pd.read_csv(arq)
    d.index = pd.to_datetime(d["Datetime"], utc=True).dt.tz_convert(FUSO)
    d.index.name = "Datetime"
    return d[COLUNAS]


def acrescentar(ticker, intervalo, novo):
    """Junta as barras novas às já guardadas (sem apagar nada) e grava."""
    if novo is None or novo.empty:
        print(f"  {ticker:<9} {intervalo}: nada novo")
        return
    idx = novo.index
    novo.index = (idx.tz_localize("UTC") if idx.tz is None else idx).tz_convert(FUSO)
    novo.index.name = "Datetime"
    novo = novo[COLUNAS]
    arq = PASTA / f"{ticker.replace('^', '')}_{intervalo}.csv"
    antes = 0
    if arq.exists():
        velho = ler(arq)
        antes = len(velho)
        novo = pd.concat([velho, novo])
    novo = novo[~novo.index.duplicated(keep="last")].sort_index()
    novo.to_csv(arq)
    print(f"  {ticker:<9} {intervalo}: {antes} -> {len(novo)} barras "
          f"({novo.index.min():%Y-%m-%d %H:%M} a {novo.index.max():%Y-%m-%d %H:%M})")


def main():
    import yfinance as yf
    PASTA.mkdir(parents=True, exist_ok=True)
    agora = pd.Timestamp.now(tz=FUSO)
    for t in ATIVOS:
        tk = yf.Ticker(t)
        try:
            acrescentar(t, "5m", tk.history(period="60d", interval="5m",
                                            auto_adjust=False, prepost=False))
        except Exception as e:
            print(f"  {t:<9} 5m ERRO: {type(e).__name__}: {e}")
        partes = []
        fim = agora.normalize() + pd.Timedelta(days=1)
        limite = agora.normalize() - pd.Timedelta(days=29)
        while fim > limite:
            ini = max(fim - pd.Timedelta(days=7), limite)
            try:
                p = tk.history(start=ini.strftime("%Y-%m-%d"), end=fim.strftime("%Y-%m-%d"),
                               interval="1m", auto_adjust=False, prepost=False)
                if not p.empty:
                    partes.append(p)
            except Exception as e:
                print(f"  {t:<9} 1m {ini:%Y-%m-%d}: ERRO {type(e).__name__}: {e}")
            fim = ini
        acrescentar(t, "1m", pd.concat(partes) if partes else None)


if __name__ == "__main__":
    try:
        main()
    finally:
        marcar("FIM_31")
