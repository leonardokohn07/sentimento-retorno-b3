# -*- coding: utf-8 -*-
"""
13_defasagem_negativa.py
------------------------
CONTROLE DE CAUSALIDADE REVERSA (D-1)

Pergunta: o sentimento das noticias de hoje se relaciona com o retorno de
ONTEM? Se sim, parte da associacao encontrada em D+0 pode ser o jornal
escrevendo sobre um movimento de preco que ja aconteceu.

Pre-registrado em docs/pre-registro_2026-09-28_defasagem-negativa.md, antes
de rodar. Ideia do professor Sauer, na FEICIT 2026.

Alem das correlacoes, o script responde a pergunta que separa os cenarios:
a correlacao em D+0 e MAIOR que a de D-1, de forma estatisticamente
significativa? Como as duas compartilham a mesma variavel (o sentimento) e
a mesma amostra, o teste correto e o de correlacoes dependentes — Williams
(1959), na formulacao de Steiger (1980), e nao dois testes separados.

Tambem reporta a autocorrelacao do retorno: se o retorno de hoje ja se
parece com o de ontem, uma correlacao real em D+0 se propaga sozinha para
D-1, sem que haja qualquer reacao do noticiario.

Rodar (da pasta InvestAI):
    .\\venv\\Scripts\\python scripts\\13_defasagem_negativa.py
"""
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from scipy import stats

from modulos.analise.hipotese import montar_serie_diaria, MIN_OBSERVACOES

ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"
ALFA = 0.05


def carregar_retornos() -> pd.DataFrame:
    fech = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        fech[arq.name.replace("_1d.csv", "")] = pd.read_csv(
            arq, index_col=0, parse_dates=True)["Close"]
    precos = pd.DataFrame(fech)
    return np.log(precos / precos.shift(1)).dropna()


def williams(r12: float, r13: float, r23: float, n: int):
    """Compara duas correlacoes DEPENDENTES que compartilham uma variavel.

        r12 = corr(sentimento, retorno D+0)
        r13 = corr(sentimento, retorno D-1)
        r23 = corr(retorno D+0, retorno D-1)   <- a autocorrelacao

    Devolve (t, p, graus de liberdade). H0: r12 = r13.
    """
    if n < 5:
        return float("nan"), float("nan"), 0
    det = 1 - r12**2 - r13**2 - r23**2 + 2 * r12 * r13 * r23
    media = (r12 + r13) / 2
    denom = 2 * ((n - 1) / (n - 3)) * det + media**2 * (1 - r23) ** 3
    if denom <= 0:
        return float("nan"), float("nan"), n - 3
    t = (r12 - r13) * np.sqrt(((n - 1) * (1 + r23)) / denom)
    p = 2 * (1 - stats.t.cdf(abs(t), df=n - 3))
    return float(t), float(p), n - 3


def main():
    noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
    retornos = carregar_retornos()
    tickers = sorted(noticias["ticker"].dropna().unique())

    linhas = []
    for t in tickers:
        if t not in retornos.columns:
            continue
        serie = montar_serie_diaria(noticias, retornos, t)
        if len(serie) < MIN_OBSERVACOES:
            continue
        s = serie.dropna(subset=["sentimento", "retorno_lag_0", "retorno_lag_-1"])
        sent = s["sentimento"].to_numpy()
        d0 = s["retorno_lag_0"].to_numpy()
        dm1 = s["retorno_lag_-1"].to_numpy()
        n = len(s)

        r_d0, p_d0 = stats.pearsonr(sent, d0)
        r_dm1, p_dm1 = stats.pearsonr(sent, dm1)
        auto, p_auto = stats.pearsonr(d0, dm1)
        t_w, p_w, gl = williams(r_d0, r_dm1, auto, n)

        linhas.append(dict(
            ativo=t.replace(".SA", ""), n=n,
            r_dm1=round(r_dm1, 4), p_dm1=round(p_dm1, 4),
            r_d0=round(r_d0, 4), p_d0=round(p_d0, 4),
            autocorr=round(auto, 4), p_autocorr=round(p_auto, 4),
            williams_t=round(t_w, 3), williams_p=round(p_w, 4),
            d0_maior=bool(p_w < ALFA and r_d0 > r_dm1),
        ))

    tab = pd.DataFrame(linhas)
    hoje = date.today().isoformat()
    tab.to_csv(PASTA_RES / f"defasagem_negativa_{hoje}.csv", index=False)

    L = "=" * 94
    out = [L, "  CONTROLE DE CAUSALIDADE REVERSA — SENTIMENTO DE HOJE x RETORNO DE ONTEM",
           L, f"  Data: {hoje}  ·  alfa = {ALFA}  ·  pre-registro em docs/",
           f"  Amostra: os mesmos {len(tab)} ativos do estudo, sem inclusao nem exclusao", L,
           f"{'ativo':<9}{'n':>6}{'r D-1':>9}{'p D-1':>9}{'r D+0':>9}{'p D+0':>9}"
           f"{'autocor':>10}{'Williams t':>12}{'p':>9}{'D+0 > D-1':>12}",
           "-" * 94]
    for _, l in tab.iterrows():
        out.append(
            f"{l['ativo']:<9}{int(l['n']):>6}{l['r_dm1']:>9.4f}{l['p_dm1']:>9.4f}"
            f"{l['r_d0']:>9.4f}{l['p_d0']:>9.4f}{l['autocorr']:>10.4f}"
            f"{l['williams_t']:>12.3f}{l['williams_p']:>9.4f}"
            f"{('sim' if l['d0_maior'] else 'nao'):>12}")
    sig_dm1 = int((tab["p_dm1"] < ALFA).sum())
    sig_d0 = int((tab["p_d0"] < ALFA).sum())
    maiores = int(tab["d0_maior"].sum())
    out += ["-" * 94,
            f"  D-1 significativo em {sig_dm1} de {len(tab)} ativos",
            f"  D+0 significativo em {sig_d0} de {len(tab)} ativos",
            f"  D+0 estatisticamente MAIOR que D-1 em {maiores} de {len(tab)} ativos "
            f"(teste de Williams)",
            L,
            "  COMO LER",
            "  Uma correlacao em D-1 nao significa, por si so, jornalismo reativo:",
            "  se o retorno de hoje e correlacionado com o de ontem (coluna autocor),",
            "  uma associacao real em D+0 aparece em D-1 por arrasto. Por isso a",
            "  comparacao direta entre as duas usa o teste de Williams, que leva a",
            "  autocorrelacao em conta e trata as duas correlacoes como dependentes.",
            L]
    texto = "\n".join(out)
    (PASTA_RES / f"defasagem_negativa_{hoje}.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
