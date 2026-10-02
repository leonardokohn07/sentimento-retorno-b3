# -*- coding: utf-8 -*-
"""
41_grafico_perfil_minuto.py — gráfico do perfil minuto a minuto (Fase G, adendo 2).

Retorno anormal ACUMULADO de 15 minutos antes a 15 minutos depois da
publicação, para o terço mais positivo e o terço mais negativo das notícias,
com barras de 1 minuto. O eixo x marca as FRONTEIRAS dos minutos: a linha é
zerada no início do minuto da publicação (faixa cinza = o próprio minuto da
publicação, que fica fora dos testes). Mesmo estilo do scripts/26.

Uso: python scripts/41_grafico_perfil_minuto.py [perfil.csv] [arquivo_dos_testes.json]
"""
import glob
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

FUNDO, FUNDO2, TINTA, TINTA2, MUDO, GRADE = "#0f1218", "#1a2030", "#f3f5f9", "#d6dbe4", "#9ba4b2", "#252c39"
AZUL, AMBAR = "#3987e5", "#c98500"
virg = lambda v, _=None: f"{v:+.3f}".replace(".", ",") if abs(v) > 1e-12 else "0"

arq = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(sorted(glob.glob(
    str(RAIZ / "resultados" / "fase_G_perfil_minuto_a_minuto_lexico_*.csv")))[-1])
arq_testes = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sorted(glob.glob(
    str(RAIZ / "resultados" / "fase_G_janelas_curtas_lexico_*.json")))[-1])
arq_bandas = Path(str(arq).replace("perfil_minuto_a_minuto", "perfil_minuto_bandas"))
p = pd.read_csv(arq)
B = pd.read_csv(arq_bandas) if arq_bandas.exists() else None
T = json.load(open(arq_testes, encoding="utf-8"))

fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor(FUNDO)
ax.set_facecolor(FUNDO)
ax.axvspan(0, 1, color=FUNDO2, zorder=0)
ax.axvspan(1, 6, color=FUNDO2, alpha=0.45, zorder=0)
for g, cor, rot in (("pos", AZUL, "terço mais POSITIVO"), ("neg", AMBAR, "terço mais NEGATIVO")):
    s = p[p["grupo"] == g].set_index("minuto_relativo").sort_index()["retorno_medio_pct"].fillna(0.0)
    fronteiras = list(range(-15, 17))                         # início do minuto -15 ... fim do minuto +15
    nivel = [0.0]
    for m in range(-15, 16):
        nivel.append(nivel[-1] + s.get(m, 0.0))
    nivel = np.array(nivel) - nivel[15]                       # zero no início do minuto da publicação
    if B is not None:                                         # faixa = IC 95% (bootstrap dos eventos)
        b = B[B["grupo"] == g].sort_values("fronteira_min")
        ax.fill_between(b["fronteira_min"], b["ic95_baixo"], b["ic95_alto"], color=cor, alpha=0.13,
                        lw=0, zorder=2)
    ax.plot(fronteiras, nivel, color=cor, lw=2.2, zorder=3)
    ax.plot([fronteiras[-1]], [nivel[-1]], marker="o", ms=8, color=cor, markeredgecolor=FUNDO,
            markeredgewidth=2, zorder=4)
    n = int(p[p["grupo"] == g]["n"].max())
    ax.annotate(f"{rot} (n = {n})", (fronteiras[-1], nivel[-1]), xytext=(10, 0),
                textcoords="offset points", color=TINTA2, fontsize=10, va="center")
ax.axhline(0, color=GRADE, lw=1, zorder=1)
lo, hi = ax.get_ylim()
ax.text(0.5, hi, "minuto da\npublicação", ha="center", va="top", color=MUDO, fontsize=8.5)
ax.text(3.5, hi, "5 min\ndepois", ha="center", va="top", color=MUDO, fontsize=8.5)
ax.text(-7.5, lo, "ANTES da notícia", ha="center", va="bottom", color=MUDO, fontsize=10)
ax.text(11, lo, "DEPOIS da notícia", ha="center", va="bottom", color=MUDO, fontsize=10)
marcas = [-15, -10, -5, 0, 5, 10, 15]
ax.set_xticks(marcas)
ax.set_xticklabels(["−15", "−10", "−5", "0", "+5", "+10", "+15"])
ax.set_xlabel("minutos desde a publicação (faixas claras = IC 95%)", color=TINTA2)
ax.set_xlim(-15.5, 24)
ax.yaxis.set_major_formatter(FuncFormatter(virg))
ax.set_ylabel("retorno anormal acumulado (%)", color=TINTA2)
ax.tick_params(colors=TINTA2)
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.grid(axis="y", color=GRADE, lw=0.8)
ax.set_axisbelow(True)


def rp(k):
    r = T[k]
    return f"r = {r['r']:+.3f}, p = {r['p']:.3f}".replace(".", ",").replace("r = +", "r = ").replace("r = -", "r = −")


fig.text(0.06, 0.95, "Nos minutos em volta da notícia, o preço se move?", color=TINTA, fontsize=15, weight="bold")
fig.text(0.06, 0.905, "Notícias no pregão com horário exato · barras de 1 minuto (20 pregões, set/2026) · "
         "retorno descontado da média das outras ações", color=MUDO, fontsize=9.5)
fig.text(0.06, 0.015, f"Fonte: Os Autores (2026). Perfil descritivo. Testes pré-registrados: 5 min depois "
         f"{rp('C1')}; 5 min antes {rp('C2')}.", color=MUDO, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 0.88))
saida = RAIZ / "resultados" / "perfil_minuto_noticias.png"
plt.savefig(saida, facecolor=FUNDO)
print("salvo em", saida)
