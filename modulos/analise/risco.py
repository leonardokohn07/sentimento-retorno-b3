"""
risco.py
--------
Análise de risco de carteira de investimentos.

Calcula: Volatilidade, Beta, VaR, Sharpe, Correlação,
Fronteira Eficiente (Markowitz) e um perfil de risco qualitativo.

NOTA METODOLÓGICA — por que aqui não existe nota de 0 a 100
    (decisão de 15/09/2026, registrada no caderno de campo)

    Este módulo já devolveu um "score de risco" de 0 a 100. Ele saiu.
    O número era montado a partir de limiares que eu mesmo escolhi, e
    a escala resultante não tinha significado: não dava para dizer o
    que separava um 48 de um 52, nem o que 100 representaria.

    Sobrou o que é defensável: a CONTAGEM DE PONTOS, que é só o número
    de critérios de risco acionados, e a FAIXA qualitativa que ela
    define. Cada ponto é rastreável até a métrica que o gerou e
    aparece escrito em 'detalhes' — o usuário lê o motivo, não a nota.

    Também não se usa classificador supervisionado aqui, por um motivo
    anterior: treinar um exigiria um rótulo de "risco real", e esse
    rótulo não existe de forma objetiva. Risco é uma construção, não
    um fato observável no histórico de preços.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


# ─────────────────────────────────────────────
# 0. PARÂMETRO DE MERCADO
# ─────────────────────────────────────────────
# Taxa livre de risco usada no Índice Sharpe e na otimização de Markowitz.
#
# Referência: Selic meta definida pelo Copom em 05/08/2026 = 14,00% a.a.
# (Banco Central do Brasil). Ao longo de 2026 a taxa caiu 15,00 -> 14,75 ->
# 14,50 -> 14,25 -> 14,00.
#
# ATENÇÃO: este é um parâmetro de mercado, não uma constante física.
# Confira a Selic vigente antes de gerar resultados para o TCC e atualize
# AQUI — os dois usos do módulo leem desta variável.
#
# Rigor metodológico: o ideal é usar a Selic MÉDIA do período analisado,
# não a taxa spot, já que o Sharpe é calculado sobre a série histórica.
TAXA_LIVRE_RISCO_ANUAL = 0.14


# ─────────────────────────────────────────────
# 1. MÉTRICAS BÁSICAS DE RISCO
# ─────────────────────────────────────────────

def calcular_volatilidade(retornos: pd.Series, anualizar: bool = True) -> float:
    """
    Volatilidade (desvio padrão dos retornos).
    Anualizada: multiplica por sqrt(252) dias úteis.
    """
    vol = retornos.std()
    return vol * np.sqrt(252) if anualizar else vol


def calcular_beta(retornos_ativo: pd.Series, retornos_mercado: pd.Series) -> float:
    """
    Beta: sensibilidade do ativo em relação ao mercado (Ibovespa).
    Beta > 1 = mais volátil que o mercado.
    Beta < 1 = menos volátil que o mercado.
    """
    retornos_alinhados = pd.concat([retornos_ativo, retornos_mercado], axis=1).dropna()
    cov = np.cov(retornos_alinhados.iloc[:, 0], retornos_alinhados.iloc[:, 1])
    return cov[0, 1] / cov[1, 1]


def calcular_var(
    retornos: pd.Series,
    confianca: float = 0.95,
    horizonte: int = 1,
    valor_investido: float = 10000.0
) -> Dict:
    """
    Value at Risk (VaR) — perda máxima esperada com certa confiança.

    Args:
        confianca: 0.95 = 95% de confiança
        horizonte: dias à frente
        valor_investido: valor em R$ para calcular perda em reais

    Returns:
        VaR histórico e paramétrico
    """
    # VaR Histórico
    var_hist = np.percentile(retornos, (1 - confianca) * 100)

    # VaR Paramétrico (assume normalidade)
    from scipy.stats import norm
    var_param = norm.ppf(1 - confianca, retornos.mean(), retornos.std())

    # Ajuste para horizonte
    var_hist_h = var_hist * np.sqrt(horizonte)
    var_param_h = var_param * np.sqrt(horizonte)

    return {
        "var_historico_pct": round(var_hist_h * 100, 2),
        "var_parametrico_pct": round(var_param_h * 100, 2),
        "var_historico_brl": round(var_hist_h * valor_investido, 2),
        "var_parametrico_brl": round(var_param_h * valor_investido, 2),
        "confianca": confianca,
        "horizonte_dias": horizonte,
    }


def calcular_sharpe(
    retornos: pd.Series,
    taxa_livre_risco_anual: float = TAXA_LIVRE_RISCO_ANUAL
) -> float:
    """
    Índice Sharpe: retorno ajustado pelo risco.
    Sharpe > 1 é considerado bom.
    """
    taxa_diaria = taxa_livre_risco_anual / 252
    excesso = retornos - taxa_diaria
    if excesso.std() == 0:
        return 0.0
    return round((excesso.mean() / excesso.std()) * np.sqrt(252), 3)


def calcular_max_drawdown(precos: pd.Series) -> Dict:
    """
    Máxima queda do pico até o vale (drawdown).
    """
    pico = precos.cummax()
    drawdown = (precos - pico) / pico
    max_dd = drawdown.min()
    data_pico = precos[:drawdown.idxmin()].idxmax()
    data_vale = drawdown.idxmin()
    return {
        "max_drawdown_pct": round(max_dd * 100, 2),
        "data_pico": str(data_pico)[:10],
        "data_vale": str(data_vale)[:10],
    }


# ─────────────────────────────────────────────
# 2. ANÁLISE DE CARTEIRA
# ─────────────────────────────────────────────

def calcular_metricas_carteira(
    retornos: pd.DataFrame,
    pesos: Dict[str, float],
    retornos_ibov: Optional[pd.Series] = None,
) -> Dict:
    """
    Calcula métricas completas para uma carteira com pesos definidos.
    """
    tickers = list(pesos.keys())

    # Alinha os tickers disponíveis — um ativo pedido pode não ter vindo do
    # yfinance, e os pesos precisam ser renormalizados sobre os que vieram
    # para continuarem somando 1
    ret_disp = retornos[[t for t in tickers if t in retornos.columns]].dropna()
    w_disp = np.array([pesos[t] for t in tickers if t in ret_disp.columns])
    w_disp = w_disp / w_disp.sum()  # renormaliza

    # Retorno e risco da carteira
    retorno_carteira = ret_disp.dot(w_disp)
    retorno_anual = retorno_carteira.mean() * 252

    # Matriz de covariância e correlação
    matriz_cov = ret_disp.cov() * 252
    matriz_corr = ret_disp.corr()

    # Risco da carteira via matriz de covariância
    var_carteira = float(w_disp @ matriz_cov.values @ w_disp)
    vol_carteira = np.sqrt(var_carteira)

    metricas = {
        "retorno_anual_pct": round(retorno_anual * 100, 2),
        "volatilidade_anual_pct": round(vol_carteira * 100, 2),
        "sharpe": calcular_sharpe(retorno_carteira),
        "var_95": calcular_var(retorno_carteira),
        "max_drawdown": calcular_max_drawdown((1 + retorno_carteira).cumprod()),
        "matriz_correlacao": matriz_corr,
        "matriz_covariancia": matriz_cov,
        "retorno_diario": retorno_carteira,
    }

    # Beta da carteira em relação ao Ibovespa
    if retornos_ibov is not None:
        metricas["beta_carteira"] = round(
            calcular_beta(retorno_carteira, retornos_ibov), 3
        )

    return metricas


def calcular_metricas_individuais(
    retornos: pd.DataFrame,
    dados_precos: Dict,
    retornos_ibov: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Tabela de métricas individuais para cada ativo da carteira.
    """
    resultados = []
    for ticker in retornos.columns:
        ret = retornos[ticker].dropna()
        linha = {
            "ticker": ticker,
            "retorno_anual_pct": round(ret.mean() * 252 * 100, 2),
            "volatilidade_anual_pct": round(calcular_volatilidade(ret) * 100, 2),
            "sharpe": calcular_sharpe(ret),
            "var_95_pct": calcular_var(ret)["var_historico_pct"],
        }
        if retornos_ibov is not None:
            linha["beta"] = round(calcular_beta(ret, retornos_ibov), 3)
        if ticker in dados_precos:
            precos = dados_precos[ticker]["Close"]
            dd = calcular_max_drawdown(precos)
            linha["max_drawdown_pct"] = dd["max_drawdown_pct"]
        resultados.append(linha)

    return pd.DataFrame(resultados).set_index("ticker")


