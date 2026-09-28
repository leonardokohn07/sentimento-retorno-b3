# -*- coding: utf-8 -*-
"""
14_curva_de_defasagem.py
------------------------
CURVA DE DEFASAGEM: de D-5 a D+5

Mede a correlacao entre o sentimento do dia D e o retorno em D+k, para varios
k, e desenha a curva. O FORMATO da curva e o resultado, nao cada ponto isolado.

Pergunta de origem (professor orientador): se a informacao ja estava no preco
quando a noticia saiu, o efeito deve aparecer ANTES da publicacao — e decair
para tras de forma gradual, nao como um pico isolado em D-1.

Pre-registrado em docs/pre-registro_2026-09-28_curva-de-defasagem.md.

Rodar (da pasta InvestAI):
    .\\venv\\Scripts\\python scripts\\14_curva_de_defasagem.py
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
from modulos.visual import SIGNIFICATIVO, INCONCLUSIVO, NEUTRO, TINTA, TINTA2, MUDO, GRADE

LAGS = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 5]
ALFA = 0.05
ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"


def carregar_retornos() -> pd.DataFrame:
    fech = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        fech[arq.name.replace("_1d.csv", "")] = pd.read_csv(
            arq, index_col=0, parse_dates=True)["Close"]
    precos = pd.DataFrame(fech)
    return np.log(precos / precos.shift(1)).dropna()


def serie_com_lags(noticias, retornos, ticker):
    """montar_serie_diaria pre-calcula so alguns lags; aqui montamos todos."""
    s = montar_serie_diaria(noticias, retornos, ticker)
    if s.empty:
        return s
    ret = retornos[ticker].copy()
    ret.index = pd.to_datetime(ret.index).normalize()
    calendario, valores = ret.index, ret.to_numpy()
    pos = calendario.searchsorted(pd.to_datetime(s["data"]))
    for k in LAGS:
        alvo = pos + k
        col = np.full(len(s), np.nan)
        dentro = (alvo >= 0) & (alvo < len(valores))
        col[dentro] = valores[alvo[dentro]]
        s[f"lag{k}"] = col
    return s


def main():
    noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
    retornos = carregar_retornos()

    series, linhas, empilhado = {}, [], []
    for t in sorted(retornos.columns):
        s = serie_com_lags(noticias, retornos, t)
        if s.empty or len(s) < MIN_OBSERVACOES:
            continue
        series[t.replace(".SA", "")] = s
        empilhado.append(s)
        for k in LAGS:
            d = s.dropna(subset=["sentimento", f"lag{k}"])
            r, p = stats.pearsonr(d["sentimento"], d[f"lag{k}"])
            linhas.append(dict(ativo=t.replace(".SA", ""), lag=k, n=len(d),
                               r=round(r, 4), p=round(p, 4), sig=bool(p < ALFA)))

    # agrupado: todos os pares ativo-dia juntos
    todos = pd.concat(empilhado, ignore_index=True)
    for k in LAGS:
        d = todos.dropna(subset=["sentimento", f"lag{k}"])
        r, p = stats.pearsonr(d["sentimento"], d[f"lag{k}"])
        linhas.append(dict(ativo="AGRUPADO", lag=k, n=len(d),
                           r=round(r, 4), p=round(p, 4), sig=bool(p < ALFA)))

    tab = pd.DataFrame(linhas)
    hoje = date.today().isoformat()
    tab.to_csv(PASTA_RES / f"curva_defasagem_{hoje}.csv", index=False)

    # ── relatorio ──
    L = "=" * 86
    out = [L, "  CURVA DE DEFASAGEM — correlacao entre o sentimento do dia D e o retorno em D+k",
           L, f"  Data: {hoje}  ·  alfa = {ALFA}  ·  pre-registro em docs/", L]
    cab = f"{'ativo':<10}" + "".join(f"{('D'+('%+d'%k) if k else 'D+0'):>8}" for k in LAGS)
    out += [cab, "-" * 86]
    for ativo in list(series) + ["AGRUPADO"]:
        sub = tab[tab["ativo"] == ativo].set_index("lag")
        linha = f"{ativo:<10}"
        for k in LAGS:
            marca = "*" if sub.loc[k, "sig"] else " "
            linha += f"{sub.loc[k, 'r']:>7.3f}{marca}"
        out.append(linha)
    out += ["-" * 86, "  * = significativo a 5%", L]
    texto = "\n".join(out)
    (PASTA_RES / f"curva_defasagem_{hoje}.txt").write_text(texto, encoding="utf-8")
    print(texto)

    # ── grafico ──
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), dpi=200,
                                   gridspec_kw={"height_ratios": [1.15, 1]})
    fundo = "#0f1218"
    fig.patch.set_facecolor(fundo)
    for ax in (ax1, ax2):
        ax.set_facecolor(fundo)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        for s_ in ("left", "bottom"):
            ax.spines[s_].set_color(GRADE)
        ax.tick_params(colors=MUDO, labelsize=9)
        ax.grid(axis="y", color=GRADE, lw=0.7)
        ax.set_axisbelow(True)
        ax.axvline(0, color=MUDO, lw=1, ls=(0, (4, 3)))
        ax.axhline(0, color=GRADE, lw=1)

    finais = []
    for ativo in series:
        sub = tab[tab["ativo"] == ativo].sort_values("lag")
        ax1.plot(sub["lag"], sub["r"], lw=1.4, alpha=.55, color=NEUTRO, zorder=2)
        sig = sub[sub["sig"]]
        ax1.scatter(sig["lag"], sig["r"], s=34, color=SIGNIFICATIVO,
                    edgecolor=fundo, lw=1.2, zorder=3)
        finais.append([float(sub[sub["lag"] == 5]["r"].iloc[0]), ativo])

    # afasta os rotulos que se sobrepoem, mantendo a ordem vertical real
    finais.sort(reverse=True)
    minimo = 0.016
    for i in range(1, len(finais)):
        if finais[i - 1][0] - finais[i][0] < minimo:
            finais[i][0] = finais[i - 1][0] - minimo
    for y, ativo in finais:
        ax1.text(5.2, y, ativo, fontsize=8, color=MUDO, va="center")
    ax1.set_title("Por ativo — pontos verdes são significativos a 5%",
                  color=TINTA, fontsize=11, loc="left", pad=12)
    ax1.set_ylabel("correlação r", color=TINTA2, fontsize=9)

    agr = tab[tab["ativo"] == "AGRUPADO"].sort_values("lag")
    cores = [SIGNIFICATIVO if s_ else NEUTRO for s_ in agr["sig"]]
    ax2.bar(agr["lag"], agr["r"], width=0.62, color=cores, zorder=2)
    for _, l in agr.iterrows():
        ax2.text(l["lag"], l["r"] + (0.004 if l["r"] >= 0 else -0.009),
                 f"{l['r']:.3f}".replace(".", ","), ha="center",
                 fontsize=8, color=TINTA2)
    ax2.set_title("Todos os ativos juntos (pares ativo-dia empilhados)",
                  color=TINTA, fontsize=11, loc="left", pad=12)
    ax2.set_ylabel("correlação r", color=TINTA2, fontsize=9)
    ax2.set_xlabel("defasagem, em pregões — negativo = retorno ANTES da notícia",
                   color=MUDO, fontsize=9, labelpad=8)
    for ax in (ax1, ax2):
        ax.set_xlim(-5.6, 6.4)
        ax.set_xticks(LAGS)
        ax.set_xticklabels([("D%+d" % k) if k else "D+0" for k in LAGS])
    fig.tight_layout(pad=1.4)
    fig.savefig(PASTA_RES / f"curva_defasagem_{hoje}.png", facecolor=fundo)
    print(f"\ngrafico: resultados/curva_defasagem_{hoje}.png")


if __name__ == "__main__":
    main()
