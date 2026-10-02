# -*- coding: utf-8 -*-
"""
38_smallcaps_testes.py — Fase H: os testes nas ações de menor liquidez.

Pré-registro: docs/pre-registro_2026-10-02_fase-H_small-caps.md
Dados: dados/smallcaps/ (coletados pelo scripts/33_smallcaps.py)

    H1  D+0: sentimento do pregão D x retorno anormal de D (unicaudal, r > 0)
    H2  notícias do dia útil D -> ABERTURA anormal de D+1 | pregão D e abertura D
    H3  notícias do pregão D <- retorno anormal de D-1 (preço -> notícia)
    H4  notícias de fim de semana -> ABERTURA anormal de segunda | pregão de sexta
    Holm sobre H1-H4. Retorno anormal = ativo - média das outras small caps (β = 1).
    Estatística e permutação: as da fase causal (teste_parcial, 10.000, semente 42).

Uso:  python scripts/38_smallcaps_testes.py --medida finbert   (ou lexico)
"""
import argparse
import datetime as dt
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

from modulos.analise.causal import ajustar_mercado_loo, teste_parcial, holm
from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise import modelos

ap = argparse.ArgumentParser()
ap.add_argument("--medida", default="lexico", choices=["lexico", "finbert", "distil"])
ap.add_argument("--n-perm", type=int, default=10_000)
ap.add_argument("--embaralhar", action="store_true", help="SÓ teste de código: sentimento embaralhado")
a = ap.parse_args()
RNG_TESTE = np.random.default_rng(7)
NP = a.n_perm
PASTA = RAIZ / "dados" / "smallcaps"

saida = []
def p(t=""):
    print(t)
    saida.append(str(t))

sel = pd.read_csv(PASTA / "selecao_smallcaps.csv")
ATIVOS = sorted(f"{c}.SA" for c in sel.loc[sel["sorteado"], "codigo"])

# ───────────── preços: abertura, pregão e fechamento a fechamento ─────────────
O, C = {}, {}
for t in ATIVOS:
    d = pd.read_csv(PASTA / "precos" / f"{t}_1d.csv", index_col=0, parse_dates=True)
    d.index = pd.to_datetime(d.index).normalize()
    O[t], C[t] = d["Open"], d["Close"]
O, C = pd.DataFrame(O), pd.DataFrame(C)
ok = O.notna().all(axis=1) & C.notna().all(axis=1) & (O > 0).all(axis=1)
O, C = O[ok], C[ok]
bruto = {"abertura": np.log(O / C.shift(1)), "pregao": np.log(C / O), "cc": np.log(C / C.shift(1))}
anormal = {k: ajustar_mercado_loo(v.dropna()) for k, v in bruto.items()}
cal = anormal["cc"].index
cpos = {d: i for i, d in enumerate(cal)}
M = lambda df: df.reindex(cal)[ATIVOS].to_numpy(float)
GAP, INTRA, CC = M(anormal["abertura"]), M(anormal["pregao"]), M(anormal["cc"])


def sh(X, k):            # sh(X, +1)[d] = X[d-1] ; sh(X, -1)[d] = X[d+1]
    Y = np.full_like(X, np.nan)
    if k > 0:
        Y[k:] = X[:-k]
    else:
        Y[:k] = X[-k:]
    return Y


# ───────────── notícias ─────────────
n = pd.read_csv(PASTA / "noticias_smallcaps.csv", parse_dates=["data", "data_pregao"])
n = n[n["ticker"].isin(ATIVOS) & (n["data"] < "2026-09-07")].copy()
n = ajustar_pregao_brasilia(n)
if a.medida != "lexico":
    n = modelos.aplicar(n, a.medida)
n["a_idx"] = n["ticker"].map({t: i for i, t in enumerate(ATIVOS)})
cdate = n["data_brasilia"].dt.normalize()
eh_util = n["data_brasilia"].dt.weekday < 5


