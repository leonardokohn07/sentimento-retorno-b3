"""
precos.py
---------
Coleta e processa dados históricos de ações da B3 usando yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import time
from pathlib import Path


# ─────────────────────────────────────────────────────────
# CARTEIRA PADRÃO — 10 ativos, 8 setores
# ─────────────────────────────────────────────────────────
# A composição prioriza DIVERSIDADE SETORIAL, não tamanho de mercado.
#
# Por quê? O veredito do estudo é uma PROPORÇÃO: "H0 rejeitada em X de N
# ativos". Isso pressupõe que os N casos sejam razoavelmente independentes.
# Empilhar ativos do mesmo setor infla o N artificialmente — três bancões
# respondem aos mesmos fatores (Selic, inadimplência, spread) e teriam
# resultados quase idênticos, contando como três evidências o que na
# prática é uma só.
#
# Por isso a carteira tem no máximo dois ativos por setor.
CARTEIRA_ESTUDO = [
    "PETR4.SA",   # petróleo e gás
    "VALE3.SA",   # mineração
    "ITUB4.SA",   # bancos
    "BBDC4.SA",   # bancos
    "WEGE3.SA",   # bens de capital
    "MGLU3.SA",   # varejo
    "ABEV3.SA",   # bebidas
    "RENT3.SA",   # locação de veículos
    "SUZB3.SA",   # papel e celulose

    # ─────────────────────────────────────────────────────────
    # ATIVOS QUE SAÍRAM DA AMOSTRA FINAL — motivo documentado
    #
    # "ELET3.SA"  Energia elétrica. O ticker DEIXOU DE EXISTIR: em novembro
    #             de 2025 a Eletrobras passou por rebranding corporativo e
    #             virou Axia Energia, negociando como AXIA3. As notícias
    #             foram coletadas (908 registros, 389 dias), mas o yfinance
    #             responde "Quote not found for symbol: ELET3.SA" e sem série
    #             de preços não há o que correlacionar.
    #             Para reincluir em trabalhos futuros: usar "AXIA3.SA" e
    #             tratar a descontinuidade histórica da mudança de ticker.
    #
    # "B3SA3.SA"  Excluída por decisão metodológica — ver a nota no
    #             TERMOS_BUSCA de modulos/coleta/noticias.py.
    # ─────────────────────────────────────────────────────────
]

# Carteira de exemplo das abas 1 a 5 (análise de risco de UMA carteira de
# investimento). É só um ponto de partida: o usuário edita na barra lateral.
# Mantida em 5 ativos para que a análise de risco continue comparável com os
# resultados já documentados no trabalho.
CARTEIRA_USUARIO = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "WEGE3.SA"]

# Compatibilidade com scripts antigos que importavam CARTEIRA_PADRAO
CARTEIRA_PADRAO = CARTEIRA_USUARIO
IBOVESPA = "^BVSP"


# ─────────────────────────────────────────────────────────
# ROBUSTEZ DO DOWNLOAD (acrescentado depois do incidente do ABEV3)
# ─────────────────────────────────────────────────────────
# O Yahoo recusa pedidos de vez em quando (bloqueio temporario, cookie que
# nao veio, rede ruim). Antes, um ativo que falhava era pulado em silencio:
# sumia da analise sem mensagem nenhuma e ainda mudava o denominador do
# resultado ("6 de 8" virava "6 de 7"). Agora:
#   1. tenta de novo algumas vezes, com pausa crescente;
#   2. guarda em disco toda coleta bem-sucedida;
#   3. se o Yahoo falhar, le a copia local — mesmos numeros da ultima coleta.
TENTATIVAS = 3
PAUSA_TENTATIVA = 1.5                      # segundos (dobra a cada tentativa)
PASTA_CACHE_PRECOS = Path(__file__).resolve().parent.parent.parent / "dados" / "cache_precos"
STATUS_PRECOS: Dict[str, str] = {}         # ticker -> online | cache | faltou

_ANOS = {"1y": 1, "2y": 2, "5y": 5, "10y": 10, "max": 100}


def _arquivo_cache(ticker: str, intervalo: str) -> Path:
    return PASTA_CACHE_PRECOS / f"{ticker.replace('^', 'IDX_')}_{intervalo}.csv"


def _salvar_cache(ticker: str, intervalo: str, df: pd.DataFrame) -> None:
    """Guarda o historico em disco, somando com o que ja existia."""
    try:
        PASTA_CACHE_PRECOS.mkdir(parents=True, exist_ok=True)
        arq = _arquivo_cache(ticker, intervalo)
        if arq.exists():
            antigo = pd.read_csv(arq, index_col=0, parse_dates=True)
            df = pd.concat([antigo, df])
            df = df[~df.index.duplicated(keep="last")].sort_index()
        df.to_csv(arq)
    except Exception as e:
        print(f"[AVISO] nao consegui salvar o cache de {ticker}: {e}")


def _ler_cache(ticker: str, periodo: str, intervalo: str):
    """Le o historico salvo e recorta o periodo pedido. None se nao existir."""
    arq = _arquivo_cache(ticker, intervalo)
    if not arq.exists():
        return None
    try:
        df = pd.read_csv(arq, index_col=0, parse_dates=True)
        df.index.name = "Data"
        anos = _ANOS.get(periodo, 2)
        corte = pd.Timestamp.now().normalize() - pd.Timedelta(days=int(anos * 365.25))
        return df.loc[df.index >= corte]
    except Exception as e:
        print(f"[AVISO] cache de {ticker} ilegivel: {e}")
        return None


def baixar_dados(
    tickers: List[str],
    periodo: str = "2y",
    intervalo: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """
    Baixa dados históricos de uma lista de tickers da B3.

    Args:
        tickers: Lista de tickers (ex: ['PETR4.SA', 'VALE3.SA'])
        periodo: Período de dados ('1y', '2y', '5y', 'max')
        intervalo: Frequência ('1d', '1wk', '1mo')

    Returns:
        Dicionário {ticker: DataFrame com OHLCV}
    """
    dados = {}
    STATUS_PRECOS.clear()
    for ticker in tickers:
        df = None
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                bruto = yf.Ticker(ticker).history(period=periodo, interval=intervalo)
                if not bruto.empty:
                    df = bruto
                    break
                print(f"[AVISO] {ticker}: resposta vazia "
                      f"(tentativa {tentativa}/{TENTATIVAS})")
            except Exception as e:
                print(f"[ERRO] {ticker} (tentativa {tentativa}/{TENTATIVAS}): {e}")
            if tentativa < TENTATIVAS:
                time.sleep(PAUSA_TENTATIVA * tentativa)

        if df is not None and not df.empty:
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.index.name = "Data"
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            dados[ticker] = df
            STATUS_PRECOS[ticker] = "online"
            _salvar_cache(ticker, intervalo, df)
            print(f"[OK] {ticker}: {len(df)} registros")
            continue

        # O Yahoo falhou. Usa a copia local da ultima coleta bem-sucedida em
        # vez de deixar o ativo sumir da analise sem aviso nenhum.
        cache = _ler_cache(ticker, periodo, intervalo)
        if cache is not None and not cache.empty:
            dados[ticker] = cache
            STATUS_PRECOS[ticker] = "cache"
            print(f"[CACHE] {ticker}: {len(cache)} registros lidos do arquivo local")
        else:
            STATUS_PRECOS[ticker] = "faltou"
            print(f"[AVISO] Sem dados para {ticker} (e sem cache local)")
    return dados


def calcular_retornos(dados: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calcula retornos diários logarítmicos para cada ativo.

    Returns:
        DataFrame com retornos de cada ativo nas colunas
    """
    precos = pd.DataFrame({
        ticker: df["Close"]
        for ticker, df in dados.items()
    })
    retornos = np.log(precos / precos.shift(1)).dropna()
    return retornos


