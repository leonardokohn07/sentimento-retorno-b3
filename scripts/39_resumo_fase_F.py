# -*- coding: utf-8 -*-
"""
39_resumo_fase_F.py — tabela lado a lado léxico x FinBERT (robustez R1, R2, R3)
e uma análise EXPLORATÓRIA (decidida depois de ver R1-R3, não confirmatória).

Lê os resultados já gerados no mesmo dia:
    resultados/fase_causal_<data>.json            (léxico, R1)
    resultados/fase_causal_finbert_<data>.json    (FinBERT, R1)
    resultados/fase_causal_A1_<data>.json         (léxico, R2)
    resultados/fase_causal_A1_finbert_<data>.json (FinBERT, R2)
    resultados/fase_F_R3_resultado_original_<data>.csv

Exploratório E-F1/E-F2: por que as correlações caem com o FinBERT?
Hipótese: o léxico pega muito as manchetes que RELATAM o preço ("Vale dispara 5%"),
que por construção andam junto com o retorno. Compara o D+0 (2024-2026, retorno
anormal) separando manchetes de relato e informativas.

Uso:  python scripts/39_resumo_fase_F.py --data 2026-10-02
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

from modulos.analise.causal import ATIVOS, retornos_decompostos, teste_parcial
from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise import modelos

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()
R = RAIZ / "resultados"
ler = lambda nome: json.load(open(R / nome, encoding="utf-8"))

saida = []
def p(t=""):
    print(t)
    saida.append(str(t))

def f(v, c=4):
    return f"{v:+.{c}f}".replace(".", ",")

p("FASE F — ROBUSTEZ: a mesma análise com o léxico e com o FinBERT-PT-BR")
p("(mesmo computador, mesmos dados de preço, mesmos métodos e permutações)\n")
lx, fb = ler(f"fase_causal_{a.data}.json"), ler(f"fase_causal_finbert_{a.data}.json")
p("R1 — família principal (Holm sobre P1 a P9)")
p(f"  {'teste':6s} {'r léxico':>10s} {'p Holm':>8s}   {'r FinBERT':>10s} {'p Holm':>8s}")
for k in [f"P{i}" for i in range(1, 10)]:
    a1, b1 = lx["principal"].get(k, {}), fb["principal"].get(k, {})
    if "r" in a1 and "r" in b1:
        p(f"  {k:6s} {f(a1['r']):>10s} {lx['holm'][k]:>8.4f}   {f(b1['r']):>10s} {fb['holm'][k]:>8.4f}")

la, fa = ler(f"fase_causal_A1_{a.data}.json"), ler(f"fase_causal_A1_finbert_{a.data}.json")
p("\nR2 — análise adicional A1 (Google + WordPress), p sem correção")
p(f"  {'teste':26s} {'r léxico':>10s} {'p':>8s}   {'r FinBERT':>10s} {'p':>8s}")
for k in la:
    if "r" in la[k] and "r" in fa.get(k, {}):
        p(f"  {k:26s} {f(la[k]['r']):>10s} {la[k]['p']:>8.4f}   {f(fa[k]['r']):>10s} {fa[k]['p']:>8.4f}")

r3 = pd.read_csv(R / f"fase_F_R3_resultado_original_{a.data}.csv")
p("\nR3 — resultado original por ativo (quantos dos 8 com p < 0,05; r médio)")
for rot in ("D-1", "D+0", "D+1"):
    lin = []
    for m in ("lexico", "finbert"):
        t = r3[r3["medida"] == m]
        lin.append(f"{m}: {int((t[f'p {rot}'] < 0.05).sum())} de {len(t)}, r médio {f(t[f'r {rot}'].mean())}")
    p(f"  {rot}:  " + "  |  ".join(lin))

# ───────────── exploratório E-F1 / E-F2 ─────────────
p("\nEXPLORATÓRIO (decidido depois de ver R1-R3; não confirmatório)")
p("D+0 em 2024-2026 (sentimento do pregão D x retorno anormal de D), separando as manchetes:")
n = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv", parse_dates=["data", "data_pregao"])
n = ajustar_pregao_brasilia(n[n["ticker"].isin(ATIVOS)].copy())
n["relato"] = n["titulo"].map(eh_relato_de_preco)
_, anormal = retornos_decompostos()
cal = anormal["cc"].index
cpos = {d: i for i, d in enumerate(cal)}
CC = anormal["cc"].reindex(cal)[ATIVOS].to_numpy(float)
EXP = {}
for medida in ("lexico", "finbert"):
    q = modelos.aplicar(n, medida)
    q["d"] = q["data_pregao"].dt.normalize().map(cpos)
    q = q.dropna(subset=["d"]); q["d"] = q["d"].astype(int)
    q["a"] = q["ticker"].map({t: i for i, t in enumerate(ATIVOS)})
    for nome, filtro in (("todas", q["relato"] | ~q["relato"]), ("informativas", ~q["relato"]),
                         ("só relato", q["relato"])):
        g = q[filtro].groupby(["a", "d"])["score_polaridade"].mean().reset_index()
        r = teste_parcial(g["score_polaridade"].to_numpy(float), g["a"].to_numpy(int), g["d"].to_numpy(int),
                          CC, [], n_perm=a.n_perm)
        EXP[f"{medida}|{nome}"] = r
        p(f"  {medida:8s} {nome:13s}: r = {f(r['r'])}  p = {r['p']:.4f}  n = {r['n']}" if "r" in r
          else f"  {medida:8s} {nome:13s}: {r}")
cor = []
for medida in ("lexico", "finbert"):
    q = modelos.aplicar(n, medida)
    cor.append(q["score_polaridade"].rename(medida))
both = pd.concat(cor, axis=1).dropna()
p(f"  Correlação entre os dois escores, manchete a manchete: {both.corr().iloc[0, 1]:+.3f} (n = {len(both)})")
rel = n["relato"].reindex(both.index)
for nome, m in (("relato", rel), ("informativas", ~rel)):
    p(f"  Escore médio em módulo — {nome:12s}: léxico {both.loc[m, 'lexico'].abs().mean():.3f}, "
      f"FinBERT {both.loc[m, 'finbert'].abs().mean():.3f}")

(R / f"fase_F_robustez_comparacao_{a.data}.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")
json.dump(EXP, open(R / f"fase_F_exploratorio_relato_{a.data}.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=float)
print(f"\nsalvo em: resultados/fase_F_robustez_comparacao_{a.data}.txt")