def agrega(q, chave):
    g = q.groupby(["a_idx", chave])["score_polaridade"].mean().reset_index()
    x = g["score_polaridade"].to_numpy(float)
    if a.embaralhar:
        x = RNG_TESTE.permutation(x)
    return x, g["a_idx"].to_numpy(int), g[chave].to_numpy(int)


def prox(dia):
    i = int(np.searchsorted(cal.values, np.datetime64(dia), side="left"))
    return i if i < len(cal) else None


def fmt(r):
    if "erro" in r:
        return f"{r['erro']} (n={r['n']})"
    return (f"r = {r['r']:+.4f}   p = {r['p']:.4f}   n = {r['n']}   "
            f"(r detectável ~{r['mde']:.3f}, {r['lado']})")


p("=" * 86)
p(f"  FASE H — SMALL CAPS   medida: {a.medida}")
p("=" * 86)
p(f"  Ativos sorteados: {', '.join(t.replace('.SA', '') for t in ATIVOS)}")
p(f"  Pregões com preço dos 8: {len(cal)} ({cal[0]:%d/%m/%Y} a {cal[-1]:%d/%m/%Y})")
p(f"  Notícias (até 06/09/2026): {len(n)}  | por ativo: "
  + ", ".join(f"{t.replace('.SA', '')} {int((n['ticker'] == t).sum())}" for t in ATIVOS))

R = {}
q1 = n.copy()
q1["d"] = q1["data_pregao"].dt.normalize().map(cpos)
q1 = q1.dropna(subset=["d"]); q1["d"] = q1["d"].astype(int)
x, ai, di = agrega(q1, "d")
R["H1"] = teste_parcial(x, ai, di, CC, [], n_perm=NP, lado="pos")
R["H3"] = teste_parcial(x, ai, di, sh(CC, 1), [], n_perm=NP)

q2 = n[eh_util & cdate.isin(cpos)].copy()
q2["d"] = cdate[q2.index].map(cpos).astype(int)
x, ai, di = agrega(q2, "d")
R["H2"] = teste_parcial(x, ai, di, sh(GAP, -1), [INTRA, GAP], n_perm=NP)

q4 = n[~eh_util].copy()
q4["d"] = [prox(x_) for x_ in cdate[q4.index]]
q4 = q4.dropna(subset=["d"]); q4["d"] = q4["d"].astype(int)
x, ai, di = agrega(q4, "d")
R["H4"] = teste_parcial(x, ai, di, GAP, [sh(INTRA, 1)], n_perm=NP)

rot = {"H1": "D+0: sentimento do pregão D x retorno anormal D (réplica)",
       "H2": "notícias do dia D -> ABERTURA de D+1 | pregão D, abertura D",
       "H3": "notícias do pregão D <- retorno anormal de D-1",
       "H4": "fim de semana -> ABERTURA de segunda | pregão de sexta"}
for k in ("H1", "H2", "H3", "H4"):
    p(f"  {k}  {rot[k]:<62}: {fmt(R[k])}")
pv = {k: v["p"] for k, v in R.items() if "p" in v}
aj = holm(pv)
p("")
p(f"  {'teste':<6} {'r':>8} {'p bruto':>9} {'p Holm':>9}  decisão (α = 5%)")
for k in sorted(pv):
    p(f"  {k:<6} {R[k]['r']:>+8.4f} {R[k]['p']:>9.4f} {aj[k]:>9.4f}  "
      f"{'REJEITA H0' if aj[k] < 0.05 else 'não rejeita'}")
p("=" * 86)

hoje = dt.date.today().isoformat()
arq = RAIZ / "resultados" / (f"fase_H_smallcaps_{a.medida}_{hoje}.txt" if not a.embaralhar
                             else f"fase_H_smallcaps_{a.medida}_TESTE_CODIGO_embaralhado_{hoje}.txt")
arq.write_text("\n".join(saida) + "\n", encoding="utf-8")
json.dump({"ativos": ATIVOS, "resultados": R, "holm": aj}, open(arq.with_suffix(".json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=float)
print(f"\nsalvo em: resultados/{arq.name}")
