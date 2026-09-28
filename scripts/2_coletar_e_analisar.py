"""
2_coletar_e_analisar.py
-----------------------
PIPELINE COMPLETO do estudo empírico do TCC.

Executa, em ordem:
    1. Coleta notícias históricas (Google News RSS)
    2. Calcula o sentimento de cada notícia
    3. Baixa os preços históricos das mesmas datas (yfinance)
    4. Roda os testes estatísticos
    5. Salva os resultados e gera os gráficos

Como rodar (a partir da pasta InvestAI/):
    venv\\Scripts\\activate
    python scripts\\2_coletar_e_analisar.py

A primeira execução demora (coleta de notícias). Os dados ficam salvos
em CSV, então as execuções seguintes são rápidas — use USAR_CACHE = True.

Rode o 1_validar_modulo_estatistico.py ANTES deste: valida o método com
dados de resposta conhecida, antes de aplicá-lo ao dado real.
"""

import sys, os, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from datetime import date

from modulos.coleta.noticias import coletar_historico, ajustar_data_pregao
from modulos.analise.sentimento import AnalisadorV2
from modulos.coleta.precos import baixar_dados, calcular_retornos, baixar_ibovespa
from modulos.analise.hipotese import gerar_relatorio, imprimir_relatorio


# ═════════════════════════════════════════════════════════
# CONFIGURAÇÃO — ajuste aqui
# ═════════════════════════════════════════════════════════

# A amostra vem de CARTEIRA_ESTUDO (modulos/coleta/precos.py), com o
# criterio ja documentado la: no maximo 2 ativos por setor. Antes esta
# lista era digitada aqui e ficou para tras quando a amostra cresceu de
# 5 para 8 ativos — o script rodava com meia amostra sem avisar.
from modulos.coleta.precos import CARTEIRA_ESTUDO
TICKERS = CARTEIRA_ESTUDO

# Defasagens testadas: 0 = mesmo pregao, 1 = dia seguinte. Ambas estavam
# na hipotese escrita em 06/08/2026, antes da coleta.
LAGS = (0, 1)
LAG_GRAFICO = 0          # defasagem usada nos graficos de dispersao

DATA_INICIO = "2024-01-01"
DATA_FIM = date.today().isoformat()

USAR_MODELO_ML = False   # True = mais preciso, porém MUITO mais lento
USAR_CACHE = True        # True = reaproveita CSVs já baixados

# Caminhos vêm do módulo central — sempre absolutos, sempre nas pastas certas
from modulos.caminhos import (
    ARQ_NOTICIAS,
    ARQ_RESULTADO_HIPOTESE as ARQ_RESULTADO, grafico,
)


# ═════════════════════════════════════════════════════════
# ETAPA 1 — NOTÍCIAS
# ═════════════════════════════════════════════════════════

def etapa_noticias() -> pd.DataFrame:
    if USAR_CACHE and os.path.exists(ARQ_NOTICIAS):
        print(f"[CACHE] Lendo {ARQ_NOTICIAS}")
        df = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
        print(f"        {len(df)} notícias carregadas")
        return df

    print("\n" + "=" * 68)
    print("  ETAPA 1/4 — COLETA DE NOTÍCIAS HISTÓRICAS")
    print("=" * 68)
    print("  Isso demora alguns minutos. Vá tomar um café.\n")

    df = coletar_historico(
        tickers=TICKERS,
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM,
        janela_dias=30,
        pausa_seg=1.0,
    )

    if df.empty:
        print("\n[ERRO] Nenhuma notícia coletada. Verifique sua conexão.")
        sys.exit(1)

    df = ajustar_data_pregao(df)
    df.to_csv(ARQ_NOTICIAS, index=False)
    print(f"\n[OK] Salvo em {ARQ_NOTICIAS}")
    return df


# ═════════════════════════════════════════════════════════
# ETAPA 2 — SENTIMENTO
# ═════════════════════════════════════════════════════════

def etapa_sentimento(noticias: pd.DataFrame) -> pd.DataFrame:
    if "score_polaridade" in noticias.columns:
        print("[CACHE] Sentimento já calculado")
        return noticias

    print("\n" + "=" * 68)
    print("  ETAPA 2/4 — ANÁLISE DE SENTIMENTO")
    print("=" * 68)

    analisador = AnalisadorV2(usar_ml=USAR_MODELO_ML)
    df = analisador.analisar_batch(noticias)

    dist = df["classificacao"].value_counts()
    print(f"\n  Distribuição das {len(df)} notícias:")
    for classe, n in dist.items():
        print(f"    {classe:10s}: {n:5d}  ({n/len(df)*100:5.1f}%)")
    print(f"\n  Score médio geral: {df['score_polaridade'].mean():+.4f}")

    df.to_csv(ARQ_NOTICIAS, index=False)
    return df


# ═════════════════════════════════════════════════════════
# ETAPA 3 — PREÇOS
# ═════════════════════════════════════════════════════════

def etapa_precos():
    print("\n" + "=" * 68)
    print("  ETAPA 3/4 — COLETA DE PREÇOS (yfinance)")
    print("=" * 68 + "\n")

    # Pede um período maior que o das notícias, porque o Event Study
    # precisa de ~120 dias ANTERIORES para estimar alfa e beta.
    dados = baixar_dados(TICKERS, periodo="3y")
    if not dados:
        print("[ERRO] Não foi possível baixar preços.")
        sys.exit(1)

    retornos = calcular_retornos(dados)
    ibov = baixar_ibovespa(periodo="3y")

    print(f"\n  {retornos.shape[0]} pregões, {retornos.shape[1]} ativos")
    return retornos, ibov


