# -*- coding: utf-8 -*-
"""
40_janelas_curtas.py — Fase G, adendo 2: a reação acontece em até 5 minutos?

Pré-registro: docs/pre-registro_2026-10-02_fase-G_minuto_ADENDO-2.md

Barras de 1 minuto (20 pregões) e de 5 minutos (60 pregões):
    C1  notícia -> minutos +1 a +5      (barras de 1 min; minuto da publicação fora)
    C2  minutos -5 a -1 -> notícia      (barras de 1 min)
    C3  notícia -> barra de 5 min seguinte à da publicação
    C4  barra de 5 min anterior à da publicação -> notícia
    Holm sobre C1-C4. Permutação: mesmo minuto (ou mesma faixa de 5 min) em
    outro dia sorteado, todos os ativos juntos (teste_horario), 10.000, semente 42.
Secundárias: C-S1 (1, 2 e 3 min), C-S2 (pulando o minuto vizinho),
C-S3 (FinBERT), C-S4 (controle positivo), C-S5 (perfil -15 a +15 min).

Uso:
    python scripts/40_janelas_curtas.py                  (léxico, a medida principal)
    python scripts/40_janelas_curtas.py --embaralhar     (SÓ teste de código)
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

from modulos.analise.causal import ATIVOS, teste_horario, holm
from modulos.analise.minuto import painel, janela, noticias_exatas, eventos

ap = argparse.ArgumentParser()
ap.add_argument("--medida", default="lexico", choices=["lexico", "finbert"])
ap.add_argument("--n-perm", type=int, default=10_000)
ap.add_argument("--embaralhar", action="store_true", help="SÓ teste de código: sentimento embaralhado")
a = ap.parse_args()
NP = a.n_perm
RNG = np.random.default_rng(7) if a.embaralhar else None

saida = []
def p(t=""):
    print(t)
    saida.append(str(t))

def fmt(r):
    if "erro" in r:
        return f"{r['erro']} (n={r['n']})"
    return f"r = {r['r']:+.4f}   p = {r['p']:.4f}   n = {r['n']}   (r detectável ~{r['mde']:.3f})"

def testar(g, W):
    if len(g) < 10:
        return {"erro": "amostra pequena", "n": int(len(g))}
    return teste_horario(g["x"].to_numpy(float), g["a"].to_numpy(int), g["d"].to_numpy(int),
                         g["k"].to_numpy(int), W, 0, n_perm=NP)

# ───────────── painéis ─────────────
dias1, R1, A1 = painel(ATIVOS, "1m", 600, 1015, 1)      # 10h00 ... 16h54
dias5, R5, A5 = painel(ATIVOS, "5m", 600, 1015, 5)      # 10h00 ... 16h50
noticias = noticias_exatas(ATIVOS)

p("=" * 86)
p(f"  FASE G, ADENDO 2 — JANELAS CURTAS   medida: {a.medida}"
  + ("   [SENTIMENTO EMBARALHADO — TESTE DE CÓDIGO]" if a.embaralhar else ""))
p("=" * 86)
p(f"  Barras de 1 min: {len(dias1)} pregões ({dias1[0]:%d/%m} a {dias1[-1]:%d/%m/%Y}); "
  f"barras de 5 min: {len(dias5)} pregões ({dias5[0]:%d/%m} a {dias5[-1]:%d/%m/%Y})")

def ev1(medida=a.medida):
    return eventos(noticias, ATIVOS, dias1, 600, 1, 610, 1005, medida, rng_embaralhar=RNG)

def ev5(medida=a.medida):
    return eventos(noticias, ATIVOS, dias5, 600, 5, 630, 980, medida, rng_embaralhar=RNG)

E1, E5 = ev1(), ev5()
p(f"  Eventos: {len(E1)} com barra de 1 min (10h10-16h45); {len(E5)} com barra de 5 min (10h30-16h20)")

RES = {}
p("\n  ── FAMÍLIA DO ADENDO 2 (Holm sobre C1 a C4) ──")
RES["C1"] = testar(E1, janela(A1, 1, 5))
RES["C2"] = testar(E1, janela(A1, -5, 5))
RES["C3"] = testar(E5, janela(A5, 1, 1))
RES["C4"] = testar(E5, janela(A5, -1, 1))
rot = {"C1": "notícia -> minutos +1 a +5 (barra de 1 min)",
       "C2": "minutos -5 a -1 -> notícia (barra de 1 min)",
       "C3": "notícia -> barra de 5 min seguinte",
       "C4": "barra de 5 min anterior -> notícia"}
for k in ("C1", "C2", "C3", "C4"):
    p(f"  {k}  {rot[k]:<46}: {fmt(RES[k])}")
pv = {k: RES[k]["p"] for k in ("C1", "C2", "C3", "C4") if "p" in RES[k]}
aj = holm(pv) if pv else {}
for k in pv:
    p(f"      {k}: p Holm = {aj[k]:.4f} -> {'REJEITA H0' if aj[k] < 0.05 else 'não rejeita'}")
RES["holm"] = aj

p("\n  ── SECUNDÁRIAS (sem correção) ──")
for n_min in (1, 2, 3):
    RES[f"CS1_depois_{n_min}min"] = testar(E1, janela(A1, 1, n_min))
    RES[f"CS1_antes_{n_min}min"] = testar(E1, janela(A1, -n_min, n_min))
    p(f"  C-S1  {n_min} min DEPOIS : {fmt(RES[f'CS1_depois_{n_min}min'])}")
    p(f"  C-S1  {n_min} min ANTES  : {fmt(RES[f'CS1_antes_{n_min}min'])}")
RES["CS2_depois_pula1"] = testar(E1, janela(A1, 2, 5))
RES["CS2_antes_pula1"] = testar(E1, janela(A1, -6, 5))
p(f"  C-S2  minutos +2 a +6 : {fmt(RES['CS2_depois_pula1'])}")
p(f"  C-S2  minutos -6 a -2 : {fmt(RES['CS2_antes_pula1'])}")
if not a.embaralhar:
    outra = "finbert" if a.medida == "lexico" else "lexico"
    F1, F5 = ev1(outra), ev5(outra)
    for k, (E, W) in {"C1": (F1, janela(A1, 1, 5)), "C2": (F1, janela(A1, -5, 5)),
                      "C3": (F5, janela(A5, 1, 1)), "C4": (F5, janela(A5, -1, 1))}.items():
        RES[f"CS3_{k}_{outra}"] = testar(E, W)
        p(f"  C-S3  {k} com {outra:<8}: {fmt(RES[f'CS3_{k}_{outra}'])}")
RES["CS4_relato_antes5"] = testar(E1[E1["relato"]], janela(A1, -5, 5))
p(f"  C-S4  CONTROLE POSITIVO (relato) <- 5 min antes : {fmt(RES['CS4_relato_antes5'])}")

# C-S5: perfil minuto a minuto, -15 a +15, terços extremos
ok = (E1["k"] >= 15) & (E1["k"] <= A1.shape[1] - 16)
Ep = E1[ok].copy()
perfil = []
if len(Ep) >= 30:
    ter = pd.qcut(Ep["x"].rank(method="first"), 3, labels=["neg", "neutro", "pos"]).to_numpy()
    for rel in range(-15, 16):
        y = A1[Ep["d"].to_numpy(), Ep["k"].to_numpy() + rel, Ep["a"].to_numpy()]
        for gname in ("neg", "pos"):
            m = (ter == gname) & np.isfinite(y)
            perfil.append({"minuto_relativo": rel, "grupo": gname,
                           "retorno_medio_pct": float(np.mean(y[m]) * 100) if m.any() else np.nan,
                           "n": int(m.sum())})
perf = pd.DataFrame(perfil)
# Faixas de incerteza do caminho ACUMULADO (bootstrap dos eventos, 2.000, semente 42).
# Fronteira 0 = início do minuto -15; fronteira 15 = início do minuto da publicação (zero).
bandas = []
if len(Ep) >= 30:
    rng_b = np.random.default_rng(42)
    rels = np.arange(-15, 16)
    for gname in ("neg", "pos"):
        sel = ter == gname
        Y = A1[Ep["d"].to_numpy()[sel][:, None], Ep["k"].to_numpy()[sel][:, None] + rels[None, :],
               Ep["a"].to_numpy()[sel][:, None]]                      # eventos x 31 minutos
        Y = np.where(np.isfinite(Y), Y, np.nan) * 100

        def caminho(M):
            media = np.nanmean(M, axis=0)
            nivel = np.concatenate([[0.0], np.cumsum(np.nan_to_num(media))])
            return nivel - nivel[15]

        base_ = caminho(Y)
        boot = np.array([caminho(Y[rng_b.integers(0, len(Y), len(Y))]) for _ in range(2000)])
        lo_, hi_ = np.percentile(boot, 2.5, axis=0), np.percentile(boot, 97.5, axis=0)
        for i in range(len(base_)):
            bandas.append({"grupo": gname, "fronteira_min": i - 15, "nivel_pct": base_[i],
                           "ic95_baixo": lo_[i], "ic95_alto": hi_[i], "n_eventos": int(sel.sum())})
bandas = pd.DataFrame(bandas)
if len(perf):
    p(f"  C-S5  perfil (retorno anormal médio, %), terços extremos, n = {len(Ep)} eventos:")
    for gname in ("neg", "pos"):
        v = perf[perf["grupo"] == gname].set_index("minuto_relativo")["retorno_medio_pct"]
        p(f"      {gname}: −15→−1 min: {v.loc[-15:-1].sum():+.3f}% | minuto 0: {v.loc[0]:+.3f}% | "
          f"+1→+5: {v.loc[1:5].sum():+.3f}% | +6→+15: {v.loc[6:15].sum():+.3f}%")
p("=" * 86)

if not a.embaralhar:
    hoje = dt.date.today().isoformat()
    PR = RAIZ / "resultados"
    base = f"fase_G_janelas_curtas_{a.medida}_{hoje}"
    (PR / f"{base}.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")
    perf.to_csv(PR / f"fase_G_perfil_minuto_a_minuto_{a.medida}_{hoje}.csv", index=False)
    bandas.to_csv(PR / f"fase_G_perfil_minuto_bandas_{a.medida}_{hoje}.csv", index=False)
    json.dump(RES, open(PR / f"{base}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    print(f"\nsalvo em: resultados/{base}.txt")
