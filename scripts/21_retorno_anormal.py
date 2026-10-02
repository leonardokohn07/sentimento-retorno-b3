# -*- coding: utf-8 -*-
"""
21_retorno_anormal.py — TESTE 3 do pré-registro de 02/10/2026.

Troca o retorno bruto pelo retorno ANORMAL (o que a ação andou além do que o
Ibovespa explicaria). Se a correlação sobrevive, não é só a bolsa inteira
caindo ou subindo junto com o noticiário.

Uso:  .\\venv\\Scripts\\python scripts\\21_retorno_anormal.py
"""
import argparse
from _base_direcao import *
from scipy import stats
from modulos.analise.painel import teste_agrupado
from modulos.analise.mercado import carregar_ibovespa, matriz_retorno_anormal

ap = argparse.ArgumentParser()
ap.add_argument("--embaralhar", action="store_true")
ap.add_argument("--mercado-proxy", action="store_true",
                help="SÓ PARA TESTAR O CÓDIGO sem internet: média dos ativos no lugar do Ibovespa")
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()

p = Saida()
noticias = carregar_noticias(a.embaralhar)
R = carregar_retornos()
mercado = R.mean(axis=1).rename("PROXY") if a.mercado_proxy else carregar_ibovespa()
AR, params = matriz_retorno_anormal(R[ATIVOS], mercado)
painel = pd.concat([sentimento_diario(noticias, t) for t in ATIVOS], ignore_index=True)

p("=" * 78)
p("  TESTE 3 — RETORNO ANORMAL (descontado o mercado)"
  + ("   [TESTE DE CÓDIGO]" if (a.embaralhar or a.mercado_proxy) else ""))
p("=" * 78)
p(f"  Mercado: {'média dos ativos (proxy de teste)' if a.mercado_proxy else 'Ibovespa (^BVSP)'}")
p("  Alfa e beta estimados nos 250 pregões antes de 02/01/2024:")
for _, r in params.iterrows():
    p(f"      {r['ativo']:<9} beta = {r['beta']:.2f}   R² do modelo = {r['r2_modelo']:.2f}")
p("")
sig = 0
for t in ATIVOS:
    q = painel[painel["ticker"] == t].merge(AR[[t]].rename(columns={t: "ar"}),
                                             left_on="data", right_index=True).dropna()
    if len(q) >= 60:
        r, pv = stats.pearsonr(q["sentimento"], q["ar"]); sig += pv < 0.05
        p(f"      {t:<9} n={len(q):>4}  r(sentimento, AR D+0) = {r:+.4f}  p = {pv:.4f}")
p(f"      por ativo (descritivo): {sig} de 8 com p < 0,05")
d0 = teste_agrupado(painel, AR, n_perm=a.n_perm)
dm1 = teste_agrupado(painel, AR.shift(1), n_perm=a.n_perm)
p("")
p(f"  AGRUPADO D+0 (H0-3): r = {d0['r']:+.4f}   p = {d0['p']:.4f}   n = {d0['n']}   (menor r detectável ~{d0['mde']:.3f})")
p(f"  AGRUPADO D-1       : r = {dm1['r']:+.4f}   p = {dm1['p']:.4f}")
p(""); p("  VEREDITO (regra pré-registrada):")
if d0["p"] < 0.05 and d0["r"] > 0:
    p("    H0-3 REJEITADA com r > 0: a associação sobrevive ao desconto do mercado.")
    p("    Não é só o dia ruim (ou bom) da bolsa inteira.")
elif d0["p"] < 0.05:
    p("    H0-3 rejeitada com r < 0: achado inesperado, reportar.")
else:
    p("    H0-3 NÃO rejeitada: descontado o mercado, não há evidência de associação.")
    p("    Parte relevante do efeito de D+0 pode ser o movimento da bolsa inteira.")
p("=" * 78)
if not (a.embaralhar or a.mercado_proxy):
    p.salvar("teste3_retorno_anormal")
