# -*- coding: utf-8 -*-
"""
causal.py — ferramentas da fase de causalidade (pré-registro de 02/10/2026).

Decompõe o retorno diário em ABERTURA (fechamento anterior -> abertura) e
PREGÃO (abertura -> fechamento), monta as barras horárias e faz o teste
agrupado com correlação parcial e permutação em blocos de data.

Mercado: média das OUTRAS ações (leave-one-out), porque a abertura do
Ibovespa no Yahoo não é confiável (igual ao fechamento anterior em 29,6% dos
dias). Retorno anormal = retorno do ativo - média das demais (beta = 1).
"""
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA",
          "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
HORAS = list(range(10, 17))            # barras de 60 min: 10h ... 16h


# ───────────────────────── preços diários ─────────────────────────
def carregar_ohlc():
    O, C = {}, {}
    for arq in sorted((RAIZ / "dados" / "cache_precos").glob("*_1d.csv")):
        t = arq.name.replace("_1d.csv", "")
        d = pd.read_csv(arq, index_col=0, parse_dates=True)
        d.index = pd.to_datetime(d.index).normalize()
        O[t], C[t] = d["Open"], d["Close"]
    O, C = pd.DataFrame(O), pd.DataFrame(C)
    ok = O.notna().all(axis=1) & C.notna().all(axis=1) & (O > 0).all(axis=1)
    return O[ok], C[ok]


def ajustar_mercado_loo(M: pd.DataFrame) -> pd.DataFrame:
    """Retorno do ativo menos a média das demais colunas (leave-one-out)."""
    k = M.shape[1]
    soma = M.sum(axis=1).to_numpy()[:, None]
    loo = (soma - M.to_numpy()) / (k - 1)
    return pd.DataFrame(M.to_numpy() - loo, index=M.index, columns=M.columns)


def retornos_decompostos():
    """Abertura, pregão e fechamento-a-fechamento, brutos e ajustados ao mercado."""
    O, C = carregar_ohlc()
    gap = np.log(O / C.shift(1))
    intra = np.log(C / O)
    cc = np.log(C / C.shift(1))
    bruto = {"abertura": gap, "pregao": intra, "cc": cc}
    anormal = {k: ajustar_mercado_loo(v.dropna()) for k, v in bruto.items()}
    return bruto, anormal


# ───────────────────────── barras horárias ─────────────────────────
def carregar_horario():
    """
    Devolve (dias, H_bruto, H_anormal), com H[i_dia, i_hora, i_ativo] = retorno
    logarítmico da barra (fechamento contra o fechamento da barra anterior do
    MESMO dia; na 1ª barra, fechamento contra abertura).
    """
    series = {}
    for t in ATIVOS:
        d = pd.read_csv(RAIZ / "dados" / "intradiario" / f"{t}_60m.csv")
        dt = pd.to_datetime(d["Datetime"], utc=True).dt.tz_convert("America/Sao_Paulo").dt.tz_localize(None)
        d = d.assign(dia=dt.dt.normalize(), hora=dt.dt.hour)
        d = d[d["hora"].isin(HORAS)].sort_values(["dia", "hora"])
        prev = d.groupby("dia")["Close"].shift(1)
        base = prev.where(prev.notna(), d["Open"])
        d["r"] = np.log(d["Close"] / base)
        series[t] = d.set_index(["dia", "hora"])["r"]
    painel = pd.DataFrame(series)
    dias = sorted(painel.index.get_level_values(0).unique())
    idx = pd.MultiIndex.from_product([dias, HORAS], names=["dia", "hora"])
    painel = painel.reindex(idx)
    Hb = painel.to_numpy().reshape(len(dias), len(HORAS), len(ATIVOS))
    soma = np.nansum(Hb, axis=2, keepdims=True)
    cnt = np.sum(~np.isnan(Hb), axis=2, keepdims=True)
    loo = (soma - np.nan_to_num(Hb)) / np.maximum(cnt - 1, 1)
    Ha = Hb - loo
    return pd.DatetimeIndex(dias), Hb, Ha


# ───────────────────────── teste agrupado ─────────────────────────
def _z_por_grupo(v, g):
    out = np.empty_like(v, dtype=float)
    for k in np.unique(g):
        m = g == k
        s = v[m].std(ddof=1)
        out[m] = (v[m] - v[m].mean()) / s if s > 0 else np.nan
    return out


def _residuo(y, X):
    if X is None or X.shape[1] == 0:
        return y - y.mean()
    X1 = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return y - X1 @ b


def _corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))


