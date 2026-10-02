# -*- coding: utf-8 -*-
"""
37_piloto_minuto.py — Fase G: o que acontece DENTRO da hora da notícia (piloto).

Pré-registro: docs/pre-registro_2026-10-02_fase-G_minuto.md (+ adendo 1)

Barras de 5 minutos (dados/minuto/), notícias com horário exato (Google real
ou WordPress com filtro de data), evento entre 10h30 e 16h20, barra da
publicação fora dos dois lados.
    M1 (notícia -> preço): sentimento x retorno anormal dos 30 min DEPOIS
    M2 (preço -> notícia): sentimento x retorno anormal dos 30 min ANTES
    Holm sobre M1 e M2; permutação: mesma faixa de 5 min em outro dia.
Secundárias: G-S1 (15 min), G-S2 (perfil -60..+60 min), G-S3 (outra medida),
G-S4 (controle positivo: manchetes de relato), G-S5 (dia errado),
G-D1/G-S6/G-S7 (adendo 1: atraso do horário do Google).

Uso:
    python scripts/37_piloto_minuto.py --medida finbert     (ou lexico)
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
from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise.horarios import filtrar_wordpress
from modulos.analise.validacao_lexico import tirar_fonte
from modulos.analise import modelos

ap = argparse.ArgumentParser()
ap.add_argument("--medida", default="lexico", choices=["lexico", "finbert", "distil"])
ap.add_argument("--n-perm", type=int, default=10_000)
ap.add_argument("--embaralhar", action="store_true", help="SÓ teste de código: sentimento embaralhado")
a = ap.parse_args()
RNG_TESTE = np.random.default_rng(7)
NP = a.n_perm
FUSO = "America/Sao_Paulo"
INICIO_SESSAO, PASSO, N_SLOTS = 10 * 60, 5, 83          # barras de 10h00 a 16h50
JAN = 6                                                   # 6 barras = 30 min

saida = []
def p(t=""):
    print(t)
    saida.append(str(t))

# ───────────────────────── barras de 5 minutos ─────────────────────────
series = {}
for t in ATIVOS:
    d = pd.read_csv(RAIZ / "dados" / "minuto" / f"{t}_5m.csv")
    hora = pd.to_datetime(d["Datetime"], utc=True).dt.tz_convert(FUSO).dt.tz_localize(None)
    d = d.assign(dia=hora.dt.normalize(), minuto=hora.dt.hour * 60 + hora.dt.minute)
    d = d[(d["minuto"] >= INICIO_SESSAO) & (d["minuto"] < INICIO_SESSAO + N_SLOTS * PASSO)]
    d = d[d["minuto"] % PASSO == 0].sort_values(["dia", "minuto"])
    ant = d.groupby("dia")["Close"].shift(1)
    base = ant.where(ant.notna(), d["Open"])
    d["r"] = np.log(d["Close"] / base)
    d["k"] = (d["minuto"] - INICIO_SESSAO) // PASSO
    series[t] = d.set_index(["dia", "k"])["r"]
painel = pd.DataFrame(series)
dias = sorted(painel.index.get_level_values(0).unique())
painel = painel.reindex(pd.MultiIndex.from_product([dias, range(N_SLOTS)]))
R = painel.to_numpy().reshape(len(dias), N_SLOTS, len(ATIVOS))
soma = np.nansum(R, axis=2, keepdims=True)
cnt = np.sum(~np.isnan(R), axis=2, keepdims=True)
A = R - (soma - np.nan_to_num(R)) / np.maximum(cnt - 1, 1)     # retorno anormal (média dos outros 7)
dpos = {d: i for i, d in enumerate(dias)}


def janela(desloc_ini, n):
    """W[d, k, a] = soma de A nas barras k+desloc_ini ... k+desloc_ini+n-1 (NaN se faltar barra)."""
    W = np.full_like(A, np.nan)
    for k in range(N_SLOTS):
        ini, fim = k + desloc_ini, k + desloc_ini + n
        if ini < 0 or fim > N_SLOTS:
            continue
        W[:, k, :] = A[:, ini:fim, :].sum(axis=1)                # NaN se alguma barra faltar
    return W


ANTES, DEPOIS = janela(-JAN, JAN), janela(1, JAN)
ANTES15, DEPOIS15 = janela(-3, 3), janela(1, 3)
p("=" * 86)
p(f"  FASE G — PILOTO DE MINUTO (barras de 5 min)   medida principal: {a.medida}")
p("=" * 86)
p(f"  Barras: {len(dias)} pregões, de {dias[0]:%d/%m/%Y} a {dias[-1]:%d/%m/%Y}; "
  f"{int(np.isfinite(R).sum())} barras-ativo")

# ───────────────────────── notícias com horário exato ─────────────────────────
def carregar_noticias():
    can = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv")
    rec = pd.read_csv(RAIZ / "dados" / "prospectivo" / "noticias_recentes.csv")
    can["origem"], rec["origem"] = "estudo", "coleta_recente"
    n = pd.concat([can, rec], ignore_index=True)
    n = n[n["ticker"].isin(ATIVOS)].copy()
    n = ajustar_pregao_brasilia(n)
    wp = pd.concat([pd.read_csv(RAIZ / "dados" / "horarios_wordpress.csv"),
                    pd.read_csv(RAIZ / "dados" / "prospectivo" / "horarios_wordpress_recentes.csv")],
                   ignore_index=True)
    wpf = filtrar_wordpress(n, wp)
    n = n.merge(wpf.drop_duplicates("url"), on="url", how="left")
    n["t_google"] = n["data_brasilia"].where(n["hora_real"])
    n["t_wp"] = n["t_wp_filtrado"]
    n["manchete"] = [tirar_fonte(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    n["relato"] = n["titulo"].map(eh_relato_de_preco)
    return n


noticias = carregar_noticias()
p(f"  Notícias (estudo + coleta recente, 8 ativos): {len(noticias)}")

# G-D1: atraso Google x WordPress
ambos = noticias.dropna(subset=["t_google", "t_wp"]).drop_duplicates("url")
dif = (ambos["t_google"] - ambos["t_wp"]).dt.total_seconds() / 60
p("")
p("  G-D1 (adendo 1) — diferença Google − WordPress, em minutos, nas notícias com as duas horas:")
if len(dif):
    q = dif.quantile([0.25, 0.5, 0.75])
    p(f"    n = {len(dif)} | mediana {q[0.5]:+.1f} | quartis {q[0.25]:+.1f} a {q[0.75]:+.1f} | "
      f"Google depois do site: {(dif > 0).mean():.1%} | iguais (±1 min): {(dif.abs() <= 1).mean():.1%} | "
      f"Google 5+ min depois: {(dif >= 5).mean():.1%}")
G_D1 = {"n": int(len(dif)), "mediana": float(dif.median()) if len(dif) else None,
        "frac_google_depois": float((dif > 0).mean()) if len(dif) else None,
        "frac_iguais_1min": float((dif.abs() <= 1).mean()) if len(dif) else None}


def eventos(n, prioridade="google", so_wp=False, medida="lexico"):
    """Um evento por (ativo, dia, faixa de 5 min), com a média do sentimento."""
    q = modelos.aplicar(n, medida) if medida != "lexico" else n.copy()
    if so_wp:
        q["t"] = q["t_wp"]
    elif prioridade == "google":
        q["t"] = q["t_google"].fillna(q["t_wp"])
    else:
        q["t"] = q["t_wp"].fillna(q["t_google"])
    q = q.dropna(subset=["t"])
    # a mesma manchete do mesmo ativo conta uma vez (a de horário mais cedo)
    q = q.sort_values("t").drop_duplicates(["ticker", "manchete"], keep="first")
    minuto = q["t"].dt.hour * 60 + q["t"].dt.minute
    dia = q["t"].dt.normalize()
    q = q[(q["t"].dt.weekday < 5) & (minuto >= 10 * 60 + 30) & (minuto < 16 * 60 + 20) & dia.isin(dpos)].copy()
    q["d"] = q["t"].dt.normalize().map(dpos).astype(int)
    q["k"] = ((q["t"].dt.hour * 60 + q["t"].dt.minute) - INICIO_SESSAO) // PASSO
    q["a"] = q["ticker"].map({t: i for i, t in enumerate(ATIVOS)})
    g = q.groupby(["a", "d", "k"]).agg(x=("score_polaridade", "mean"), relato=("relato", "max")).reset_index()
    if a.embaralhar:
        g["x"] = RNG_TESTE.permutation(g["x"].to_numpy())
    return g


def testar(g, W, nome, lado="bi"):
    if len(g) < 10:
        return {"erro": "amostra pequena", "n": int(len(g))}
    return teste_horario(g["x"].to_numpy(float), g["a"].to_numpy(int), g["d"].to_numpy(int),
                         g["k"].to_numpy(int), W, 0, n_perm=NP, lado=lado)


def fmt(r):
    if "erro" in r:
        return f"{r['erro']} (n={r['n']})"
    return f"r = {r['r']:+.4f}   p = {r['p']:.4f}   n = {r['n']}   (r detectável ~{r['mde']:.3f})"


RES = {"G_D1": G_D1}
ev = eventos(noticias, "google", medida=a.medida)
p(f"\n  Eventos válidos (10h30-16h20, prioridade Google > WordPress): {len(ev)}")
p("\n  ── TESTES PRINCIPAIS (Holm sobre M1 e M2) ──")
RES["M1"] = testar(ev, DEPOIS, "M1")
RES["M2"] = testar(ev, ANTES, "M2")
p(f"  M1  notícia -> 30 min DEPOIS (notícia -> preço) : {fmt(RES['M1'])}")
p(f"  M2  notícia <- 30 min ANTES  (preço -> notícia) : {fmt(RES['M2'])}")
pv = {k: RES[k]["p"] for k in ("M1", "M2") if "p" in RES[k]}
aj = holm(pv) if pv else {}
for k in pv:
    p(f"      {k}: p Holm = {aj[k]:.4f} -> {'REJEITA H0' if aj[k] < 0.05 else 'não rejeita'}")
RES["holm"] = aj

p("\n  ── SECUNDÁRIAS (sem correção) ──")
RES["GS1_depois15"] = testar(ev, DEPOIS15, "GS1d")
RES["GS1_antes15"] = testar(ev, ANTES15, "GS1a")
p(f"  G-S1  15 min DEPOIS : {fmt(RES['GS1_depois15'])}")
p(f"  G-S1  15 min ANTES  : {fmt(RES['GS1_antes15'])}")
outra = "lexico" if a.medida != "lexico" else "finbert"
try:
    ev2 = eventos(noticias, "google", medida=outra)
    RES["GS3_M1"], RES["GS3_M2"] = testar(ev2, DEPOIS, "x"), testar(ev2, ANTES, "x")
    p(f"  G-S3  M1 com {outra:<8}: {fmt(RES['GS3_M1'])}")
    p(f"  G-S3  M2 com {outra:<8}: {fmt(RES['GS3_M2'])}")
except Exception as e:
    p(f"  G-S3  outra medida indisponível: {e}")
evr = ev[ev["relato"]]
RES["GS4_relato_antes"] = testar(evr, ANTES, "GS4")
p(f"  G-S4  CONTROLE POSITIVO (relato) <- 30 min ANTES : {fmt(RES['GS4_relato_antes'])}")
ok = ev["d"] >= 1
evd = ev[ok].assign(d=ev.loc[ok, "d"] - 1)
RES["GS5_dia_errado"] = testar(evd, DEPOIS, "GS5")
p(f"  G-S5  FALSIFICAÇÃO (mesma faixa, pregão anterior) : {fmt(RES['GS5_dia_errado'])}")
ev6 = eventos(noticias, "wordpress", medida=a.medida)
RES["GS6_M1"], RES["GS6_M2"] = testar(ev6, DEPOIS, "x"), testar(ev6, ANTES, "x")
p(f"  G-S6  prioridade WordPress > Google, M1 : {fmt(RES['GS6_M1'])}")
p(f"  G-S6  prioridade WordPress > Google, M2 : {fmt(RES['GS6_M2'])}")
ev7 = eventos(noticias, so_wp=True, medida=a.medida)
RES["GS7_M1"], RES["GS7_M2"] = testar(ev7, DEPOIS, "x"), testar(ev7, ANTES, "x")
p(f"  G-S7  só hora do WordPress, M1 : {fmt(RES['GS7_M1'])}")
p(f"  G-S7  só hora do WordPress, M2 : {fmt(RES['GS7_M2'])}")

# G-S2: perfil -60..+60 min para os terços extremos (eventos 11h00-15h50)
evp = ev[(ev["k"] >= 12) & (ev["k"] <= N_SLOTS - 13)].copy()
perfil = []
if len(evp) >= 30:
    ter = pd.qcut(evp["x"].rank(method="first"), 3, labels=["neg", "neutro", "pos"]).to_numpy()
    for rel in range(-12, 13):
        y = A[evp["d"].to_numpy(), evp["k"].to_numpy() + rel, evp["a"].to_numpy()]
        for gname in ("neg", "pos"):
            m = (ter == gname) & np.isfinite(y)
            perfil.append({"barra_relativa": rel, "minutos": rel * 5, "grupo": gname,
                           "retorno_medio_pct": float(np.mean(y[m]) * 100) if m.any() else np.nan,
                           "n": int(m.sum())})
perf = pd.DataFrame(perfil)
if len(perf):
    p("  G-S2  perfil (retorno anormal médio por barra, %), terços extremos:")
    for gname in ("neg", "pos"):
        v = perf[perf["grupo"] == gname].set_index("minutos")["retorno_medio_pct"]
        acum = v.cumsum()
        p(f"      {gname}: acumulado -60→0 min: {acum.loc[-5]:+.3f}% | barra 0: {v.loc[0]:+.3f}% | "
          f"0→+60 min: {(acum.loc[60] - acum.loc[0]):+.3f}%")
p("=" * 86)

hoje = dt.date.today().isoformat()
PR = RAIZ / "resultados"
suf = f"_{a.medida}" + ("_TESTE_CODIGO_embaralhado" if a.embaralhar else "")
(PR / f"fase_G_piloto_minuto{suf}_{hoje}.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")
perf.to_csv(PR / f"fase_G_perfil_minuto{suf}_{hoje}.csv", index=False)
json.dump(RES, open(PR / f"fase_G_piloto_minuto{suf}_{hoje}.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=float)
print(f"\nsalvo em: resultados/fase_G_piloto_minuto{suf}_{hoje}.txt")
