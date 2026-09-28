# -*- coding: utf-8 -*-
"""
congelar_resultados.py
----------------------
Recalcula o resultado do estudo (D+0 e D+1) a partir de arquivos LOCAIS:
    dados/noticias_com_sentimento.csv   (sentimento ja calculado)
    dados/cache_precos/*.csv            (precos da ultima coleta bem-sucedida)

Serve como REFERENCIA CONGELADA: roda antes de mexer no codigo, roda de novo
depois, e os numeros tem que bater. E o teste de regressao do estudo.

Nao depende de internet nem do yfinance. Nao altera nada do projeto.

Uso, da pasta InvestAI:
    .\\venv\\Scripts\\python scripts\\congelar_resultados.py
"""
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from modulos.analise.hipotese import (montar_serie_diaria,
                                      regressao_sentimento_retorno,
                                      MIN_OBSERVACOES)

ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"
PASTA_RES.mkdir(exist_ok=True)


def carregar_retornos() -> pd.DataFrame:
    """Mesma conta de modulos/coleta/precos.calcular_retornos, lendo do cache:
    retorno logaritmico do fechamento, com dropna geral (linha so entra se
    TODOS os ativos tem preco naquele dia)."""
    fechamentos = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        ticker = arq.name.replace("_1d.csv", "")
        df = pd.read_csv(arq, index_col=0, parse_dates=True)
        fechamentos[ticker] = df["Close"]
    precos = pd.DataFrame(fechamentos)
    return np.log(precos / precos.shift(1)).dropna()


def main():
    noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
    retornos = carregar_retornos()
    tickers = sorted(noticias["ticker"].dropna().unique())

    linhas = []
    for t in tickers:
        if t not in retornos.columns:
            linhas.append(dict(ativo=t, n=0, motivo="sem serie de precos"))
            continue
        serie = montar_serie_diaria(noticias, retornos, t)
        if len(serie) < MIN_OBSERVACOES:
            linhas.append(dict(ativo=t, n=len(serie),
                               motivo=f"menos de {MIN_OBSERVACOES} dias"))
            continue
        linha = dict(ativo=t, n=len(serie), motivo="")
        for lag, rot in ((-1, "dm1"), (0, "d0"), (1, "d1")):
            reg = regressao_sentimento_retorno(serie, lag=lag)
            if "erro" in reg:
                linha[f"{rot}_erro"] = reg["erro"]
                continue
            linha[f"n_{rot}"] = reg["n_observacoes"]
            linha[f"r_{rot}"] = reg["r"]
            linha[f"r2_{rot}"] = reg["r2"]
            linha[f"p_{rot}"] = reg["p_valor"]
            linha[f"sig_{rot}"] = reg["significativo_5pct"]
        linhas.append(linha)

    tab = pd.DataFrame(linhas)
    hoje = date.today().isoformat()
    csv = PASTA_RES / f"congelado_{hoje}.csv"
    tab.to_csv(csv, index=False)

    validos = tab[tab["motivo"] == ""]
    sig0 = int(validos["sig_d0"].sum()) if "sig_d0" in validos else 0
    sig1 = int(validos["sig_d1"].sum()) if "sig_d1" in validos else 0
    p_medio0 = validos.loc[validos["sig_d0"] == True, "p_d0"].mean() if sig0 else float("nan")

    larg = "=" * 96
    txt = [larg, f"  RESULTADO CONGELADO — {hoje}", larg,
           f"  Fonte: dados/noticias_com_sentimento.csv ({len(noticias)} noticias)",
           f"         dados/cache_precos/ ({retornos.shape[1]} ativos, "
           f"{retornos.shape[0]} pregoes apos alinhamento)",
           f"  Minimo de observacoes: {MIN_OBSERVACOES}", larg,
           f"{'ativo':<10}{'n':>6}{'r D-1':>9}{'p D-1':>10}"
           f"{'r D+0':>9}{'p D+0':>10}{'H0 D+0':>9}"
           f"{'r D+1':>9}{'p D+1':>10}{'H0 D+1':>9}",
           "-" * 96]
    for _, l in tab.iterrows():
        if l["motivo"]:
            txt.append(f"{l['ativo']:<10}{int(l['n']):>6}   FORA — {l['motivo']}")
            continue
        txt.append(f"{l['ativo']:<10}{int(l['n']):>6}"
                   f"{l['r_dm1']:>9.4f}{l['p_dm1']:>10.4f}"
                   f"{l['r_d0']:>9.4f}{l['p_d0']:>10.4f}"
                   f"{('rejeita' if l['sig_d0'] else 'nao'):>9}"
                   f"{l['r_d1']:>9.4f}{l['p_d1']:>10.4f}"
                   f"{('rejeita' if l['sig_d1'] else 'nao'):>9}")
    sigm1 = int(validos["sig_dm1"].sum()) if "sig_dm1" in validos else 0
    txt += ["-" * 96,
            f"  D-1 (controle de causalidade reversa): {sigm1} de {len(validos)} "
            f"rejeitam H0",
            f"  D+0: {sig0} de {len(validos)} rejeitam H0"
            + (f" (p medio dos significativos = {p_medio0:.4f})" if sig0 else ""),
            f"  D+1: {sig1} de {len(validos)} rejeitam H0", larg,
            "  Estes numeros sao a REFERENCIA. Depois de qualquer mudanca no codigo,",
            "  rode este script de novo: se algum numero mudar, a mudanca quebrou algo.",
            larg]
    saida = "\n".join(txt)
    (PASTA_RES / f"congelado_{hoje}.txt").write_text(saida, encoding="utf-8")
    print(saida)
    print(f"\nsalvo em: {csv.name} e congelado_{hoje}.txt")


if __name__ == "__main__":
    main()
