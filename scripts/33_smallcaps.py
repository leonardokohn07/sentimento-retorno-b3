# -*- coding: utf-8 -*-
"""
33_smallcaps.py — Fase H: seleção e coleta das ações de menor liquidez.
SÓ COLETA. Nenhum teste é feito aqui.

Pré-registro: docs/pre-registro_2026-10-02_fase-H_small-caps.md

Regra de seleção (fixada antes de rodar):
    1. carteira do Índice Small Cap (SMLL) da B3 no dia da coleta (guardada como veio)
    2. tira os ativos do estudo e os que têm termos próprios no coletor
    3. sondagem: manchetes no Google News pelo código, de 01/06/2026 a 31/08/2026
    4. elegíveis: pelo menos 30 manchetes únicas
    5. sorteio de 8 elegíveis (ordem alfabética, numpy default_rng(42))

Depois coleta, só das sorteadas:
    notícias de 01/01/2024 a 06/09/2026 (mesmo coletor, termo = código, léxico)
    preços diários (desde 01/06/2023) e barras de 60 min (~730 dias)

Saídas em dados/smallcaps/ (nada do estudo principal é tocado).
Uso:  .\\venv\\Scripts\\python scripts\\33_smallcaps.py
"""
import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

from modulos.coleta.noticias import coletar_historico
from modulos.analise.sentimento import AnalisadorV2
from modulos.analise.validacao_lexico import tirar_fonte

PASTA = RAIZ / "dados" / "smallcaps"
STATUS = RAIZ / "dados" / "execucao" / "status.txt"
EXCLUIR = {"ABEV3", "BBAS3", "BBDC4", "ELET3", "ITUB4", "MGLU3", "PETR4",
           "RENT3", "SUZB3", "VALE3", "WEGE3"}
SONDA_INI, SONDA_FIM, MINIMO, N_SORTEIO, SEMENTE = "2026-06-01", "2026-08-31", 30, 8, 42
COLETA_INI, COLETA_FIM = "2024-01-01", "2026-09-07"     # fim exclusivo = até 06/09/2026
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def marcar(texto):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"{texto} {datetime.now():%Y-%m-%d %H:%M:%S}\n")


