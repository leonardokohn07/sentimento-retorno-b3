# -*- coding: utf-8 -*-
"""
22_granger.py — TESTE 5 do pré-registro de 02/10/2026.

Granger nos dois sentidos, por ativo, com dados diários:
  sentimento -> retorno : os sentimentos passados melhoram a previsão do
                          retorno de hoje, além dos retornos passados?
  retorno -> sentimento : os retornos passados melhoram a previsão do
                          sentimento de hoje, além dos sentimentos passados?

Wald robusto (HC1). Um sentido é "sustentado" se der p < 0,05 em 3 ou mais
dos 8 ativos (pelo acaso: 0,6%). Dias sem notícia: sentimento 0.
Limitação: com dados diários, Granger não enxerga o mesmo dia.

Uso:  .\\venv\\Scripts\\python scripts\\22_granger.py
"""
import argparse
from _base_direcao import *
from scipy import stats

ap = argparse.ArgumentParser()
ap.add_argument("--embaralhar", action="store_true")
a = ap.parse_args()


def wald_hc1(y, X, cols):
    n, kx = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    meat = (X * e[:, None] ** 2).T @ X
    V = XtX_inv @ meat @ XtX_inv * n / (n - kx)
    C = np.zeros((len(cols), kx)); C[np.arange(len(cols)), cols] = 1
    Cb = C @ b
    W = float(Cb @ np.linalg.inv(C @ V @ C.T) @ Cb)
    return W, float(stats.chi2.sf(W, len(cols)))


def granger(alvo, causa, p):
    T = len(alvo)
    y = alvo[p:]
    lag_a = np.column_stack([alvo[p - i:T - i] for i in range(1, p + 1)])
    lag_c = np.column_stack([causa[p - i:T - i] for i in range(1, p + 1)])
    X = np.column_stack([np.ones(len(y)), lag_a, lag_c])
    return wald_hc1(y, X, list(range(1 + p, 1 + 2 * p)))


pr = Saida()
noticias = carregar_noticias(a.embaralhar)
R = carregar_retornos()
ini, fim = noticias["data_pregao"].min(), noticias["data_pregao"].max()
cal = R.index[(R.index >= ini) & (R.index <= fim)]

pr("=" * 78)
pr("  TESTE 5 — GRANGER NOS DOIS SENTIDOS" + ("   [EMBARALHADO — TESTE DE CÓDIGO]" if a.embaralhar else ""))
pr("=" * 78)
pr(f"  Pregões: {len(cal)} ({cal[0]:%d/%m/%Y} a {cal[-1]:%d/%m/%Y})")
resumo = {}
for p in (5, 1):
    pr(""); pr(f"  --- {p} defasagem(ns) {'(PRINCIPAL)' if p == 5 else '(sensibilidade)'} ---")
    pr(f"    {'ativo':<9} {'sent->ret p':>12} {'ret->sent p':>12}")
    c1 = c2 = 0
    for t in ATIVOS:
        s = sentimento_diario(noticias, t).set_index("data")["sentimento"]
        s = s.reindex(cal).fillna(0.0).to_numpy()
        r = R.loc[cal, t].to_numpy()
        _, p_sr = granger(r, s, p)
        _, p_rs = granger(s, r, p)
        c1 += p_sr < 0.05; c2 += p_rs < 0.05
        pr(f"    {t:<9} {p_sr:>12.4f}{'*' if p_sr < .05 else ' '} {p_rs:>12.4f}{'*' if p_rs < .05 else ' '}")
    pr(f"    significativos: sentimento->retorno {c1} de 8 | retorno->sentimento {c2} de 8")
    resumo[p] = (c1, c2)

c1, c2 = resumo[5]
pr(""); pr("  VEREDITO (regra pré-registrada: 3 ou mais de 8, com 5 defasagens):")
pr(f"    sentimento -> retorno : {'SUSTENTADO' if c1 >= 3 else 'não sustentado'} ({c1} de 8)")
pr(f"    retorno -> sentimento : {'SUSTENTADO' if c2 >= 3 else 'não sustentado'} ({c2} de 8)")
pr("    (Granger testa as defasagens de 1 a 5 pregões; não diz nada sobre o mesmo dia.)")
pr("=" * 78)
if not a.embaralhar:
    pr.salvar("teste5_granger")
