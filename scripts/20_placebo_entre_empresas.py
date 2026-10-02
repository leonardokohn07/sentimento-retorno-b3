# -*- coding: utf-8 -*-
"""
20_placebo_entre_empresas.py — TESTE 2 do pré-registro de 02/10/2026.

Sentimento da empresa A contra o retorno ANORMAL da empresa B. Se a notícia
age sobre a própria empresa, a correlação "cruzada" deve ser ~0 e a "própria"
(A com A) deve ser maior. Se a cruzada também aparece, há um humor geral do
mercado que o desconto do Ibovespa não tirou.

Pares principais: os 54 de setores diferentes. ITUB4 x BBDC4 à parte.

Uso:  .\\venv\\Scripts\\python scripts\\20_placebo_entre_empresas.py
"""
import argparse
from _base_direcao import *
from modulos.analise.mercado import carregar_ibovespa, matriz_retorno_anormal

ap = argparse.ArgumentParser()
ap.add_argument("--embaralhar", action="store_true")
ap.add_argument("--mercado-proxy", action="store_true")
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()

p = Saida()
noticias = carregar_noticias(a.embaralhar)
R = carregar_retornos()
mercado = R.mean(axis=1).rename("PROXY") if a.mercado_proxy else carregar_ibovespa()
AR, _ = matriz_retorno_anormal(R[ATIVOS], mercado)

ini = noticias["data_pregao"].min(); fim = noticias["data_pregao"].max()
U = AR.loc[(AR.index >= ini) & (AR.index <= fim)].dropna()
datas = U.index.to_numpy()
Z = ((U - U.mean()) / U.std(ddof=1)).to_numpy()          # dias x 8
k = len(ATIVOS)

xs, idx = [], []
for t in ATIVOS:
    s = sentimento_diario(noticias, t)
    s = s[s["data"].isin(U.index)]
    x = s["sentimento"].to_numpy(dtype=float)
    xs.append((x - x.mean()) / x.std(ddof=1))
    idx.append(np.searchsorted(datas, s["data"].to_numpy()))

def matriz_r(perm=None):
    M = np.empty((k, k))
    for i in range(k):
        d = idx[i] if perm is None else perm[idx[i]]
        Y = Z[d]; Y = Y - Y.mean(axis=0)
        M[i] = xs[i] @ Y / (np.sqrt(xs[i] @ xs[i]) * np.sqrt((Y * Y).sum(axis=0)))
    return M

mesmo_setor = np.array([[SETOR[ATIVOS[i]] == SETOR[ATIVOS[j]] for j in range(k)] for i in range(k)])
proprio = np.eye(k, dtype=bool)
cruz = ~mesmo_setor                                      # 54 pares, setores diferentes
banco = mesmo_setor & ~proprio                           # ITUB4 x BBDC4

def stats_de(M):
    return M[proprio].mean(), M[cruz].mean(), M[proprio].mean() - M[cruz].mean()

M = matriz_r()
own, cross, delta = stats_de(M)
rng = np.random.default_rng(42); c_cross = c_delta = 0
for _ in range(a.n_perm):
    o2, c2, d2 = stats_de(matriz_r(rng.permutation(len(datas))))
    c_cross += abs(c2) >= abs(cross); c_delta += abs(d2) >= abs(delta)
p_cross = (c_cross + 1) / (a.n_perm + 1); p_delta = (c_delta + 1) / (a.n_perm + 1)

p("=" * 78)
p("  TESTE 2 — PLACEBO ENTRE EMPRESAS (retorno anormal)"
  + ("   [TESTE DE CÓDIGO]" if (a.embaralhar or a.mercado_proxy) else ""))
p("=" * 78)
p("  Linhas = notícias de A; colunas = retorno anormal de B (mesmo dia)")
p("           " + " ".join(f"{t[:5]:>7}" for t in ATIVOS))
for i, t in enumerate(ATIVOS):
    p(f"  {t[:5]:>7}  " + " ".join(f"{M[i, j]:+7.3f}" for j in range(k)))
p("")
p(f"  Média das 8 próprias (A com A)        : {own:+.4f}")
p(f"  Média das 54 cruzadas (setor diferente): {cross:+.4f}   H0-2a p = {p_cross:.4f}")
p(f"  Própria - cruzada                     : {delta:+.4f}   H0-2b p = {p_delta:.4f}")
p(f"  Pares entre bancos (à parte)          : {M[banco].mean():+.4f}")
p(""); p("  VEREDITO (regra pré-registrada):")
if p_delta < 0.05 and delta > 0 and p_cross >= 0.05:
    p("    Cruzada ~0 e própria significativamente maior: o efeito é da notícia da")
    p("    PRÓPRIA empresa, não de um humor geral do mercado.")
elif p_cross < 0.05 and cross > 0:
    p("    Cruzada significativa: existe um humor geral que o desconto do Ibovespa")
    p("    não removeu." + (" Mesmo assim, a própria é maior que a cruzada." if (p_delta < 0.05 and delta > 0) else ""))
elif p_delta < 0.05 and delta > 0:
    p("    Própria significativamente maior que a cruzada.")
else:
    p("    Nenhuma diferença significativa entre própria e cruzada.")
p("=" * 78)
if not (a.embaralhar or a.mercado_proxy):
    p.salvar("teste2_placebo_entre_empresas")