# ───────────────────────── 1. carteira do SMLL ─────────────────────────
def carteira_smll():
    """Baixa a carteira do SMLL da API pública do site da B3. Guarda a resposta bruta."""
    import requests
    tentativas = []
    for metodo in ("GetPortfolioDay", "GetTheoricalPortfolio"):
        for segmento in ("1", "2"):
            params = {"language": "pt-br", "pageNumber": 1, "pageSize": 200,
                      "index": "SMLL", "segment": segmento}
            for sep in ((",", ":"), (", ", ": ")):
                b64 = base64.b64encode(json.dumps(params, separators=sep).encode()).decode()
                tentativas.append((metodo, segmento,
                                   f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/{metodo}/{b64}"))
    for metodo, segmento, url in tentativas:
        for cliente in ("requests", "curl_cffi"):
            try:
                if cliente == "requests":
                    r = requests.get(url, headers=UA, timeout=30)
                else:
                    from curl_cffi import requests as creq
                    r = creq.get(url, impersonate="chrome", timeout=30)
                if r.status_code != 200 or '"results"' not in r.text:
                    print(f"  B3 {metodo} seg={segmento} ({cliente}): HTTP {r.status_code}")
                    continue
                dados = r.json()
                res = pd.DataFrame(dados.get("results", []))
                if res.empty:
                    continue
                hoje = datetime.now().strftime("%Y-%m-%d")
                (PASTA / f"carteira_SMLL_bruta_{hoje}.json").write_text(r.text, encoding="utf-8")
                print(f"  B3 {metodo} seg={segmento} ({cliente}): {len(res)} linhas. Colunas: {list(res.columns)}")
                return res
            except Exception as e:
                print(f"  B3 {metodo} seg={segmento} ({cliente}): {type(e).__name__}: {e}")
    return None


def codigos(res):
    """Acha a coluna com os códigos de negociação (ex.: ALOS3, TAEE11)."""
    padrao = re.compile(r"^[A-Z]{4}\d{1,2}$")
    melhor, n_melhor = None, 0
    for c in res.columns:
        n = res[c].astype(str).str.strip().str.match(padrao).sum()
        if n > n_melhor:
            melhor, n_melhor = c, n
    if melhor is None:
        return []
    return sorted({x.strip() for x in res[melhor].astype(str) if padrao.match(x.strip())})


# ───────────────────────── 2-5. sondagem e sorteio ─────────────────────────
def sondar(candidatos):
    linhas = []
    for i, cod in enumerate(candidatos, 1):
        d = coletar_historico([f"{cod}.SA"], SONDA_INI, SONDA_FIM, janela_dias=31,
                              pausa_seg=1.0, verbose=False)
        n = len({tirar_fonte(t, f) for t, f in zip(d["titulo"], d["fonte"])}) if len(d) else 0
        linhas.append({"codigo": cod, "manchetes_sondagem": n})
        print(f"  [{i}/{len(candidatos)}] {cod}: {n} manchetes", flush=True)
    return pd.DataFrame(linhas)


def sortear(sonda):
    eleg = sorted(sonda.loc[sonda["manchetes_sondagem"] >= MINIMO, "codigo"])
    if len(eleg) <= N_SORTEIO:
        escolhidos = eleg
    else:
        idx = np.random.default_rng(SEMENTE).choice(len(eleg), size=N_SORTEIO, replace=False)
        escolhidos = sorted(eleg[i] for i in idx)
    sonda["elegivel"] = sonda["codigo"].isin(eleg)
    sonda["sorteado"] = sonda["codigo"].isin(escolhidos)
    return escolhidos


# ───────────────────────── coleta das sorteadas ─────────────────────────
def coletar(escolhidos):
    tickers = [f"{c}.SA" for c in escolhidos]
    df = coletar_historico(tickers, COLETA_INI, COLETA_FIM, janela_dias=30, pausa_seg=1.0, verbose=True)
    if len(df):
        df = AnalisadorV2(usar_ml=False).analisar_batch(df)
        df.to_csv(PASTA / "noticias_smallcaps.csv", index=False, encoding="utf-8")
        print(f"Notícias: {len(df)} -> dados/smallcaps/noticias_smallcaps.csv")

    import yfinance as yf
    (PASTA / "precos").mkdir(exist_ok=True)
    (PASTA / "intradiario").mkdir(exist_ok=True)
    for t in tickers:
        tk = yf.Ticker(t)
        try:
            d = tk.history(start="2023-06-01", end="2026-10-02", interval="1d", auto_adjust=False)
            d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
            d.index.name = "Date"
            d[["Open", "High", "Low", "Close", "Volume"]].to_csv(PASTA / "precos" / f"{t}_1d.csv")
            print(f"  {t}: {len(d)} pregões diários")
        except Exception as e:
            print(f"  {t} diário: ERRO {type(e).__name__}: {e}")
        try:
            h = tk.history(period="730d", interval="60m", auto_adjust=False, prepost=False)
            idx = h.index
            h.index = (idx.tz_localize("UTC") if idx.tz is None else idx).tz_convert("America/Sao_Paulo")
            h.index.name = "Datetime"
            h[["Open", "High", "Low", "Close", "Volume"]].to_csv(PASTA / "intradiario" / f"{t}_60m.csv")
            print(f"  {t}: {len(h)} barras de 60 min")
        except Exception as e:
            print(f"  {t} 60m: ERRO {type(e).__name__}: {e}")


def main():
    PASTA.mkdir(parents=True, exist_ok=True)
    print("1) Carteira do SMLL na B3")
    res = carteira_smll()
    if res is None:
        print("A B3 não respondeu. Pelo pré-registro, a fase NÃO é feita com lista improvisada.")
        return
    todos = codigos(res)
    candidatos = [c for c in todos if c not in EXCLUIR]
    print(f"   {len(todos)} ativos na carteira; {len(candidatos)} candidatos depois das exclusões")

    print(f"2) Sondagem de cobertura ({SONDA_INI} a {SONDA_FIM})")
    sonda = sondar(candidatos)
    escolhidos = sortear(sonda)
    sonda.to_csv(PASTA / "selecao_smallcaps.csv", index=False, encoding="utf-8")
    print(f"   elegíveis (>= {MINIMO}): {int(sonda['elegivel'].sum())}")
    print(f"   SORTEADOS (semente {SEMENTE}): {escolhidos}")
    if not escolhidos:
        print("Nenhum elegível. Fase H não segue.")
        return

    print("3) Coleta das sorteadas")
    coletar(escolhidos)


if __name__ == "__main__":
    try:
        main()
    finally:
        marcar("FIM_33")
