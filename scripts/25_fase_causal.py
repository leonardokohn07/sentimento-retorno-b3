# -*- coding: utf-8 -*-
"""
25_fase_causal.py — executa TODOS os testes do pré-registro mestre
(docs/pre-registro_2026-10-02_fase-causal.md), na ordem, com correção de
Holm na família principal (P1 a P9) e as análises secundárias (S1 a S7).

Uso:
    .\\venv\\Scripts\\python scripts\\25_fase_causal.py
    .\\venv\\Scripts\\python scripts\\25_fase_causal.py --embaralhar --n-perm 300   (SÓ teste de código)
    .\\venv\\Scripts\\python scripts\\25_fase_causal.py --medida finbert   (Fase F, robustez R1/R2)
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.causal import (ATIVOS, retornos_decompostos, carregar_horario,
                                    teste_parcial, teste_horario, holm, _corr)
from modulos.analise.mercado import carregar_ibovespa, matriz_retorno_anormal
from modulos.analise import modelos

ap = argparse.ArgumentParser()
ap.add_argument("--embaralhar", action="store_true")
ap.add_argument("--n-perm", type=int, default=10_000)
ap.add_argument("--semente-embaralhar", type=int, default=7)
ap.add_argument("--so-principal", action="store_true")
ap.add_argument("--adicional-wp", action="store_true",
                help="Análise adicional A1 (adendo 1): Google + WordPress com filtro de data; só P2-P5, S4, S5, S7")
ap.add_argument("--medida", default="lexico", choices=["lexico", "finbert", "distil"],
                help="Fase F: troca o score_polaridade pelo escore de um modelo de linguagem")
a = ap.parse_args()
SUF = "" if a.medida == "lexico" else f"_{a.medida}"   # nome dos arquivos de saída
NP = a.n_perm
FIM_ESTUDO = pd.Timestamp("2024-01-01")

linhas = []
def p(s=""):
    print(s); linhas.append(str(s))

# ═══════════════════ dados ═══════════════════
def carregar(arq, periodo):
    n = pd.read_csv(RAIZ / "dados" / arq, parse_dates=["data", "data_pregao"])
    n = n[n["ticker"].isin(ATIVOS)].copy()
    n = ajustar_pregao_brasilia(n)
    n["periodo"] = periodo
    return n

noticias = pd.concat([carregar("noticias_com_sentimento.csv", "2024-2026"),
                      carregar("noticias_2021_2023.csv", "2021-2023")], ignore_index=True)
noticias = noticias.drop_duplicates(subset=["ticker", "titulo", "data"])
noticias = modelos.aplicar(noticias, a.medida)
if a.embaralhar:
    noticias["score_polaridade"] = np.random.default_rng(a.semente_embaralhar).permutation(noticias["score_polaridade"].to_numpy())
noticias["relato"] = noticias["titulo"].map(eh_relato_de_preco)
a_map = {t: i for i, t in enumerate(ATIVOS)}
noticias["a_idx"] = noticias["ticker"].map(a_map)

# ── horários: Google (hora real) > WordPress (validado) > busca (só sensibilidade)
noticias["hora_fonte"] = np.where(noticias["hora_real"], "google", "")
noticias["t_brt"] = noticias["data_brasilia"].where(noticias["hora_real"])

wp_info = "arquivo ausente"
arq_wp = RAIZ / "dados" / "horarios_wordpress.csv"
usar_wp = False
if arq_wp.exists():
    wp = pd.read_csv(arq_wp)
    wp = wp[wp["status"] == "ok"].dropna(subset=["wp_date_gmt"])
    wp["t_wp"] = pd.to_datetime(wp["wp_date_gmt"], utc=True, errors="coerce").dt.tz_convert(
        "America/Sao_Paulo").dt.tz_localize(None)
    wp = wp.dropna(subset=["t_wp"]).drop_duplicates("url")
    m = noticias.merge(wp[["url", "t_wp", "dominio"]], on="url", how="left")
    sobre = m[m["hora_real"] & m["t_wp"].notna()]
    dif = (sobre["t_wp"] - sobre["data_brasilia"]).dt.total_seconds().abs() / 60
    concord = float((dif <= 15).mean()) if len(sobre) else float("nan")
    usar_wp = len(sobre) >= 20 and concord >= 0.85
    wp_info = (f"{len(wp)} horários; sobreposição com o Google: {len(sobre)} notícias, "
               f"{concord:.1%} dentro de 15 min -> {'APROVADO' if usar_wp else 'REPROVADO'} (corte: 85%, n >= 20)")
    if usar_wp:
        novo = m["t_brt"].isna() & m["t_wp"].notna()
        m.loc[novo, "t_brt"] = m.loc[novo, "t_wp"]
        m.loc[novo, "hora_fonte"] = "wordpress"
    noticias = m.drop(columns=["t_wp", "dominio"])

if a.adicional_wp:
    wf = pd.read_csv(RAIZ / "dados" / "horarios_wordpress_filtrado.csv", parse_dates=["t_wp_filtrado"])
    noticias = noticias.merge(wf.drop_duplicates("url"), on="url", how="left")
    novo = noticias["t_brt"].isna() & noticias["t_wp_filtrado"].notna()
    noticias.loc[novo, "t_brt"] = noticias.loc[novo, "t_wp_filtrado"]
    noticias.loc[novo, "hora_fonte"] = "wordpress_filtrado"
    noticias = noticias.drop(columns=["t_wp_filtrado"])
    wp_info = "A1: Google + WordPress filtrado por data (adendo 1; validação 94,0% em 15 min, n = 100)"
busca = pd.read_csv(RAIZ / "dados" / "horarios_busca.csv") if (RAIZ / "dados" / "horarios_busca.csv").exists() else pd.DataFrame()
if len(busca):
    busca = busca[~busca["controle"]]
    busca["t_busca"] = pd.to_datetime(busca["data_pagina"] + " " + busca["hora_brasilia"], format="%d/%m/%Y %H:%M", errors="coerce")
    noticias = noticias.merge(busca[["url", "t_busca"]].drop_duplicates("url"), on="url", how="left")
else:
    noticias["t_busca"] = pd.NaT

bruto, anormal = retornos_decompostos()
cal = anormal["cc"].index
cpos = {d: i for i, d in enumerate(cal)}
def M(df):
    return df.reindex(cal)[ATIVOS].to_numpy(float)
GAP, INTRA, CC = M(anormal["abertura"]), M(anormal["pregao"]), M(anormal["cc"])
GAPb, INTRAb, CCb = M(bruto["abertura"]), M(bruto["pregao"]), M(bruto["cc"])
def sh(X, k):            # sh(X, +1)[d] = X[d-1] ; sh(X, -1)[d] = X[d+1]
    Y = np.full_like(X, np.nan)
    if k > 0: Y[k:] = X[:-k]
    else: Y[:k] = X[-k:]
    return Y

def agrega(df, chave_d):
    g = df.groupby(["a_idx", chave_d])["score_polaridade"].mean().reset_index()
    return g["score_polaridade"].to_numpy(float), g["a_idx"].to_numpy(int), g[chave_d].to_numpy(int)

def prox_pregao_idx(dia):
    i = int(np.searchsorted(cal.values, np.datetime64(dia), side="left"))
    return i if i < len(cal) else None

# ═══════════════════ montagem das linhas ═══════════════════
cdate = noticias["data_brasilia"].dt.normalize()
eh_util = noticias["data_brasilia"].dt.weekday < 5

def linhas_p1(periodo):
    q = noticias[(noticias["periodo"] == periodo) & eh_util & cdate.isin(cal)].copy()
    q["d"] = cdate[q.index].map(cpos)
    return agrega(q, "d")

def linhas_p9(periodo):
    q = noticias[(noticias["periodo"] == periodo) & ~eh_util].copy()
    q["d"] = [prox_pregao_idx(x) for x in cdate[q.index]]
    q = q.dropna(subset=["d"]); q["d"] = q["d"].astype(int)
    return agrega(q, "d")

def com_hora(col_t, incluir_busca=False):
    q = noticias.copy()
    t = q[col_t]
    if incluir_busca:
        t = t.fillna(q["t_busca"])
    q["t"] = t
    return q.dropna(subset=["t"])

def linhas_noite(q):
    h = q["t"].dt.hour; dia = q["t"].dt.normalize(); util = dia.isin(cal)
    sel = (~util) | (h < 10) | (h >= 18)
    q = q[sel].copy(); h = q["t"].dt.hour; dia = q["t"].dt.normalize(); util = dia.isin(cal)
    d = []
    for di, hi, ui in zip(dia, h, util):
        i = prox_pregao_idx(di)
        if i is None: d.append(None); continue
        if ui and hi >= 18: i += 1
        d.append(i if i < len(cal) else None)
    q["d"] = d
    q = q.dropna(subset=["d"]); q["d"] = q["d"].astype(int)
    return q

dias_h, Hb, Ha = carregar_horario()
dpos_h = {d: i for i, d in enumerate(dias_h)}
def linhas_pregao(q):
    h = q["t"].dt.hour; dia = q["t"].dt.normalize()
    q = q[(h >= 11) & (h < 16) & dia.isin(dpos_h)].copy()
    q["dia"] = q["t"].dt.normalize().map(dpos_h).astype(int)
    q["k"] = q["t"].dt.hour - 10
    g = q.groupby(["a_idx", "dia", "k"])["score_polaridade"].mean().reset_index()
    return (g["score_polaridade"].to_numpy(float), g["a_idx"].to_numpy(int),
            g["dia"].to_numpy(int), g["k"].to_numpy(int))

def fmt(res):
    if "erro" in res:
        return f"{res['erro']} (n={res['n']})"
    return f"r = {res['r']:+.4f}   p = {res['p']:.4f}   n = {res['n']}   (r detectável ~{res['mde']:.3f}, {res['lado']})"

# ═══════════════════ cabeçalho ═══════════════════
p("=" * 86)
p("  FASE CAUSAL — testes do pré-registro mestre de 02/10/2026"
  + ("   [SENTIMENTO EMBARALHADO — TESTE DE CÓDIGO]" if a.embaralhar else ""))
p("=" * 86)
p(f"  Horários WordPress: {wp_info}")
q_g = com_hora("t_brt")
p(f"  Notícias com horário no principal: {len(q_g)}  "
  f"(fontes: {q_g['hora_fonte'].value_counts().to_dict()})")
p(f"  + horários da busca web (só sensibilidade): {int(noticias['t_busca'].notna().sum())}")

R = {}
if a.adicional_wp:
    p(""); p("  ── ANÁLISE ADICIONAL A1 (fora da família de Holm) ──")
    qn = linhas_noite(q_g); x, ai, di = agrega(qn, "d")
    R["A1_P2"] = teste_parcial(x, ai, di, GAP, [sh(INTRA, 1)], n_perm=NP)
    R["A1_P3"] = teste_parcial(x, ai, di, sh(INTRA, 1), [], n_perm=NP)
    x, ai, dh, kh = linhas_pregao(q_g)
    R["A1_P4"] = teste_horario(x, ai, dh, kh, Ha, +1, n_perm=NP)
    R["A1_P5"] = teste_horario(x, ai, dh, kh, Ha, -1, n_perm=NP)
    qr = q_g[q_g["relato"]]
    x2, ai2, di2 = agrega(linhas_noite(qr), "d")
    R["A1_S4_noite_relato"] = teste_parcial(x2, ai2, di2, sh(INTRA, 1), [], n_perm=NP)
    x3, ai3, dh3, kh3 = linhas_pregao(qr)
    R["A1_S4_pregao_relato_antes"] = teste_horario(x3, ai3, dh3, kh3, Ha, -1, n_perm=NP)
    ok_ = dh >= 1
    R["A1_S5_dia_errado"] = teste_horario(x[ok_], ai[ok_], dh[ok_] - 1, kh[ok_], Ha, +1, n_perm=NP)
    rot = {"A1_P2": "noite -> ABERTURA seguinte | pregão anterior", "A1_P3": "noite <- PREGÃO passado (relato)",
           "A1_P4": "pregão -> HORA SEGUINTE", "A1_P5": "pregão <- HORA ANTERIOR (relato/vazamento)",
           "A1_S4_noite_relato": "CONTROLE POSITIVO noite <- pregão passado",
           "A1_S4_pregao_relato_antes": "CONTROLE POSITIVO pregão <- hora anterior",
           "A1_S5_dia_errado": "FALSIFICAÇÃO dia errado"}
    for k, v in R.items():
        p(f"  {k:<26} {rot[k]:<46}: {fmt(v)}")
    ter = pd.qcut(pd.Series(x).rank(method="first"), 3, labels=["neg", "neutro", "pos"]).to_numpy()
    perfil = []
    for rel in range(-3, 4):
        alvo = kh + rel; okr = (alvo >= 0) & (alvo < Ha.shape[1])
        y = Ha[dh[okr], alvo[okr], ai[okr]]
        for g in ("neg", "pos"):
            mg = (ter[okr] == g) & np.isfinite(y)
            perfil.append({"hora_relativa": rel, "grupo": g, "retorno_medio_pct": float(np.mean(y[mg]) * 100) if mg.any() else np.nan, "n": int(mg.sum())})
    perf = pd.DataFrame(perfil)
    p("  A1 S7 perfil médio (retorno anormal %):")
    for g in ("neg", "pos"):
        v = perf[perf["grupo"] == g].set_index("hora_relativa")["retorno_medio_pct"]
        p(f"      tercil {g:<4} " + "  ".join(f"{h:+d}h:{v[h]:+.3f}" for h in v.index))
    p("=" * 86)
    if not a.embaralhar:
        hoje = date.today().isoformat(); PR = RAIZ / "resultados"; PR.mkdir(exist_ok=True)
        (PR / f"fase_causal_A1{SUF}_{hoje}.txt").write_text("\n".join(linhas), encoding="utf-8")
        perf.to_csv(PR / f"fase_causal_A1{SUF}_perfil_horario_{hoje}.csv", index=False)
        json.dump(R, open(PR / f"fase_causal_A1{SUF}_{hoje}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
        print(f"\nsalvo em: resultados/fase_causal_A1{SUF}_{hoje}.txt")
    sys.exit(0)
# ═══════════════════ FAMÍLIA PRINCIPAL ═══════════════════
p(""); p("  ── FAMÍLIA PRINCIPAL (Holm sobre P1 a P9) ──")

x, ai, di = linhas_p1("2024-2026")
R["P1"] = teste_parcial(x, ai, di, sh(GAP, -1), [INTRA, GAP], n_perm=NP)
p(f"  P1  notícias do dia D -> ABERTURA de D+1 | pregão D, abertura D : {fmt(R['P1'])}")

qn = linhas_noite(q_g)
x, ai, di = agrega(qn, "d")
R["P2"] = teste_parcial(x, ai, di, GAP, [sh(INTRA, 1)], n_perm=NP)
p(f"  P2  notícias da noite/madrugada -> ABERTURA seguinte | pregão anterior : {fmt(R['P2'])}")
R["P3"] = teste_parcial(x, ai, di, sh(INTRA, 1), [], n_perm=NP)
p(f"  P3  notícias da noite/madrugada <- PREGÃO que já passou (relato)      : {fmt(R['P3'])}")

x, ai, dh, kh = linhas_pregao(q_g)
R["P4"] = teste_horario(x, ai, dh, kh, Ha, +1, n_perm=NP)
p(f"  P4  notícia no pregão -> HORA SEGUINTE à publicação                    : {fmt(R['P4'])}")
R["P5"] = teste_horario(x, ai, dh, kh, Ha, -1, n_perm=NP)
p(f"  P5  notícia no pregão <- HORA ANTERIOR à publicação (relato/vazamento) : {fmt(R['P5'])}")

x, ai, di = linhas_p1("2021-2023")
lado6 = "pos" if ("r" in R["P1"] and R["P1"]["r"] > 0) else "neg"
R["P6"] = teste_parcial(x, ai, di, sh(GAP, -1), [INTRA, GAP], n_perm=NP, lado=lado6)
p(f"  P6  RÉPLICA de P1 em 2021-2023                                          : {fmt(R['P6'])}")

q7 = noticias[(noticias["periodo"] == "2021-2023") & ~noticias["relato"]].copy()
q7["d"] = q7["data_pregao"].dt.normalize().map(cpos)
q7 = q7.dropna(subset=["d"]); q7["d"] = q7["d"].astype(int)
x, ai, di = agrega(q7, "d")
R["P7"] = teste_parcial(x, ai, di, CCb, [], n_perm=NP, lado="pos")
p(f"  P7  RÉPLICA do Teste 1 (informativas, D+0) em 2021-2023                 : {fmt(R['P7'])}")

try:
    ibov = carregar_ibovespa(baixar_se_faltar=False)
    ret_cc = bruto["cc"].dropna()
    _, par = matriz_retorno_anormal(ret_cc[ATIVOS], ibov)      # alfa e beta estimados em 2023 (como no Teste 3)
    comum = ret_cc.index.intersection(ibov.index)
    AR = pd.DataFrame({r_["ativo"]: ret_cc.loc[comum, r_["ativo"]] - (r_["alfa"] + r_["beta"] * ibov.loc[comum])
                       for _, r_ in par.iterrows()})                # mesmos parâmetros aplicados a TODO o período
    ARm = AR.reindex(cal)[ATIVOS].to_numpy(float)
    q8 = noticias[noticias["periodo"] == "2021-2023"].copy()
    q8["d"] = q8["data_pregao"].dt.normalize().map(cpos)
    q8 = q8.dropna(subset=["d"]); q8["d"] = q8["d"].astype(int)
    x, ai, di = agrega(q8, "d")
    R["P8"] = teste_parcial(x, ai, di, ARm, [], n_perm=NP, lado="pos")
except Exception as e:
    R["P8"] = {"erro": f"Ibovespa indisponível: {e}", "n": 0}
p(f"  P8  RÉPLICA do Teste 3 (retorno anormal, D+0) em 2021-2023              : {fmt(R['P8'])}")

x, ai, di = linhas_p9("2024-2026")
R["P9"] = teste_parcial(x, ai, di, GAP, [sh(INTRA, 1)], n_perm=NP)
p(f"  P9  notícias de fim de semana -> ABERTURA de segunda | pregão de sexta : {fmt(R['P9'])}")

pv = {k: v["p"] for k, v in R.items() if "p" in v}
aj = holm(pv)
p(""); p(f"  {'teste':<6} {'r':>8} {'p bruto':>9} {'p Holm':>9}  decisão (α = 5%)")
for k in sorted(R):
    if "p" in R[k]:
        p(f"  {k:<6} {R[k]['r']:>+8.4f} {R[k]['p']:>9.4f} {aj[k]:>9.4f}  {'REJEITA H0' if aj[k] < 0.05 else 'não rejeita'}")
    else:
        p(f"  {k:<6} {'—':>8} {'—':>9} {'—':>9}  {R[k]['erro']}")

# ═══════════════════ SECUNDÁRIAS ═══════════════════
if a.so_principal:
    print("CALIB " + " ".join(f"{k}={R[k].get('p', float('nan')):.4f}" for k in sorted(R)))
    sys.exit(0)
S = {}
p(""); p("  ── ANÁLISES SECUNDÁRIAS (sem correção; servem de apoio) ──")
# S1 janelas do resto do dia
x, ai, dh, kh = linhas_pregao(q_g)
nd, nh, na = Ha.shape
PRE_DIA = np.full_like(Ha, np.nan); POS_DIA = np.full_like(Ha, np.nan)
cs = np.nancumsum(np.nan_to_num(Ha), axis=1)
for k in range(nh):
    PRE_DIA[:, k, :] = cs[:, k - 1, :] if k > 0 else np.nan
    POS_DIA[:, k, :] = cs[:, -1, :] - cs[:, k, :] if k < nh - 1 else np.nan
S["S1_pos_dia"] = teste_horario(x, ai, dh, kh, POS_DIA, 0, n_perm=NP)
S["S1_pre_dia"] = teste_horario(x, ai, dh, kh, PRE_DIA, 0, n_perm=NP)
p(f"  S1  pregão: do fim da hora da notícia ao FECHAMENTO : {fmt(S['S1_pos_dia'])}")
p(f"  S1  pregão: da ABERTURA ao início da hora da notícia: {fmt(S['S1_pre_dia'])}")
# S2 brutos
x, ai, di = linhas_p1("2024-2026")
S["S2_P1"] = teste_parcial(x, ai, di, sh(GAPb, -1), [INTRAb, GAPb], n_perm=NP)
x, ai, di = agrega(qn, "d")
S["S2_P2"] = teste_parcial(x, ai, di, GAPb, [sh(INTRAb, 1)], n_perm=NP)
S["S2_P3"] = teste_parcial(x, ai, di, sh(INTRAb, 1), [], n_perm=NP)
x, ai, dh, kh = linhas_pregao(q_g)
S["S2_P4"] = teste_horario(x, ai, dh, kh, Hb, +1, n_perm=NP)
S["S2_P5"] = teste_horario(x, ai, dh, kh, Hb, -1, n_perm=NP)
for k in ("P1", "P2", "P3", "P4", "P5"):
    p(f"  S2  {k} com retorno BRUTO                            : {fmt(S['S2_' + k])}")
# S3 com horários da busca
q_b = com_hora("t_brt", incluir_busca=True)
x, ai, di = agrega(linhas_noite(q_b), "d")
S["S3_P2"] = teste_parcial(x, ai, di, GAP, [sh(INTRA, 1)], n_perm=NP)
S["S3_P3"] = teste_parcial(x, ai, di, sh(INTRA, 1), [], n_perm=NP)
x, ai, dh, kh = linhas_pregao(q_b)
S["S3_P4"] = teste_horario(x, ai, dh, kh, Ha, +1, n_perm=NP)
S["S3_P5"] = teste_horario(x, ai, dh, kh, Ha, -1, n_perm=NP)
for k in ("P2", "P3", "P4", "P5"):
    p(f"  S3  {k} + horários da busca web                      : {fmt(S['S3_' + k])}")
# S4 controle positivo do método: manchetes de relato
qr = q_g[q_g["relato"]]
x, ai, di = agrega(linhas_noite(qr), "d")
S["S4_noite_relato"] = teste_parcial(x, ai, di, sh(INTRA, 1), [], n_perm=NP)
x, ai, dh, kh = linhas_pregao(qr)
S["S4_pregao_relato_antes"] = teste_horario(x, ai, dh, kh, Ha, -1, n_perm=NP)
p(f"  S4  CONTROLE POSITIVO: relato da noite <- pregão passado : {fmt(S['S4_noite_relato'])}")
p(f"  S4  CONTROLE POSITIVO: relato no pregão <- hora anterior : {fmt(S['S4_pregao_relato_antes'])}")
# S5 falsificação: a mesma hora, mas do pregão ANTERIOR (dia errado)
x, ai, dh, kh = linhas_pregao(q_g)
ok = dh >= 1
S["S5_dia_errado"] = teste_horario(x[ok], ai[ok], dh[ok] - 1, kh[ok], Ha, +1, n_perm=NP)
p(f"  S5  FALSIFICAÇÃO: hora seguinte, mas do DIA ANTERIOR     : {fmt(S['S5_dia_errado'])}")
# S6 placebo própria x cruzada em 2021-2023 (retorno anormal LOO, D+0)
q6 = noticias[noticias["periodo"] == "2021-2023"].copy()
q6["d"] = q6["data_pregao"].dt.normalize().map(cpos)
q6 = q6.dropna(subset=["d"]); q6["d"] = q6["d"].astype(int)
x6, a6, d6 = agrega(q6, "d")
Z = (CC - np.nanmean(CC, axis=0)) / np.nanstd(CC, axis=0, ddof=1)
def placebo(perm=None):
    own, cross = [], []
    for i in range(len(ATIVOS)):
        m = a6 == i
        xi = x6[m]; xi = (xi - xi.mean()) / xi.std(ddof=1)
        dd = d6[m] if perm is None else perm[d6[m]]
        for j in range(len(ATIVOS)):
            y = Z[dd, j]; f = np.isfinite(y)
            r = _corr(xi[f], y[f])
            (own if i == j else cross).append(r)
    return np.mean(own), np.mean(cross)
o6, c6 = placebo()
rng = np.random.default_rng(42); cnt = 0; nperm6 = max(200, NP // 10)
for _ in range(nperm6):
    o, c = placebo(rng.permutation(len(cal)))
    cnt += (o - c) >= (o6 - c6)
S["S6_placebo_2021"] = {"r": o6 - c6, "p": (cnt + 1) / (nperm6 + 1), "n": int(len(x6)), "mde": float("nan"), "lado": "pos"}
p(f"  S6  RÉPLICA do placebo em 2021-2023 (própria - cruzada) : própria {o6:+.4f}, cruzada {c6:+.4f}, "
  f"diferença p = {S['S6_placebo_2021']['p']:.4f}")
# S7 perfil horário (descritivo) — salvo em CSV para o gráfico
x, ai, dh, kh = linhas_pregao(q_g)
ter = pd.qcut(pd.Series(x).rank(method="first"), 3, labels=["neg", "neutro", "pos"]).to_numpy()
perfil = []
for rel in range(-3, 4):
    alvo = kh + rel
    okr = (alvo >= 0) & (alvo < nh)
    y = Ha[dh[okr], alvo[okr], ai[okr]]
    for g in ("neg", "pos"):
        mg = (ter[okr] == g) & np.isfinite(y)
        perfil.append({"hora_relativa": rel, "grupo": g, "retorno_medio_pct": float(np.mean(y[mg]) * 100) if mg.any() else np.nan,
                       "n": int(mg.sum())})
perf = pd.DataFrame(perfil)
p("  S7  perfil médio (retorno anormal %, notícias no pregão; descritivo):")
for g in ("neg", "pos"):
    v = perf[perf["grupo"] == g].set_index("hora_relativa")["retorno_medio_pct"]
    p(f"      tercil {g:<4} " + "  ".join(f"{h:+d}h:{v[h]:+.3f}" for h in v.index))

p("=" * 86)
if not a.embaralhar:
    hoje = date.today().isoformat()
    PR = RAIZ / "resultados"; PR.mkdir(exist_ok=True)
    (PR / f"fase_causal{SUF}_{hoje}.txt").write_text("\n".join(linhas), encoding="utf-8")
    perf.to_csv(PR / f"fase_causal{SUF}_perfil_horario_{hoje}.csv", index=False)
    json.dump({"principal": R, "holm": aj, "secundarias": S, "wordpress": wp_info},
              open(PR / f"fase_causal{SUF}_{hoje}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    print(f"\nsalvo em: resultados/fase_causal{SUF}_{hoje}.txt (+ .json e perfil horário)")