# ─────────────────────────────────────────────
# 3. OTIMIZAÇÃO DE MARKOWITZ
# ─────────────────────────────────────────────

def otimizar_carteira(
    retornos: pd.DataFrame,
    n_simulacoes: int = 5000,
    taxa_livre_risco: float = TAXA_LIVRE_RISCO_ANUAL
) -> Dict:
    """
    Simulação de Monte Carlo + Fronteira Eficiente de Markowitz.

    Returns:
        Dicionário com portfólios simulados e portfólio de máximo Sharpe
    """
    n_ativos = retornos.shape[1]
    tickers = retornos.columns.tolist()

    ret_medios = retornos.mean() * 252
    cov_matrix = retornos.cov() * 252

    resultados = np.zeros((3, n_simulacoes))
    pesos_simulados = []

    for i in range(n_simulacoes):
        w = np.random.dirichlet(np.ones(n_ativos))
        ret = np.dot(w, ret_medios)
        vol = np.sqrt(w @ cov_matrix.values @ w)
        sharpe = (ret - taxa_livre_risco) / vol
        resultados[0, i] = ret
        resultados[1, i] = vol
        resultados[2, i] = sharpe
        pesos_simulados.append(w)

    # Portfólio de máximo Sharpe
    idx_max_sharpe = np.argmax(resultados[2])
    # Portfólio de mínima variância
    idx_min_vol = np.argmin(resultados[1])

    return {
        "retornos": resultados[0],
        "volatilidades": resultados[1],
        "sharpes": resultados[2],
        "pesos_simulados": pesos_simulados,
        "tickers": tickers,
        "max_sharpe": {
            "pesos": dict(zip(tickers, pesos_simulados[idx_max_sharpe])),
            "retorno": round(resultados[0, idx_max_sharpe] * 100, 2),
            "volatilidade": round(resultados[1, idx_max_sharpe] * 100, 2),
            "sharpe": round(resultados[2, idx_max_sharpe], 3),
        },
        "min_volatilidade": {
            "pesos": dict(zip(tickers, pesos_simulados[idx_min_vol])),
            "retorno": round(resultados[0, idx_min_vol] * 100, 2),
            "volatilidade": round(resultados[1, idx_min_vol] * 100, 2),
            "sharpe": round(resultados[2, idx_min_vol], 3),
        },
    }


