# -*- coding: utf-8 -*-
"""
horarios.py — horário exato de publicação das notícias.

Junta as duas fontes de horário do projeto, na ordem de prioridade fixada
no pré-registro da fase causal e no adendo 1:
    1. a hora real do Google (quando não é o 07:00/08:00 UTC fictício);
    2. a hora da API WordPress do site, só quando a DATA bate (filtro do
       adendo 1): notícia com hora real -> mesmo dia em Brasília; notícia só
       com data (meia-noite do Pacífico) -> mesmo dia ou o seguinte.
       Sem esse filtro, títulos parecidos de outros dias casavam errado.
"""
import pandas as pd

from modulos.analise.fuso import FUSO_BR, ajustar_pregao_brasilia


def wordpress_em_brasilia(wp: pd.DataFrame) -> pd.DataFrame:
    """Linhas achadas (status ok) com a hora oficial convertida para Brasília."""
    w = wp[wp["status"] == "ok"].dropna(subset=["wp_date_gmt"]).copy()
    w["t_wp"] = (pd.to_datetime(w["wp_date_gmt"], utc=True, errors="coerce")
                 .dt.tz_convert(FUSO_BR).dt.tz_localize(None))
    return w.dropna(subset=["t_wp"]).drop_duplicates("url")[["url", "t_wp"]]


def filtrar_wordpress(noticias: pd.DataFrame, wp: pd.DataFrame) -> pd.DataFrame:
    """Horários do WordPress que passam no filtro de data do adendo 1.

    noticias: precisa de url e data (UTC, como no arquivo de notícias).
    Devolve url e t_wp_filtrado (horário de Brasília, sem fuso).
    """
    n = noticias.drop_duplicates("url").copy()
    if "hora_real" not in n.columns:
        n = ajustar_pregao_brasilia(n)
    m = n[["url", "hora_real", "data_brasilia"]].merge(wordpress_em_brasilia(wp), on="url")
    dia_wp = m["t_wp"].dt.normalize()
    dia_g = m["data_brasilia"].dt.normalize()
    ok_real = m["hora_real"] & (dia_wp == dia_g)
    ok_data = ~m["hora_real"] & ((dia_wp == dia_g) | (dia_wp == dia_g + pd.Timedelta(days=1)))
    m = m[ok_real | ok_data]
    return m[["url", "t_wp"]].rename(columns={"t_wp": "t_wp_filtrado"}).reset_index(drop=True)


def horario_exato(noticias: pd.DataFrame, wp_filtrado: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta t_exato (Brasília) e fonte_hora ('google', 'wordpress' ou vazio)."""
    df = noticias.copy()
    if "hora_real" not in df.columns:
        df = ajustar_pregao_brasilia(df)
    df = df.merge(wp_filtrado.drop_duplicates("url"), on="url", how="left")
    df["t_exato"] = df["data_brasilia"].where(df["hora_real"])
    usa_wp = df["t_exato"].isna() & df["t_wp_filtrado"].notna()
    df.loc[usa_wp, "t_exato"] = df.loc[usa_wp, "t_wp_filtrado"]
    df["fonte_hora"] = ""
    df.loc[df["hora_real"], "fonte_hora"] = "google"
    df.loc[usa_wp, "fonte_hora"] = "wordpress"
    return df.drop(columns=["t_wp_filtrado"])
