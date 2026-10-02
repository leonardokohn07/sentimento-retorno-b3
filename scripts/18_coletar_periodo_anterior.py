# -*- coding: utf-8 -*-
"""
18_coletar_periodo_anterior.py
------------------------------
Amplia o período de notícias para TRÁS: outubro/2021 a dezembro/2023.
Mesmo coletor, mesmos termos de busca e mesmo léxico do estudo.

Salva num ARQUIVO SEPARADO (dados/noticias_2021_2023.csv). O arquivo
original do estudo não é tocado, então o resultado publicado e o
congelado continuam reproduzíveis.

Por que outubro/2021: é onde começa o cache de preços.

Uso, da pasta InvestAI:
    .\\venv\\Scripts\\python scripts\\18_coletar_periodo_anterior.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

from modulos.coleta.noticias import coletar_historico, ajustar_data_pregao
from modulos.analise.sentimento import AnalisadorV2

INICIO, FIM = "2021-10-01", "2024-01-01"     # FIM exclusivo: o estudo começa em 01/01/2024
ATIVOS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
          "WEGE3.SA", "MGLU3.SA", "ABEV3.SA", "SUZB3.SA"]
SAIDA = RAIZ / "dados" / "noticias_2021_2023.csv"
ORIGINAL = RAIZ / "dados" / "noticias_com_sentimento.csv"


def main():
    if SAIDA.exists() and "--refazer" not in sys.argv:
        print(f"[JA EXISTE] {SAIDA.name} — use --refazer para coletar de novo")
        df = pd.read_csv(SAIDA, parse_dates=["data", "data_pregao"])
    else:
        df = coletar_historico(ATIVOS, INICIO, FIM, janela_dias=30, pausa_seg=1.0)
        if df.empty:
            print("[ERRO] nada coletado"); sys.exit(1)
        df = ajustar_data_pregao(df)
        df = AnalisadorV2(usar_ml=False).analisar_batch(df)
        df.to_csv(SAIDA, index=False)
        print(f"\n[OK] salvo em dados/{SAIDA.name}")

    orig = pd.read_csv(ORIGINAL, parse_dates=["data"])
    junto = pd.concat([df.assign(_f="novo"), orig.assign(_f="original")])
    junto = junto[junto["ticker"].isin(ATIVOS)]
    junto["ano"] = pd.to_datetime(junto["data"]).dt.year
    print("\nNotícias por ano (densidade — o arquivo antigo do Google pode ser mais esparso):")
    print(junto.pivot_table(index="ticker", columns="ano", values="titulo",
                            aggfunc="count", fill_value=0).to_string())
    fds = pd.to_datetime(df["data"]).dt.weekday >= 5
    print(f"\nNovas notícias: {len(df)}  |  de fim de semana: {int(fds.sum())}")


if __name__ == "__main__":
    main()