# ─────────────────────────────────────────────
# 4. PERFIL DE RISCO (CONTAGEM DE CRITÉRIOS)
# ─────────────────────────────────────────────
# Os limiares ficam declarados aqui em vez de escondidos dentro da
# função, para poderem ser exibidos na tela e citados na defesa.

CRITERIOS_RISCO = [
    {
        "criterio": "Volatilidade anual",
        "limiares": "> 15% = 1 pt | > 25% = 2 pts | > 40% = 3 pts",
        "base": "Convenção de mercado para ações; abaixo de 15% ao ano é "
                "o patamar típico de ativos defensivos na B3.",
        "referencia": "MARKOWITZ, H. Portfolio Selection, 1952.",
    },
    {
        "criterio": "Índice de Sharpe",
        "limiares": "< 1,0 = 1 pt | < 0,5 = 2 pts | < 0 = 3 pts",
        "base": "Sharpe abaixo de 1 é considerado fraco e abaixo de 0 "
                "significa render menos que a taxa livre de risco.",
        "referencia": "SHARPE, W. F. Mutual Fund Performance, 1966.",
    },
    {
        "criterio": "Drawdown máximo",
        "limiares": "> 15% = 1 pt | > 25% = 2 pts | > 40% = 3 pts",
        "base": "Mede o pior tombo já ocorrido, informação que a "
                "volatilidade média esconde.",
        "referencia": "MAGDON-ISMAIL, M.; ATIYA, A. F. Maximum Drawdown, 2004.",
    },
    {
        "criterio": "Concentração (HHI)",
        "limiares": "> 0,25 = 1 pt | > 0,50 = 2 pts",
        "base": "Faixas do próprio índice de Hirschman, usadas por órgãos "
                "de defesa da concorrência para separar mercados "
                "desconcentrados, moderados e concentrados.",
        "referencia": "HIRSCHMAN, A. O. The Paternity of an Index, 1964.",
    },
]

