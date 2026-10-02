# -*- coding: utf-8 -*-
"""
32_coletar_recentes.py — notícias recentes dos 8 ativos + horário oficial (Fase G).
SÓ COLETA. Nenhum teste é feito aqui.

Pré-registro: docs/pre-registro_2026-10-02_fase-G_minuto.md

1. Notícias: o MESMO coletor do estudo (modulos/coleta/noticias.py), os
   mesmos termos e o mesmo léxico, em janelas de 7 dias (mais resultados por
   consulta). Para notícias recentes o Google informa a hora real.
2. Horário oficial: procura cada manchete nova na API WordPress do site
   (mesmas funções do scripts/24_horarios_wordpress.py).

NUNCA mexe em dados/noticias_com_sentimento.csv (o arquivo do estudo).
Acrescenta ao que já foi coletado, sem apagar:
    dados/prospectivo/noticias_recentes.csv
    dados/prospectivo/horarios_wordpress_recentes.csv

Uso:
    .\\venv\\Scripts\\python scripts\\32_coletar_recentes.py                    (de 04/08/2026 até hoje)
    .\\venv\\Scripts\\python scripts\\32_coletar_recentes.py --dias 3           (só os últimos 3 dias)
"""
import argparse
import concurrent.futures as cf
import importlib.util
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd

from modulos.coleta.noticias import coletar_historico
from modulos.analise.sentimento import AnalisadorV2

ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA", "PETR4.SA",
          "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
PASTA = RAIZ / "dados" / "prospectivo"
ARQ_NOT = PASTA / "noticias_recentes.csv"
ARQ_WP = PASTA / "horarios_wordpress_recentes.csv"
STATUS = RAIZ / "dados" / "execucao" / "status.txt"


def marcar(texto):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"{texto} {datetime.now():%Y-%m-%d %H:%M:%S}\n")


def modulo_wordpress():
    """Carrega as funções do script 24 (o nome começa com número, então não dá
    para usar import normal)."""
    spec = importlib.util.spec_from_file_location(
        "wp24", RAIZ / "scripts" / "24_horarios_wordpress.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def coletar_noticias(inicio, fim):
    df = coletar_historico(ATIVOS, inicio, fim, janela_dias=7, pausa_seg=1.0, verbose=True)
    if df.empty:
        return df
    df = AnalisadorV2(usar_ml=False).analisar_batch(df)
    df["coletado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PASTA.mkdir(parents=True, exist_ok=True)
    antes = 0
    if ARQ_NOT.exists():
        velho = pd.read_csv(ARQ_NOT)
        antes = len(velho)
        df = pd.concat([velho, df], ignore_index=True)
    # Mantém a 1ª vez em que a notícia foi vista (o horário mais próximo do real).
    df = df.drop_duplicates(subset=["ticker", "titulo"], keep="first")
    df.to_csv(ARQ_NOT, index=False, encoding="utf-8")
    print(f"\nNotícias recentes: {antes} -> {len(df)} em {ARQ_NOT.relative_to(RAIZ)}")
    return df


def horarios_wordpress(noticias, limite_min):
    wp = modulo_wordpress()
    wp.LIMITE_MIN = limite_min
    ja = set(pd.read_csv(ARQ_WP)["url"]) if ARQ_WP.exists() else set()
    n = noticias.drop_duplicates("url")
    n = n[n["fonte"].isin(wp.DOMINIOS) & ~n["url"].isin(ja)].copy()
    if n.empty:
        print("WordPress: nada novo para procurar")
        return
    n["dominio"] = n["fonte"].map(wp.DOMINIOS)
    n["titulo_limpo"] = [wp.titulo_limpo(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    n = n[["url", "fonte", "dominio", "titulo_limpo", "data"]]
    with cf.ThreadPoolExecutor(16) as ex:
        sond = list(ex.map(wp.sondar, sorted(n["dominio"].unique())))
    abertos = {d for d, ok, _ in sond if ok}
    alvo = n[n["dominio"].isin(abertos)]
    print(f"WordPress: {len(abertos)} sites com API aberta, {len(alvo)} manchetes a procurar")
    prazo = time.time() + limite_min * 60
    res = []
    with cf.ThreadPoolExecutor(max(1, len(abertos))) as ex:
        futs = {ex.submit(wp.buscar, d, g, prazo): d for d, g in alvo.groupby("dominio")}
        for f in cf.as_completed(futs):
            res.extend(f.result())
    if not res:
        return
    novo = pd.DataFrame(res)
    novo["procurado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ARQ_WP.exists():
        novo = pd.concat([pd.read_csv(ARQ_WP), novo], ignore_index=True)
    novo = novo.drop_duplicates("url", keep="last")
    novo.to_csv(ARQ_WP, index=False, encoding="utf-8")
    print(f"WordPress: {int((novo['status'] == 'ok').sum())} horários no total em {ARQ_WP.relative_to(RAIZ)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", default="2026-08-04")
    ap.add_argument("--dias", type=int, default=None, help="só os últimos N dias")
    ap.add_argument("--limite-wp-min", type=int, default=20)
    a = ap.parse_args()
    fim = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    inicio = ((datetime.now() - timedelta(days=a.dias)).strftime("%Y-%m-%d")
              if a.dias else a.inicio)
    print(f"Coleta de {inicio} até {fim}")
    df = coletar_noticias(inicio, fim)
    if df is not None and len(df):
        horarios_wordpress(df, a.limite_wp_min)


if __name__ == "__main__":
    try:
        main()
    finally:
        marcar("FIM_32")
