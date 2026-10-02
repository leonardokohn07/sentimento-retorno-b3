# -*- coding: utf-8 -*-
"""
26_grafico_perfil_horario.py — gráfico do estudo de eventos hora a hora.

Retorno anormal ACUMULADO em torno da hora de publicação, para o terço mais
positivo e o terço mais negativo das notícias publicadas no pregão (11h-15h59).
O eixo x marca as FRONTEIRAS das horas: a linha começa no início da hora -3 e
é zerada no início da hora da publicação (faixa cinza = a própria hora da
publicação, que fica fora dos testes).

Uso: .\\venv\\Scripts\\python scripts\\26_grafico_perfil_horario.py [arquivo_perfil.csv]
"""
import glob, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

FUNDO, FUNDO2, TINTA, TINTA2, MUDO, GRADE = "#0f1218", "#1a2030", "#f3f5f9", "#d6dbe4", "#9ba4b2", "#252c39"
AZUL, AMBAR = "#3987e5", "#c98500"
virg = lambda v, _=None: f"{v:+.2f}".replace(".", ",") if v else "0"

arq = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(str(RAIZ / "resultados" / "fase_causal_A1_perfil_horario_*.csv")))[-1]
p = pd.read_csv(arq)
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor(FUNDO); ax.set_facecolor(FUNDO)
ax.axvspan(0, 1, color=FUNDO2, zorder=0)
for g, cor, rot in (("pos", AZUL, "terço mais POSITIVO"), ("neg", AMBAR, "terço mais NEGATIVO")):
    s = p[p["grupo"] == g].set_index("hora_relativa").sort_index()["retorno_medio_pct"].fillna(0.0)
    fronteiras = list(range(-3, 5))                          # início da hora -3 ... fim da hora +3
    nivel = [0.0]
    for h in range(-3, 4):
        nivel.append(nivel[-1] + s.get(h, 0.0))
    nivel = np.array(nivel) - nivel[3]                        # zero no início da hora da publicação
    ax.plot(fronteiras, nivel, color=cor, lw=2.4, marker="o", ms=8, markeredgecolor=FUNDO,
            markeredgewidth=2, zorder=3)
    n = int(p[p["grupo"] == g]["n"].max())
    ax.annotate(f"{rot} (n = {n})", (fronteiras[-1], nivel[-1]), xytext=(10, 0),
                textcoords="offset points", color=TINTA2, fontsize=10, va="center")
ax.axhline(0, color=GRADE, lw=1, zorder=1)
lo, hi = ax.get_ylim()
ax.text(0.5, hi, "hora da\npublicação", ha="center", va="top", color=MUDO, fontsize=9)
ax.text(-1.5, lo, "ANTES da notícia", ha="center", va="bottom", color=MUDO, fontsize=10)
ax.text(2.5, lo, "DEPOIS da notícia", ha="center", va="bottom", color=MUDO, fontsize=10)
ax.set_xticks(range(-3, 5))
ax.set_xticklabels(["−3h", "−2h", "−1h", "início", "fim", "+1h", "+2h", "+3h"])
ax.set_xlim(-3.3, 6.2)
ax.yaxis.set_major_formatter(FuncFormatter(virg))
ax.set_ylabel("retorno anormal acumulado (%)", color=TINTA2)
ax.tick_params(colors=TINTA2)
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.grid(axis="y", color=GRADE, lw=0.8); ax.set_axisbelow(True)
fig.text(0.06, 0.95, "O preço se move antes ou depois da notícia?", color=TINTA, fontsize=15, weight="bold")
fig.text(0.06, 0.905, "Notícias publicadas no pregão com horário exato (Google + API dos sites) · "
         "retorno descontado da média das outras ações", color=MUDO, fontsize=9.5)
fig.text(0.06, 0.015, "Fonte: Os Autores (2026). Perfil descritivo. Testes formais (análise A1): "
         "hora anterior r = 0,091, p = 0,003; hora seguinte r = 0,036, p = 0,23.", color=MUDO, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 0.88))
saida = RAIZ / "resultados" / "perfil_horario_noticias.png"
plt.savefig(saida, facecolor=FUNDO); print("salvo em", saida)