def teste_parcial(x, a_idx, d_idx, Y, controles=(), n_perm=10_000, semente=42,
                  lado="bi"):
    """
    Correlação parcial agrupada entre x (sentimento, por linha) e o resultado
    Y[d, a], controlando por matrizes `controles` [d, a].

    - Y e controles são residualizados por ativo em TODO o calendário.
    - x é padronizado dentro do ativo e residualizado nos controles das linhas.
    - p-valor: permutação em blocos de data (sorteia qual data fornece o
      resultado, levando todos os ativos juntos).
    lado: "bi" (bicaudal), "pos" (unicaudal, r > 0) ou "neg".
    """
    Y = np.asarray(Y, float)
    Cs = [np.asarray(c, float) for c in controles]
    valid_d = np.isfinite(Y).all(axis=1)
    for c in Cs:
        valid_d &= np.isfinite(c).all(axis=1)
    EY = np.full_like(Y, np.nan)
    for j in range(Y.shape[1]):
        Xc = np.column_stack([c[valid_d, j] for c in Cs]) if Cs else None
        e = _residuo(Y[valid_d, j], Xc)
        EY[valid_d, j] = (e - e.mean()) / e.std(ddof=1)
    keep = valid_d[d_idx] & np.isfinite(x)
    x, a_idx, d_idx = x[keep], a_idx[keep], d_idx[keep]
    xz = _z_por_grupo(x, a_idx)
    ok = np.isfinite(xz)
    xz, a_idx, d_idx = xz[ok], a_idx[ok], d_idx[ok]
    if len(xz) < 10:
        return {"erro": "amostra pequena", "n": int(len(xz))}
    Xc_rows = np.column_stack([_z_por_grupo(c[d_idx, a_idx], a_idx) for c in Cs]) if Cs else None
    ex = _residuo(xz, Xc_rows)
    r = _corr(ex, EY[d_idx, a_idx])
    datas_validas = np.where(valid_d)[0]
    pos = {d: i for i, d in enumerate(datas_validas)}
    d_loc = np.array([pos[d] for d in d_idx])
    rng = np.random.default_rng(semente)
    cnt = 0
    for _ in range(n_perm):
        perm = datas_validas[rng.permutation(len(datas_validas))]
        rp = _corr(ex, EY[perm[d_loc], a_idx])
        if lado == "bi":
            cnt += abs(rp) >= abs(r)
        elif lado == "pos":
            cnt += rp >= r
        else:
            cnt += rp <= r
    from scipy import stats
    n = len(ex)
    mde = float(np.tanh((stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) / np.sqrt(n - 3)))
    return {"r": r, "p": (cnt + 1) / (n_perm + 1), "n": int(n),
            "n_datas": int(len(np.unique(d_idx))), "mde": mde, "lado": lado}


def teste_horario(x, a_idx, dia_idx, k_idx, H, desloc, n_perm=10_000, semente=42, lado="bi"):
    """
    Correlação agrupada entre o sentimento e o retorno da barra (k + desloc) do
    mesmo dia. desloc = +1 (hora DEPOIS) ou -1 (hora ANTES).
    Permutação: mesma hora em outro dia sorteado, todos os ativos juntos.
    """
    alvo = k_idx + desloc
    ok = (alvo >= 0) & (alvo < H.shape[1]) & np.isfinite(x)
    x, a_idx, dia_idx, alvo = x[ok], a_idx[ok], dia_idx[ok], alvo[ok]
    Z = H.copy()
    for j in range(H.shape[2]):           # padroniza cada ativo em todas as barras
        v = Z[:, :, j]
        Z[:, :, j] = (v - np.nanmean(v)) / np.nanstd(v, ddof=1)
    y = Z[dia_idx, alvo, a_idx]
    ok = np.isfinite(y)
    x, a_idx, dia_idx, alvo, y = x[ok], a_idx[ok], dia_idx[ok], alvo[ok], y[ok]
    xz = _z_por_grupo(x, a_idx)
    ok = np.isfinite(xz)
    xz, a_idx, dia_idx, alvo, y = xz[ok], a_idx[ok], dia_idx[ok], alvo[ok], y[ok]
    if len(xz) < 10:
        return {"erro": "amostra pequena", "n": int(len(xz))}
    r = _corr(xz, y)
    rng = np.random.default_rng(semente)
    cnt = 0
    nd = H.shape[0]
    for _ in range(n_perm):
        perm = rng.permutation(nd)
        yp = Z[perm[dia_idx], alvo, a_idx]
        m = np.isfinite(yp)
        rp = _corr(xz[m], yp[m])
        cnt += (abs(rp) >= abs(r)) if lado == "bi" else ((rp >= r) if lado == "pos" else (rp <= r))
    from scipy import stats
    n = len(xz)
    mde = float(np.tanh((stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) / np.sqrt(n - 3)))
    return {"r": r, "p": (cnt + 1) / (n_perm + 1), "n": int(n), "mde": mde, "lado": lado}


def holm(pvals: dict) -> dict:
    """Ajuste de Holm-Bonferroni. Recebe {nome: p} e devolve {nome: p_ajustado}."""
    itens = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(itens); ajust = {}; maximo = 0.0
    for i, (k, p) in enumerate(itens):
        v = min(1.0, (m - i) * p)
        maximo = max(maximo, v)
        ajust[k] = maximo
    return ajust
