# -*- coding: utf-8 -*-
"""
minuto.py — barras intradiárias (1 ou 5 minutos) e eventos com horário exato.

Usado pelas janelas curtas da Fase G (scripts/40_janelas_curtas.py).
O piloto de 30 minutos (scripts/37_piloto_minuto.py) tem a mesma lógica
escrita dentro dele e não foi alterado.

    painel()          R[d, k, a] = log-retorno da barra k do dia d do ativo a
                      (fechamento contra o fechamento anterior do MESMO dia;
                      na 1ª barra do dia, contra a abertura) e o retorno
                      anormal A = R - média dos outros ativos (beta = 1)
    janela()          soma de A em várias barras seguidas, a partir da barra k
    noticias_exatas() notícias do estudo + coleta recente com o horário exato
    eventos()         um evento por (ativo, dia, barra), com a média do sentimento
"""
from pathlib import Path

import numpy as np
import pandas as pd

from modulos.analise.filtro_relato import eh_relato_de_preco
from modulos.analise.fuso import ajustar_pregao_brasilia
from modulos.analise.horarios import filtrar_wordpress
from modulos.analise.validacao_lexico import tirar_fonte
from modulos.analise import modelos

RAIZ = Path(__file__).resolve().parent.parent.parent
FUSO = "America/Sao_Paulo"


def painel(ativos, intervalo, inicio_min, fim_min, passo):
    """Lê dados/minuto/<ativo>_<intervalo>.csv. Devolve (dias, R, A)."""
    n_slots = (fim_min - inicio_min) // passo
    series = {}
    for t in ativos:
        d = pd.read_csv(RAIZ / "dados" / "minuto" / f"{t}_{intervalo}.csv")
        hora = pd.to_datetime(d["Datetime"], utc=True).dt.tz_convert(FUSO).dt.tz_localize(None)
        d = d.assign(dia=hora.dt.normalize(), minuto=hora.dt.hour * 60 + hora.dt.minute)
        d = d[(d["minuto"] >= inicio_min) & (d["minuto"] < fim_min) & (d["minuto"] % passo == 0)]
        d = d.sort_values(["dia", "minuto"])
        ant = d.groupby("dia")["Close"].shift(1)
        d["r"] = np.log(d["Close"] / ant.where(ant.notna(), d["Open"]))
        d["k"] = (d["minuto"] - inicio_min) // passo
        series[t] = d.set_index(["dia", "k"])["r"]
    pan = pd.DataFrame(series)
    dias = sorted(pan.index.get_level_values(0).unique())
    pan = pan.reindex(pd.MultiIndex.from_product([dias, range(n_slots)]))
    R = pan.to_numpy().reshape(len(dias), n_slots, len(ativos))
    soma = np.nansum(R, axis=2, keepdims=True)
    cnt = np.sum(~np.isnan(R), axis=2, keepdims=True)
    A = R - (soma - np.nan_to_num(R)) / np.maximum(cnt - 1, 1)
    return dias, R, A


def janela(A, desloc_ini, n):
    """W[d, k, a] = soma de A nas barras k+desloc_ini ... k+desloc_ini+n-1.
    NaN se a janela sair do pregão ou se faltar alguma barra."""
    W = np.full_like(A, np.nan)
    n_slots = A.shape[1]
    for k in range(n_slots):
        ini, fim = k + desloc_ini, k + desloc_ini + n
        if ini >= 0 and fim <= n_slots:
            W[:, k, :] = A[:, ini:fim, :].sum(axis=1)
    return W


def noticias_exatas(ativos):
    """Notícias do estudo + coleta recente, com t_google (hora real) e t_wp
    (WordPress com o filtro de data do adendo 1 da fase causal)."""
    can = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv")
    rec = pd.read_csv(RAIZ / "dados" / "prospectivo" / "noticias_recentes.csv")
    n = pd.concat([can, rec], ignore_index=True)
    n = ajustar_pregao_brasilia(n[n["ticker"].isin(ativos)].copy())
    wp = pd.concat([pd.read_csv(RAIZ / "dados" / "horarios_wordpress.csv"),
                    pd.read_csv(RAIZ / "dados" / "prospectivo" / "horarios_wordpress_recentes.csv")],
                   ignore_index=True)
    n = n.merge(filtrar_wordpress(n, wp).drop_duplicates("url"), on="url", how="left")
    n["t_google"] = n["data_brasilia"].where(n["hora_real"])
    n["t_wp"] = n["t_wp_filtrado"]
    n["manchete"] = [tirar_fonte(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    n["relato"] = n["titulo"].map(eh_relato_de_preco)
    return n


def eventos(n, ativos, dias, inicio_min, passo, t_ini_min, t_fim_min,
            medida="lexico", prioridade="google", rng_embaralhar=None):
    """Um evento por (ativo, dia, barra da publicação), com a média do sentimento."""
    q = modelos.aplicar(n, medida) if medida != "lexico" else n.copy()
    if prioridade == "google":
        q["t"] = q["t_google"].fillna(q["t_wp"])
    else:
        q["t"] = q["t_wp"].fillna(q["t_google"])
    q = q.dropna(subset=["t"]).sort_values("t").drop_duplicates(["ticker", "manchete"], keep="first")
    minuto = q["t"].dt.hour * 60 + q["t"].dt.minute
    dpos = {d: i for i, d in enumerate(dias)}
    dia = q["t"].dt.normalize()
    q = q[(q["t"].dt.weekday < 5) & (minuto >= t_ini_min) & (minuto < t_fim_min) & dia.isin(dpos)].copy()
    q["d"] = q["t"].dt.normalize().map(dpos).astype(int)
    q["k"] = ((q["t"].dt.hour * 60 + q["t"].dt.minute) - inicio_min) // passo
    q["a"] = q["ticker"].map({t: i for i, t in enumerate(ativos)})
    g = q.groupby(["a", "d", "k"]).agg(x=("score_polaridade", "mean"), relato=("relato", "max")).reset_index()
    if rng_embaralhar is not None:
        g["x"] = rng_embaralhar.permutation(g["x"].to_numpy())
    return g