PONTOS_MAXIMO = 11


def extrair_features_risco(
    retornos: pd.DataFrame,
    pesos: Dict[str, float],
    retornos_ibov: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Extrai as features quantitativas que alimentam o score de risco.
    Janelas: 30, 90 e 252 dias.
    """
    tickers = [t for t in pesos.keys() if t in retornos.columns]
    w = np.array([pesos[t] for t in tickers])
    w = w / w.sum()
    ret_cart = retornos[tickers].dot(w)

    features = {}
    for janela in [30, 90, 252]:
        r = ret_cart.tail(janela)
        features[f"vol_{janela}d"] = r.std() * np.sqrt(252)
        features[f"ret_{janela}d"] = r.mean() * 252
        features[f"skew_{janela}d"] = float(r.skew())
        features[f"kurt_{janela}d"] = float(r.kurtosis())
        features[f"sharpe_{janela}d"] = calcular_sharpe(r)
        dd = calcular_max_drawdown((1 + r).cumprod())
        features[f"drawdown_{janela}d"] = abs(dd["max_drawdown_pct"])

    if retornos_ibov is not None:
        features["beta"] = calcular_beta(ret_cart, retornos_ibov)

    # Concentração (HHI)
    features["hhi"] = float(np.sum(w ** 2))
    # Correlação média entre ativos
    if len(tickers) > 1:
        corr = retornos[tickers].corr()
        mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
        features["corr_media"] = float(corr.where(mask).stack().mean())
    else:
        features["corr_media"] = 0.0

    return pd.DataFrame([features])


def classificar_risco(features: pd.DataFrame) -> Dict:
    """
    Classifica o risco da carteira em: Baixo / Médio / Alto / Muito Alto.

    Devolve uma FAIXA, não uma nota. A faixa vem da contagem de
    critérios de risco acionados (0 a 11 pontos possíveis), e cada
    ponto atribuído é registrado em 'detalhes' com a métrica e o valor
    que o causaram.

    Quatro critérios, com os limiares abaixo:
        volatilidade anual  > 15% / 25% / 40%   -> 1 / 2 / 3 pontos
        Sharpe              < 1,0 / 0,5 / 0     -> 1 / 2 / 3 pontos
        drawdown máximo     > 15% / 25% / 40%   -> 1 / 2 / 3 pontos
        concentração (HHI)  > 0,25 / 0,50       -> 1 / 2 pontos

    Os limiares são convenções de mercado, não resultados do estudo.
    Estão escritos aqui e na tela justamente para poderem ser
    contestados por quem lê.
    """
    vol = features.get("vol_252d", [None])[0] if hasattr(features, "get") else features["vol_252d"].iloc[0]
    sharpe = features.get("sharpe_252d", [None])[0] if hasattr(features, "get") else features["sharpe_252d"].iloc[0]
    drawdown = features.get("drawdown_252d", [None])[0] if hasattr(features, "get") else features["drawdown_252d"].iloc[0]
    hhi = features.get("hhi", [None])[0] if hasattr(features, "get") else features["hhi"].iloc[0]

    # Sistema de pontos de risco
    pontos = 0
    detalhes = []

    if vol is not None:
        if vol > 0.40:
            pontos += 3; detalhes.append(f"Volatilidade muito alta ({vol*100:.1f}%/ano)")
        elif vol > 0.25:
            pontos += 2; detalhes.append(f"Volatilidade alta ({vol*100:.1f}%/ano)")
        elif vol > 0.15:
            pontos += 1; detalhes.append(f"Volatilidade moderada ({vol*100:.1f}%/ano)")
        else:
            detalhes.append(f"Volatilidade baixa ({vol*100:.1f}%/ano)")

    if sharpe is not None:
        if sharpe < 0:
            pontos += 3; detalhes.append(f"Sharpe negativo ({sharpe:.2f})")
        elif sharpe < 0.5:
            pontos += 2; detalhes.append(f"Sharpe baixo ({sharpe:.2f})")
        elif sharpe < 1.0:
            pontos += 1; detalhes.append(f"Sharpe moderado ({sharpe:.2f})")
        else:
            detalhes.append(f"Sharpe bom ({sharpe:.2f})")

    if drawdown is not None:
        if drawdown > 40:
            pontos += 3; detalhes.append(f"Drawdown muito alto (-{drawdown:.1f}%)")
        elif drawdown > 25:
            pontos += 2; detalhes.append(f"Drawdown alto (-{drawdown:.1f}%)")
        elif drawdown > 15:
            pontos += 1; detalhes.append(f"Drawdown moderado (-{drawdown:.1f}%)")
        else:
            detalhes.append(f"Drawdown controlado (-{drawdown:.1f}%)")

    if hhi is not None:
        if hhi > 0.5:
            pontos += 2; detalhes.append(f"Carteira muito concentrada (HHI={hhi:.2f})")
        elif hhi > 0.25:
            pontos += 1; detalhes.append(f"Carteira concentrada (HHI={hhi:.2f})")

    # Faixa final — a partir da contagem de critérios acionados.
    # Não há conversão para uma escala 0-100: a faixa é ordinal
    # (Baixo < Médio < Alto < Muito Alto) e é lida junto com
    # 'detalhes', que diz exatamente quais critérios acenderam.
    if pontos >= 8:
        nivel, cor = "Muito Alto", "#E24B4A"
    elif pontos >= 5:
        nivel, cor = "Alto", "#EF9F27"
    elif pontos >= 3:
        nivel, cor = "Médio", "#F0C040"
    else:
        nivel, cor = "Baixo", "#1D9E75"

    return {
        "nivel": nivel,
        "cor": cor,
        "pontos_risco": pontos,
        "pontos_maximo": PONTOS_MAXIMO,
        "criterios": CRITERIOS_RISCO,
        "detalhes": detalhes,
        "recomendacoes": _gerar_recomendacoes(nivel, detalhes),
    }


def _gerar_recomendacoes(nivel: str, detalhes: List[str]) -> List[str]:
    recs = []
    if nivel in ["Alto", "Muito Alto"]:
        recs.append("Considere diversificar em mais setores e classes de ativos.")
        recs.append("Avalie incluir ativos defensivos (renda fixa, FIIs, dólar).")
    if any("concentrada" in d for d in detalhes):
        recs.append("Reduza a concentração distribuindo melhor os pesos entre os ativos.")
    if any("Sharpe" in d and ("negativo" in d or "baixo" in d) for d in detalhes):
        recs.append("Revise os ativos com pior relação risco/retorno.")
    if any("Drawdown muito alto" in d for d in detalhes):
        recs.append("Implemente stop-loss ou proteção com opções para limitar perdas.")
    if not recs:
        recs.append("Carteira com perfil de risco adequado. Continue monitorando.")
    return recs
