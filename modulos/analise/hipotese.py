"""
hipotese.py
-----------
Testa estatisticamente a HIPÓTESE CENTRAL do TCC:

    H0 (hipótese nula):      o sentimento das notícias NÃO influencia o
                             retorno das ações. Qualquer relação observada
                             é fruto do acaso.

    H1 (hipótese alternativa): o sentimento das notícias INFLUENCIA o
                             retorno das ações.

Em estatística nunca se "prova" H1 diretamente. O que se faz é tentar
REJEITAR H0. Se a probabilidade de o resultado ter surgido por acaso
(o p-valor) for muito baixa (< 0,05), rejeitamos H0 e concluímos que
existe evidência a favor de H1.

Quatro testes são aplicados aqui:
    1. Correlação com defasagem (lag)   -> existe relação e em qual sentido?
    2. Teste t de duas amostras          -> notícia boa rende mais que notícia ruim?
    3. Event Study (retorno anormal)     -> metodologia clássica de finanças
    4. Regressão linear                  -> quanto o sentimento explica?
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List


# ─────────────────────────────────────────────────────────
# TAMANHO MÍNIMO DE AMOSTRA
# ─────────────────────────────────────────────────────────
# Este valor NÃO é arbitrário: vem da análise de poder feita em
# scripts/7_curvas_de_deteccao.py, que mede quantas observações são
# necessárias para o teste ter 80% de chance de detectar um efeito real
# (convenção de Cohen, 1988).
#
#   obs. | poder medido | poder teórico
#     20 |     —        |    32,4%      <- valor usado antes, insuficiente
#     40 |   65,7%      |    61,6%
#     60 |   82,7%      |    80,3%      <- primeiro ponto acima da meta
#    100 |   96,0%      |    95,8%
#
# Abaixo de 60 observações, um resultado NÃO significativo é ambíguo:
# não distingue "não há efeito" de "o teste não teve força para ver".
MIN_OBSERVACOES = 60


# ─────────────────────────────────────────────────────────
# 1. PREPARAÇÃO: JUNTAR SENTIMENTO COM RETORNO
# ─────────────────────────────────────────────────────────

def montar_serie_diaria(
    noticias: pd.DataFrame,
    retornos: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """
    Cria a tabela base do estudo: um registro por DIA DE PREGÃO, contendo
    o sentimento médio das notícias daquele dia e o retorno da ação.

    Args:
        noticias: precisa ter as colunas ticker, data_pregao, score_polaridade
        retornos: DataFrame do data_loader (índice = data, colunas = tickers)
        ticker: ativo a analisar

    Returns:
        DataFrame com: data, sentimento, n_noticias, retorno
    """
    # --- lado das notícias: média do sentimento por dia ---
    noti = noticias[noticias["ticker"] == ticker].copy()
    if noti.empty:
        return pd.DataFrame()

    noti["data_pregao"] = pd.to_datetime(noti["data_pregao"]).dt.normalize()

    agg = noti.groupby("data_pregao").agg(
        sentimento=("score_polaridade", "mean"),
        n_noticias=("score_polaridade", "size"),
    )

    # --- lado dos preços: retorno diário do ativo ---
    if ticker not in retornos.columns:
        return pd.DataFrame()
    ret = retornos[ticker].copy()
    ret.index = pd.to_datetime(ret.index).normalize()
    ret = ret.rename("retorno")

    # --- junção: só ficam os dias que têm notícia E pregão ---
    df = agg.join(ret, how="inner")
    df.index.name = "data"
    return df.reset_index()


def montar_serie_completa(
    noticias: pd.DataFrame,
    retornos: pd.DataFrame,
    tickers: List[str],
) -> pd.DataFrame:
    """Monta a série diária de todos os ativos empilhados num só DataFrame."""
    partes = []
    for t in tickers:
        serie = montar_serie_diaria(noticias, retornos, t)
        if not serie.empty:
            serie["ticker"] = t
            partes.append(serie)
    if not partes:
        return pd.DataFrame()
    return pd.concat(partes, ignore_index=True)


# ─────────────────────────────────────────────────────────
# 2. TESTE 1 — CORRELAÇÃO COM DEFASAGEM (LAG)
# ─────────────────────────────────────────────────────────

def testar_correlacao_defasada(
    serie: pd.DataFrame,
    lags: List[int] = [0, 1, 2, 3, 5],
) -> pd.DataFrame:
    """
    Mede a correlação entre o sentimento do dia D e o retorno em D+lag.

    Por que testar vários lags?
        lag = 0 -> o mercado reage no MESMO dia (mercado eficiente)
        lag = 1 -> a reação aparece no dia SEGUINTE (é o caso mais comum,
                   pois muita notícia sai fora do horário de pregão)
        lag > 2 -> se houver correlação alta aqui, é sinal de reação lenta

    Usa duas medidas:
        Pearson  -> relação LINEAR (sensível a outliers)
        Spearman -> relação de ORDEM (mais robusta, não exige linearidade)

    Returns:
        DataFrame com r, p-valor e significância para cada lag
    """
    resultados = []

    for lag in lags:
        s = serie.copy().sort_values("data")
        # Desloca o retorno para trás: linha do dia D passa a ter o retorno de D+lag
        s["retorno_lag"] = s["retorno"].shift(-lag)
        s = s.dropna(subset=["sentimento", "retorno_lag"])

        if len(s) < 10:
            continue

        r_p, p_p = stats.pearsonr(s["sentimento"], s["retorno_lag"])
        r_s, p_s = stats.spearmanr(s["sentimento"], s["retorno_lag"])

        resultados.append({
            "lag_dias": lag,
            "n_observacoes": len(s),
            "pearson_r": round(r_p, 4),
            "pearson_p": round(p_p, 4),
            "spearman_r": round(r_s, 4),
            "spearman_p": round(p_s, 4),
            "significativo_5pct": p_p < 0.05,
        })

    return pd.DataFrame(resultados)


# ─────────────────────────────────────────────────────────
# 3. TESTE 2 — COMPARAÇÃO DE MÉDIAS (TESTE t)
# ─────────────────────────────────────────────────────────

def testar_diferenca_medias(
    serie: pd.DataFrame,
    lag: int = 1,
    limiar: float = 0.2,
) -> Dict:
    """
    Separa os dias em dois grupos e compara o retorno médio de cada um.

        Grupo A: dias com sentimento POSITIVO (score >  +limiar)
        Grupo B: dias com sentimento NEGATIVO (score <  -limiar)

    Aplica o teste t de Welch (não assume variâncias iguais, é o mais seguro).

    Interpretação:
        p < 0,05  -> a diferença entre os grupos é estatisticamente
                     significativa; rejeitamos H0.
        p >= 0,05 -> não há evidência suficiente; não rejeitamos H0.

    Também calcula o d de Cohen (tamanho do efeito):
        |d| < 0,2 -> efeito desprezível
        0,2-0,5   -> efeito pequeno
        0,5-0,8   -> efeito médio
        > 0,8     -> efeito grande
    """
    s = serie.copy().sort_values("data")
    s["retorno_lag"] = s["retorno"].shift(-lag)
    s = s.dropna(subset=["sentimento", "retorno_lag"])

    pos = s.loc[s["sentimento"] > limiar, "retorno_lag"]
    neg = s.loc[s["sentimento"] < -limiar, "retorno_lag"]

    if len(pos) < 5 or len(neg) < 5:
        return {
            "erro": "Amostra insuficiente (mínimo 5 dias em cada grupo)",
            "n_positivo": len(pos),
            "n_negativo": len(neg),
        }

    t_stat, p_valor = stats.ttest_ind(pos, neg, equal_var=False)

    # d de Cohen com desvio-padrão combinado
    n1, n2 = len(pos), len(neg)
    dp_comb = np.sqrt(
        ((n1 - 1) * pos.var(ddof=1) + (n2 - 1) * neg.var(ddof=1)) / (n1 + n2 - 2)
    )
    d_cohen = (pos.mean() - neg.mean()) / dp_comb if dp_comb > 0 else 0.0

    if abs(d_cohen) < 0.2:
        magnitude = "Desprezível"
    elif abs(d_cohen) < 0.5:
        magnitude = "Pequeno"
    elif abs(d_cohen) < 0.8:
        magnitude = "Médio"
    else:
        magnitude = "Grande"

    return {
        "lag_dias": lag,
        "n_positivo": n1,
        "n_negativo": n2,
        "retorno_medio_apos_noticia_positiva_pct": round(pos.mean() * 100, 4),
        "retorno_medio_apos_noticia_negativa_pct": round(neg.mean() * 100, 4),
        "diferenca_pct": round((pos.mean() - neg.mean()) * 100, 4),
        "estatistica_t": round(t_stat, 4),
        "p_valor": round(p_valor, 4),
        "significativo_5pct": bool(p_valor < 0.05),
        "d_cohen": round(d_cohen, 4),
        "magnitude_efeito": magnitude,
    }


# ─────────────────────────────────────────────────────────
# 4. TESTE 3 — EVENT STUDY (RETORNO ANORMAL)
# ─────────────────────────────────────────────────────────

def calcular_retorno_anormal(
    retornos_ativo: pd.Series,
    retornos_mercado: pd.Series,
    janela_estimacao: int = 120,
) -> pd.DataFrame:
    """
    Calcula o RETORNO ANORMAL (AR) usando o Modelo de Mercado.

    A ideia central do Event Study (MacKinlay, 1997):
        Parte do movimento da ação vem do mercado inteiro (o Ibovespa subiu,
        então quase tudo subiu). Isso NÃO é efeito da notícia.

        Primeiro estimamos o retorno ESPERADO da ação em função do mercado:
            R_esperado = alfa + beta * R_mercado

        O que sobra é o retorno ANORMAL — o pedaço não explicado pelo mercado:
            AR = R_real - R_esperado

        Se a notícia realmente influencia o preço, o AR deve ser
        sistematicamente positivo após notícia boa e negativo após ruim.

    Args:
        janela_estimacao: nº de dias usados para estimar alfa e beta
    """
    df = pd.DataFrame({
        "ativo": retornos_ativo,
        "mercado": retornos_mercado,
    }).dropna()

    if len(df) < janela_estimacao + 20:
        raise ValueError(
            f"Histórico insuficiente: {len(df)} dias "
            f"(mínimo {janela_estimacao + 20})"
        )

    # Estima alfa e beta na janela inicial (antes do período analisado),
    # evitando que os próprios eventos contaminem a estimativa.
    est = df.iloc[:janela_estimacao]
    beta, alfa, r_valor, _, _ = stats.linregress(est["mercado"], est["ativo"])

    df["retorno_esperado"] = alfa + beta * df["mercado"]
    df["retorno_anormal"] = df["ativo"] - df["retorno_esperado"]

    df.attrs["alfa"] = alfa
    df.attrs["beta"] = beta
    df.attrs["r2_modelo"] = r_valor ** 2
    return df


def event_study(
    noticias: pd.DataFrame,
    retornos_ativo: pd.Series,
    retornos_mercado: pd.Series,
    ticker: str,
    limiar: float = 0.3,
    janela: int = 3,
) -> Dict:
    """
    Executa o Event Study completo.

    Para cada notícia forte (positiva ou negativa), acumula o retorno anormal
    numa janela de +/- N dias em torno do evento (o CAR — Cumulative
    Abnormal Return) e testa se a média dos CARs é diferente de zero.

    Se o CAR médio após notícia positiva for > 0 com p < 0,05, temos
    evidência formal de que a notícia moveu o preço além do mercado.
    """
    ar = calcular_retorno_anormal(retornos_ativo, retornos_mercado)
    ar.index = pd.to_datetime(ar.index).normalize()

    noti = noticias[noticias["ticker"] == ticker].copy()
    if noti.empty:
        return {"erro": f"Sem notícias para {ticker}"}

    noti["data_pregao"] = pd.to_datetime(noti["data_pregao"]).dt.normalize()
    # Sentimento consolidado do dia
    diario = noti.groupby("data_pregao")["score_polaridade"].mean()

    datas_ar = ar.index
    cars_pos, cars_neg = [], []

    for data_evento, score in diario.items():
        if abs(score) < limiar:
            continue  # notícia fraca/neutra, ignora

        # Localiza a posição do evento no calendário de pregões
        pos = datas_ar.searchsorted(data_evento)
        if pos <= janela or pos >= len(datas_ar) - janela:
            continue  # sem janela completa disponível

        trecho = ar["retorno_anormal"].iloc[pos: pos + janela + 1]
        car = float(trecho.sum())  # retorno anormal acumulado

        (cars_pos if score > 0 else cars_neg).append(car)

    resultado = {
        "ticker": ticker,
        "beta_estimado": round(ar.attrs["beta"], 4),
        "alfa_estimado": round(ar.attrs["alfa"], 6),
        "r2_modelo_mercado": round(ar.attrs["r2_modelo"], 4),
        "janela_dias": janela,
        "n_eventos_positivos": len(cars_pos),
        "n_eventos_negativos": len(cars_neg),
    }

    # Teste t de uma amostra: o CAR médio é diferente de zero?
    if len(cars_pos) >= 5:
        t, p = stats.ttest_1samp(cars_pos, 0)
        resultado.update({
            "car_medio_positivo_pct": round(np.mean(cars_pos) * 100, 4),
            "p_valor_positivo": round(p, 4),
            "significativo_positivo": bool(p < 0.05),
        })

    if len(cars_neg) >= 5:
        t, p = stats.ttest_1samp(cars_neg, 0)
        resultado.update({
            "car_medio_negativo_pct": round(np.mean(cars_neg) * 100, 4),
            "p_valor_negativo": round(p, 4),
            "significativo_negativo": bool(p < 0.05),
        })

    return resultado


# ─────────────────────────────────────────────────────────
# 5. TESTE 4 — REGRESSÃO LINEAR
# ─────────────────────────────────────────────────────────

def regressao_sentimento_retorno(serie: pd.DataFrame, lag: int = 1) -> Dict:
    """
    Ajusta a reta:  retorno = a + b * sentimento

    O coeficiente b indica o quanto o retorno varia para cada ponto de
    sentimento. O R² indica QUANTO da variação do preço é explicada
    pelo sentimento.

    Atenção honesta para a defesa do TCC:
        R² baixo (0,01 a 0,10) é o NORMAL nesta literatura. O preço de uma
        ação depende de dezenas de fatores. Encontrar 3% de explicação vinda
        só do sentimento já é um resultado relevante — e não invalida a
        hipótese. O que importa é o p-valor do coeficiente.
    """
    s = serie.copy().sort_values("data")
    s["retorno_lag"] = s["retorno"].shift(-lag)
    s = s.dropna(subset=["sentimento", "retorno_lag"])

    if len(s) < MIN_OBSERVACOES:
        return {
            "erro": (
                f"Amostra insuficiente ({len(s)} obs., mínimo {MIN_OBSERVACOES}). "
                f"Abaixo disso o teste tem menos de 80% de poder."
            )
        }

    b, a, r, p, erro_padrao = stats.linregress(s["sentimento"], s["retorno_lag"])

    return {
        "lag_dias": lag,
        "n_observacoes": len(s),
        "coeficiente_angular_b": round(b, 6),
        "intercepto_a": round(a, 6),
        "r": round(r, 4),
        "r2": round(r ** 2, 4),
        "variancia_explicada_pct": round(r ** 2 * 100, 2),
        "p_valor": round(p, 4),
        "erro_padrao": round(erro_padrao, 6),
        "significativo_5pct": bool(p < 0.05),
        "interpretacao": (
            f"Cada +1 ponto de sentimento associa-se a "
            f"{b * 100:+.3f}% de retorno em D+{lag}"
        ),
    }


# ─────────────────────────────────────────────────────────
# 6. RELATÓRIO CONSOLIDADO
# ─────────────────────────────────────────────────────────

def gerar_relatorio(
    noticias: pd.DataFrame,
    retornos: pd.DataFrame,
    retornos_mercado: pd.Series,
    tickers: List[str],
    lag_principal: int = 1,
) -> Dict:
    """
    Roda todos os testes para todos os ativos e monta o veredito final
    da hipótese do TCC.
    """
    relatorio = {"por_ativo": {}, "consolidado": {}}
    p_valores, evidencias = [], 0

    for ticker in tickers:
        serie = montar_serie_diaria(noticias, retornos, ticker)
        if serie.empty or len(serie) < 20:
            relatorio["por_ativo"][ticker] = {"erro": "Dados insuficientes"}
            continue

        bloco = {
            "n_dias_com_noticia": len(serie),
            "correlacao_defasada": testar_correlacao_defasada(serie).to_dict("records"),
            "teste_medias": testar_diferenca_medias(serie, lag=lag_principal),
            "regressao": regressao_sentimento_retorno(serie, lag=lag_principal),
        }

        if ticker in retornos.columns:
            try:
                bloco["event_study"] = event_study(
                    noticias, retornos[ticker], retornos_mercado, ticker
                )
            except Exception as e:
                bloco["event_study"] = {"erro": str(e)}

        # Contabiliza evidências a favor de H1
        reg = bloco["regressao"]
        if reg.get("significativo_5pct"):
            evidencias += 1
            p_valores.append(reg["p_valor"])

        relatorio["por_ativo"][ticker] = bloco

    n_testados = sum(
        1 for v in relatorio["por_ativo"].values() if "erro" not in v
    )

    relatorio["consolidado"] = {
        "ativos_analisados": n_testados,
        "ativos_com_relacao_significativa": evidencias,
        "p_valor_medio": round(float(np.mean(p_valores)), 4) if p_valores else None,
        "veredito": _veredito(evidencias, n_testados),
    }
    return relatorio


def _veredito(evidencias: int, total: int) -> str:
    """Traduz os números em uma conclusão redigida para o TCC."""
    if total == 0:
        return "Inconclusivo: não houve dados suficientes para testar a hipótese."

    proporcao = evidencias / total

    if proporcao >= 0.6:
        return (
            f"H0 REJEITADA em {evidencias} de {total} ativos (p < 0,05). "
            "Há evidência estatística consistente de que o sentimento das "
            "notícias influencia o retorno das ações analisadas."
        )
    if proporcao >= 0.3:
        return (
            f"H0 rejeitada em {evidencias} de {total} ativos. Evidência PARCIAL: "
            "o efeito existe em parte da amostra, sugerindo que a influência "
            "do sentimento varia conforme o ativo e sua cobertura na mídia."
        )
    return (
        f"H0 NÃO rejeitada na maioria dos casos ({evidencias} de {total}). "
        "Não houve evidência estatística suficiente no período analisado. "
        "Isso é um resultado válido e deve ser reportado com honestidade."
    )


def imprimir_relatorio(relatorio: Dict) -> None:
    """Imprime o relatório formatado no terminal."""
    print("\n" + "=" * 68)
    print("  VALIDAÇÃO DA HIPÓTESE — SENTIMENTO x RETORNO DAS AÇÕES")
    print("=" * 68)

    for ticker, bloco in relatorio["por_ativo"].items():
        print(f"\n▸ {ticker}")
        if "erro" in bloco:
            print(f"    {bloco['erro']}")
            continue

        print(f"    Dias com notícia: {bloco['n_dias_com_noticia']}")

        reg = bloco.get("regressao", {})
        if "erro" not in reg:
            marca = "SIM" if reg["significativo_5pct"] else "não"
            print(f"    Regressão  : R² = {reg['r2']:.4f} | "
                  f"p = {reg['p_valor']:.4f} | significativo: {marca}")

        tm = bloco.get("teste_medias", {})
        if "erro" not in tm:
            print(f"    Teste t    : notícia boa {tm['retorno_medio_apos_noticia_positiva_pct']:+.3f}% "
                  f"vs ruim {tm['retorno_medio_apos_noticia_negativa_pct']:+.3f}% | "
                  f"p = {tm['p_valor']:.4f}")

        ev = bloco.get("event_study", {})
        if ev and "erro" not in ev:
            if "car_medio_positivo_pct" in ev:
                print(f"    CAR (+)    : {ev['car_medio_positivo_pct']:+.3f}% "
                      f"em {ev['n_eventos_positivos']} eventos | "
                      f"p = {ev['p_valor_positivo']:.4f}")
            if "car_medio_negativo_pct" in ev:
                print(f"    CAR (−)    : {ev['car_medio_negativo_pct']:+.3f}% "
                      f"em {ev['n_eventos_negativos']} eventos | "
                      f"p = {ev['p_valor_negativo']:.4f}")

    c = relatorio["consolidado"]
    print("\n" + "-" * 68)
    print("  CONCLUSÃO")
    print("-" * 68)
    print(f"  Ativos analisados            : {c['ativos_analisados']}")
    print(f"  Com relação significativa    : {c['ativos_com_relacao_significativa']}")
    if c["p_valor_medio"] is not None:
        print(f"  p-valor médio                : {c['p_valor_medio']}")
    print(f"\n  {c['veredito']}")
    print("=" * 68 + "\n")