# ═════════════════════════════════════════════════════════
# ETAPA 4 — TESTES ESTATÍSTICOS
# ═════════════════════════════════════════════════════════

def etapa_testes(noticias, retornos, ibov):
    print("\n" + "=" * 68)
    print("  ETAPA 4/4 — TESTES ESTATÍSTICOS")
    print("=" * 68)

    saida = {}
    for lag in LAGS:
        print("\n" + "-" * 68)
        print(f"  DEFASAGEM D+{lag} "
              f"({'mesmo pregao' if lag == 0 else 'dia seguinte'})")
        print("-" * 68)
        relatorio = gerar_relatorio(
            noticias=noticias,
            retornos=retornos,
            retornos_mercado=ibov,
            tickers=TICKERS,
            lag_principal=lag,
        )
        imprimir_relatorio(relatorio)
        saida[f"lag_{lag}"] = relatorio

    with open(ARQ_RESULTADO, "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=2, ensure_ascii=False, default=str)
    print(f"[OK] Resultado completo salvo em {ARQ_RESULTADO}")
    print("     (o json tem uma chave por defasagem: lag_0 e lag_1)")

    return saida


# ═════════════════════════════════════════════════════════
# ETAPA 5 — GRÁFICOS
# ═════════════════════════════════════════════════════════

def etapa_graficos(noticias, retornos):
    """Gera os gráficos que vão para o TCC."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[AVISO] matplotlib não instalado — gráficos pulados.")
        return

    from modulos.analise.hipotese import (
        montar_serie_diaria, testar_correlacao_defasada
    )

    print("\n  Gerando gráficos...")

    for ticker in TICKERS:
        serie = montar_serie_diaria(noticias, retornos, ticker)
        if serie.empty or len(serie) < 20:
            continue

        fig, axs = plt.subplots(1, 2, figsize=(13, 4.5))

        # --- Gráfico 1: dispersão sentimento x retorno em D+LAG_GRAFICO ---
        s = serie.sort_values("data").copy()
        s["retorno_lag"] = s["retorno"].shift(-LAG_GRAFICO)
        s = s.dropna()

        axs[0].scatter(s["sentimento"], s["retorno_lag"] * 100,
                       alpha=0.45, s=22, color="#1B4F8A")
        if len(s) > 2:
            b, a = np.polyfit(s["sentimento"], s["retorno_lag"] * 100, 1)
            xs = np.linspace(s["sentimento"].min(), s["sentimento"].max(), 50)
            axs[0].plot(xs, a + b * xs, color="#E87722", lw=2.2,
                        label=f"tendência (b={b:.3f})")
            axs[0].legend(fontsize=9)
        axs[0].axhline(0, color="gray", lw=0.8, ls="--")
        axs[0].axvline(0, color="gray", lw=0.8, ls="--")
        axs[0].set_xlabel("Sentimento da notícia (dia D)")
        axs[0].set_ylabel(f"Retorno em D+{LAG_GRAFICO} (%)")
        axs[0].set_title(f"{ticker} — Sentimento vs Retorno")
        axs[0].grid(alpha=0.25)

        # --- Gráfico 2: correlação por defasagem ---
        corr = testar_correlacao_defasada(serie, lags=[0, 1, 2, 3, 5])
        if not corr.empty:
            cores = ["#1B7A4A" if sig else "#94A3B8"
                     for sig in corr["significativo_5pct"]]
            axs[1].bar(corr["lag_dias"].astype(str), corr["pearson_r"],
                       color=cores, width=0.6)
            axs[1].axhline(0, color="black", lw=0.9)
            axs[1].set_xlabel("Defasagem (dias após a notícia)")
            axs[1].set_ylabel("Correlação de Pearson (r)")
            axs[1].set_title("Correlação por defasagem\n(verde = significativo, p<0,05)",
                             fontsize=10)
            axs[1].grid(alpha=0.25, axis="y")

        plt.tight_layout()
        caminho = grafico(f"dispersao_{ticker.replace('.SA','')}.png")
        plt.savefig(caminho, dpi=150)
        plt.close()
        print(f"    [OK] resultados/{caminho.name}")


# ═════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "#" * 68)
    print("#  InvestAI — ESTUDO EMPÍRICO DA HIPÓTESE")
    print("#")
    print("#  H0: o sentimento das notícias NÃO influencia o retorno")
    print("#  H1: o sentimento das notícias INFLUENCIA o retorno")
    print("#")
    print(f"#  Ativos : {', '.join(TICKERS)}")
    print(f"#  Período: {DATA_INICIO} a {DATA_FIM}")
    print("#" * 68)

    noticias = etapa_noticias()
    noticias = etapa_sentimento(noticias)
    retornos, ibov = etapa_precos()
    relatorio = etapa_testes(noticias, retornos, ibov)
    etapa_graficos(noticias, retornos)

    print("\n" + "#" * 68)
    print("#  ESTUDO CONCLUÍDO")
    print("#" * 68)
    print(f"\n  Arquivos gerados:")
    print(f"    dados/{ARQ_NOTICIAS.name}")
    print(f"    resultados/{ARQ_RESULTADO.name}")
    print(f"    resultados/dispersao_*.png\n")
