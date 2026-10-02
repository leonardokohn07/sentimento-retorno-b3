# -*- coding: utf-8 -*-
"""
19_sem_manchetes_de_preco.py — TESTE 1 do pré-registro de 02/10/2026.

Retira as manchetes que RELATAM o movimento da cotação ("Ação da Vale salta
3,9%", "Ibovespa fecha em alta") e refaz o D+0 só com as informativas.
Se a correlação sobrevive, ela não depende do jornal relatando o pregão.

Uso:  .\\venv\\Scripts\\python scripts\\19_sem_manchetes_de_preco.py
"""
import argparse
from _base_direcao import *
from scipy import stats
from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.painel import teste_agrupado

ap = argparse.ArgumentParser()
ap.add_argument("--embaralhar", action="store_true")
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()

p = Saida()
noticias = carregar_noticias(a.embaralhar)
noticias["relato"] = noticias["titulo"].map(eh_relato_de_preco)
R = carregar_retornos()

p("=" * 78)
p("  TESTE 1 — SEM AS MANCHETES QUE RELATAM PREÇO" + ("   [EMBARALHADO — TESTE DE CÓDIGO]" if a.embaralhar else ""))
p("=" * 78)
p(f"  Notícias: {len(noticias)}  |  manchetes de relato: {int(noticias['relato'].sum())} "
  f"({noticias['relato'].mean():.1%})")

for nome, sub in (("TODAS (referência)", noticias),
                  ("INFORMATIVAS (principal)", noticias[~noticias["relato"]]),
                  ("SÓ RELATO DE PREÇO", noticias[noticias["relato"]])):
    painel = pd.concat([sentimento_diario(sub, t) for t in ATIVOS], ignore_index=True)
    p(""); p(f"  --- {nome}: {len(sub)} notícias, {len(painel)} pares ativo-dia ---")
    sig = 0; testados = 0
    for t in ATIVOS:
        q = painel[painel["ticker"] == t].merge(R[[t]].rename(columns={t: "ret"}),
                                                 left_on="data", right_index=True)
        if len(q) >= 60 and q["sentimento"].std() > 0:
            r, pv = stats.pearsonr(q["sentimento"], q["ret"])
            testados += 1; sig += pv < 0.05
            p(f"      {t:<9} n={len(q):>4}  r={r:+.4f}  p={pv:.4f}")
    if testados:
        p(f"      por ativo (descritivo): {sig} de {testados} com p < 0,05 em D+0")
    d0 = teste_agrupado(painel, R, n_perm=a.n_perm)
    dm1 = teste_agrupado(painel, R.shift(1), n_perm=a.n_perm)
    for rot, res in (("D+0", d0), ("D-1", dm1)):
        if "erro" in res:
            p(f"    AGRUPADO {rot}: {res['erro']} (n={res['n']})")
        else:
            p(f"    AGRUPADO {rot}: r = {res['r']:+.4f}   p = {res['p']:.4f}   n = {res['n']}   "
              f"(menor r detectável ~{res['mde']:.3f})")
    if nome.startswith("INFORMATIVAS"):
        principal = d0

p(""); p("  VEREDITO (regra pré-registrada, H0-1 = informativas em D+0):")
if principal["p"] < 0.05 and principal["r"] > 0:
    p("    H0-1 REJEITADA com r > 0: a relação de D+0 NÃO depende das manchetes")
    p("    que relatam preço.")
elif principal["p"] < 0.05:
    p("    H0-1 rejeitada, mas com r < 0: achado inesperado, reportar.")
else:
    p(f"    H0-1 NÃO rejeitada: sem as manchetes de relato, não há evidência de associação")
    p(f"    em D+0 (o teste detectaria r acima de ~{principal['mde']:.3f}).")
p("=" * 78)
if not a.embaralhar:
    p.salvar("teste1_sem_manchetes_de_preco")
