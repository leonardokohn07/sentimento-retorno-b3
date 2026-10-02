# -*- coding: utf-8 -*-
"""
fuso.py — horário das notícias convertido para o horário de Brasília.

POR QUE ESTE MÓDULO EXISTE (descoberto em 01/10/2026)

  1. O feedparser entrega `published_parsed` em UTC. A coleta gravava esse
     UTC direto na coluna `data`, e `ajustar_data_pregao` aplicava a regra
     "publicada depois das 17h vale para o pregão seguinte" sobre o UTC — que
     está 3 horas à frente de Brasília. Uma notícia das 15h de Brasília
     (18h UTC) era empurrada para o dia seguinte. No arquivo do estudo, 177
     notícias com horário real, publicadas entre 14h e 17h de Brasília em dia
     útil, foram deslocadas para o pregão seguinte.

  2. Os registros SEM horário real chegam todos com 07:00:00 ou 08:00:00 UTC.
     É meia-noite no fuso do Pacífico (EUA): 07h UTC de março a novembro e
     08h UTC no resto do ano, exatamente o horário de verão americano. Para
     esses registros a hora não carrega informação nenhuma; vale só a data.

  Este módulo NÃO altera o arquivo de notícias. Ele recalcula `data_pregao`
  na hora da análise, para que o resultado publicado continue reproduzível.
"""
import pandas as pd

FUSO_BR = "America/Sao_Paulo"
HORA_FECHAMENTO = 17          # mesma convenção do estudo original
HORAS_FICTICIAS = (7, 8)      # meia-noite do Pacífico, em UTC


def tem_hora_real(datas_utc: pd.Series) -> pd.Series:
    """True quando o horário veio de verdade, e não o 07:00/08:00 fictício."""
    d = pd.to_datetime(datas_utc)
    ficticia = d.dt.hour.isin(HORAS_FICTICIAS) & (d.dt.minute == 0) & (d.dt.second == 0)
    return ~ficticia


def para_brasilia(datas_utc: pd.Series) -> pd.Series:
    """Converte datas UTC sem fuso para o horário de Brasília, sem fuso."""
    d = pd.to_datetime(datas_utc)
    return d.dt.tz_localize("UTC").dt.tz_convert(FUSO_BR).dt.tz_localize(None)


def ajustar_pregao_brasilia(noticias: pd.DataFrame,
                            hora_fechamento: int = HORA_FECHAMENTO) -> pd.DataFrame:
    """
    Recalcula `data_pregao` com o horário de Brasília.

    - Notícia COM hora real: converte UTC -> Brasília; se saiu às 17h ou
      depois, vale para o pregão seguinte.
    - Notícia SEM hora real: mantém a data gravada (igual ao estudo original).
    - Sábado e domingo vão para a segunda-feira.

    Acrescenta as colunas `hora_real` (bool) e `data_brasilia`.
    """
    df = noticias.copy()
    utc = pd.to_datetime(df["data"])
    df["hora_real"] = tem_hora_real(utc)
    local = para_brasilia(utc)
    df["data_brasilia"] = local.where(df["hora_real"], utc.dt.normalize())

    pregao = df["data_brasilia"].dt.normalize()
    apos = df["hora_real"] & (df["data_brasilia"].dt.hour >= hora_fechamento)
    pregao = pregao.where(~apos, pregao + pd.Timedelta(days=1))
    ate_segunda = pregao.dt.weekday.map({5: 2, 6: 1}).fillna(0)
    df["data_pregao"] = pregao + pd.to_timedelta(ate_segunda, unit="D")
    return df