def baixar_ibovespa(periodo: str = "2y") -> pd.DataFrame:
    """Baixa dados do Ibovespa como benchmark."""
    ibov = yf.Ticker(IBOVESPA)
    df = ibov.history(period=periodo)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    retornos = np.log(df["Close"] / df["Close"].shift(1)).dropna()
    return retornos.rename("IBOV")


def info_ativo(ticker: str) -> Dict:
    """
    Retorna informações fundamentalistas básicas de um ativo.

    Returns:
        Dicionário com nome, setor, P/L, dividend yield, etc.
    """
    try:
        ativo = yf.Ticker(ticker)
        info = ativo.info
        return {
            "nome": info.get("longName", ticker),
            "setor": info.get("sector", "N/D"),
            "industria": info.get("industry", "N/D"),
            "pl": info.get("trailingPE", None),
            "pvp": info.get("priceToBook", None),
            "dividend_yield": info.get("dividendYield", None),
            "market_cap": info.get("marketCap", None),
            "preco_atual": info.get("currentPrice", None),
            "52w_high": info.get("fiftyTwoWeekHigh", None),
            "52w_low": info.get("fiftyTwoWeekLow", None),
        }
    except Exception as e:
        print(f"[ERRO info] {ticker}: {e}")
        return {}


def montar_portfolio(
    tickers: List[str],
    pesos: Optional[List[float]] = None
) -> Dict:
    """
    Monta estrutura de portfólio com pesos.

    Args:
        tickers: Lista de tickers
        pesos: Lista de pesos (deve somar 1.0). Se None, pesos iguais.

    Returns:
        Dicionário com tickers e pesos
    """
    if pesos is None:
        pesos = [1.0 / len(tickers)] * len(tickers)

    assert abs(sum(pesos) - 1.0) < 1e-6, "Pesos devem somar 1.0"
    assert len(tickers) == len(pesos), "tickers e pesos devem ter o mesmo tamanho"

    return {
        "tickers": tickers,
        "pesos": dict(zip(tickers, pesos)),
        "n_ativos": len(tickers),
    }


if __name__ == "__main__":
    print("=== Teste do módulo de dados ===\n")
    portfolio = montar_portfolio(CARTEIRA_PADRAO)
    print(f"Carteira: {portfolio['tickers']}")

    dados = baixar_dados(portfolio["tickers"], periodo="1y")
    retornos = calcular_retornos(dados)

    print(f"\nRetornos calculados: {retornos.shape[0]} dias, {retornos.shape[1]} ativos")
    print(retornos.tail(3))
