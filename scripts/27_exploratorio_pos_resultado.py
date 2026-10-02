# -*- coding: utf-8 -*-
"""
27_exploratorio_pos_resultado.py — análises EXPLORATÓRIAS.

Decididas DEPOIS de ver os resultados da fase causal (02/10/2026). Não são
confirmatórias e não entram em nenhuma família de testes: servem para
INTERPRETAR o que foi achado. Usam os horários da análise A1 (Google +
WordPress filtrado por data).

E1: os testes de relato (A1_P3, A1_P5) só com notícias INFORMATIVAS (sem
    manchetes de relato). O "preço antes da notícia" vem só das manchetes
    óbvias, ou as notícias informativas também chegam depois do preço?
E2: notícia informativa no pregão -> hora seguinte (A1_P4 sem relato).
E3: janelas do resto do dia (da abertura até a notícia; da notícia até o
    fechamento), com os horários da A1.
"""
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np, pandas as pd
from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.causal import ATIVOS, retornos_decompostos, carregar_horario, teste_parcial, teste_horario, holm

NP = 10_000
def carregar(arq):
    n = pd.read_csv(RAIZ / "dados" / arq, parse_dates=["data", "data_pregao"])
    return ajustar_pregao_brasilia(n[n["ticker"].isin(ATIVOS)].copy())
n = pd.concat([carregar("noticias_com_sentimento.csv"), carregar("noticias_2021_2023.csv")], ignore_index=True)
n = n.drop_duplicates(subset=["ticker", "titulo", "data"])
n["relato"] = n["titulo"].map(eh_relato_de_preco)
n["a_idx"] = n["ticker"].map({t: i for i, t in enumerate(ATIVOS)})
n["t"] = n["data_brasilia"].where(n["hora_real"])
wf = pd.read_csv(RAIZ / "dados" / "horarios_wordpress_filtrado.csv", parse_dates=["t_wp_filtrado"]).drop_duplicates("url")
n = n.merge(wf, on="url", how="left"); n["t"] = n["t"].fillna(n["t_wp_filtrado"]); n = n.dropna(subset=["t"])

bruto, anormal = retornos_decompostos()
cal = anormal["cc"].index
GAP = anormal["abertura"].reindex(cal)[ATIVOS].to_numpy(float)
INTRA = anormal["pregao"].reindex(cal)[ATIVOS].to_numpy(float)
INTRA_ANT = np.full_like(INTRA, np.nan); INTRA_ANT[1:] = INTRA[:-1]
def prox(dia):
    i = int(np.searchsorted(cal.values, np.datetime64(dia), side="left")); return i if i < len(cal) else None
def noite(q):
    h = q["t"].dt.hour; dia = q["t"].dt.normalize(); util = dia.isin(cal)
    q = q[(~util) | (h < 10) | (h >= 18)].copy()
    d = []
    for di, hi, ui in zip(q["t"].dt.normalize(), q["t"].dt.hour, q["t"].dt.normalize().isin(cal)):
        i = prox(di)
        if i is not None and ui and hi >= 18: i += 1
        d.append(i if (i is not None and i < len(cal)) else None)
    q["d"] = d; q = q.dropna(subset=["d"]); q["d"] = q["d"].astype(int)
    g = q.groupby(["a_idx", "d"])["score_polaridade"].mean().reset_index()
    return g["score_polaridade"].to_numpy(float), g["a_idx"].to_numpy(int), g["d"].to_numpy(int)
dias_h, Hb, Ha = carregar_horario(); dpos = {d: i for i, d in enumerate(dias_h)}
def pregao(q):
    h = q["t"].dt.hour; dia = q["t"].dt.normalize()
    q = q[(h >= 11) & (h < 16) & dia.isin(dpos)].copy()
    q["dia"] = q["t"].dt.normalize().map(dpos).astype(int); q["k"] = q["t"].dt.hour - 10
    g = q.groupby(["a_idx", "dia", "k"])["score_polaridade"].mean().reset_index()
    return (g["score_polaridade"].to_numpy(float), g["a_idx"].to_numpy(int), g["dia"].to_numpy(int), g["k"].to_numpy(int))
def fmt(r):
    return f"{r['erro']} (n={r['n']})" if "erro" in r else f"r = {r['r']:+.4f}   p = {r['p']:.4f}   n = {r['n']}"

linhas = []
def p(s=""):
    print(s); linhas.append(s)
inf = n[~n["relato"]]
p("=" * 80); p("  EXPLORATÓRIO (decidido depois dos resultados; não confirmatório)"); p("=" * 80)
x, a, d = noite(inf)
E = {}
E["E1_noite_relato_informativas"] = teste_parcial(x, a, d, INTRA_ANT, [], n_perm=NP)
x, a, dh, k = pregao(inf)
E["E1_pregao_hora_anterior_informativas"] = teste_horario(x, a, dh, k, Ha, -1, n_perm=NP)
E["E2_pregao_hora_seguinte_informativas"] = teste_horario(x, a, dh, k, Ha, +1, n_perm=NP)
x, a, dh, k = pregao(n)
nd, nh, na = Ha.shape
cs = np.nancumsum(np.nan_to_num(Ha), axis=1)
PRE = np.full_like(Ha, np.nan); POS = np.full_like(Ha, np.nan)
for kk in range(nh):
    if kk > 0: PRE[:, kk, :] = cs[:, kk - 1, :]
    if kk < nh - 1: POS[:, kk, :] = cs[:, -1, :] - cs[:, kk, :]
E["E3_da_abertura_ate_a_noticia"] = teste_horario(x, a, dh, k, PRE, 0, n_perm=NP)
E["E3_da_noticia_ate_o_fechamento"] = teste_horario(x, a, dh, k, POS, 0, n_perm=NP)
for kk, v in E.items():
    p(f"  {kk:<40}: {fmt(v)}")
p("=" * 80)
(RAIZ / "resultados" / "exploratorio_pos_resultado.txt").write_text("\n".join(linhas), encoding="utf-8")
