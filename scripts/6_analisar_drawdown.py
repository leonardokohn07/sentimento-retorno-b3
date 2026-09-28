"""
6_analisar_drawdown.py
----------------------
Investiga o DRAWDOWN MAXIMO da carteira e responde a pergunta:

    "A queda veio do MERCADO INTEIRO ou foi especifica da minha carteira?"

Essa distincao e o que separa RISCO SISTEMATICO (nao diversificavel, medido
pelo Beta) de RISCO ESPECIFICO (proprio dos ativos escolhidos). E exatamente
o tipo de pergunta que uma banca faz ao ver um drawdown na tela.

Como rodar (a partir da pasta InvestAI/):
    venv\\Scripts\\activate
    python scripts\\6_analisar_drawdown.py
"""

import sys
from pathlib import Path

# Permite importar 'modulos' rodando o script de dentro de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.coleta.precos import baixar_dados, calcular_retornos, CARTEIRA_PADRAO
import yfinance as yf


# ─── CONFIGURACAO (edite aqui se sua carteira for outra) ───
CARTEIRA = CARTEIRA_PADRAO          # ["PETR4.SA", "VALE3.SA", ...]
PERIODO = "1y"                      # o mesmo do dashboard
PESOS_IGUAIS = True


def calcular_drawdown(retornos: pd.Series):
    """
    Reproduz exatamente o calculo de risco.py:
        1. reconstroi a curva de patrimonio
        2. marca o topo historico ate cada dia (cummax)
        3. mede o quanto o patrimonio esta abaixo desse topo
    """
    curva = (1 + retornos).cumprod()
    pico_movel = curva.cummax()
    dd = (curva - pico_movel) / pico_movel

    data_vale = dd.idxmin()
    data_pico = curva[:data_vale].idxmax()
    return round(dd.min() * 100, 2), data_pico, data_vale


def variacao(serie: pd.Series, ini, fim) -> float:
    """Variacao percentual de uma serie de precos entre duas datas."""
    trecho = serie.loc[str(pd.to_datetime(ini).date()):str(pd.to_datetime(fim).date())]
    if len(trecho) < 2:
        return float("nan")
    return (trecho.iloc[-1] / trecho.iloc[0] - 1) * 100


print("=" * 70)
print("  ANALISE DO DRAWDOWN MAXIMO DA CARTEIRA")
print("=" * 70)

# ─── 1. Precos da carteira ───
print(f"\n[1/3] Baixando precos de {len(CARTEIRA)} ativos ({PERIODO})...")
dados = baixar_dados(CARTEIRA, periodo=PERIODO)
if not dados:
    print("\n[ERRO] Nenhum dado baixado. Verifique a conexao.")
    sys.exit(1)

retornos = calcular_retornos(dados)
tickers_ok = list(retornos.columns)

w = np.array([1 / len(tickers_ok)] * len(tickers_ok))
ret_carteira = retornos.dot(w)

# ─── 2. Ibovespa ───
print("[2/3] Baixando Ibovespa (^BVSP)...")
ibov_df = yf.Ticker("^BVSP").history(period=PERIODO)
ibov_px = ibov_df["Close"].copy()
ibov_px.index = pd.to_datetime(ibov_px.index).tz_localize(None)
ret_ibov = np.log(ibov_px / ibov_px.shift(1)).dropna()

# ─── 3. Drawdowns ───
print("[3/3] Calculando drawdowns...\n")

dd_c, pico_c, vale_c = calcular_drawdown(ret_carteira)
dd_i, pico_i, vale_i = calcular_drawdown(ret_ibov)

print("-" * 70)
print("  SUA CARTEIRA")
print("-" * 70)
print(f"  Drawdown maximo : {dd_c:.2f}%")
print(f"  Pico            : {pico_c:%d/%m/%Y}")
print(f"  Vale            : {vale_c:%d/%m/%Y}")
print(f"  Duracao         : {(vale_c - pico_c).days} dias corridos")

print("\n" + "-" * 70)
print("  IBOVESPA (drawdown proprio, no mesmo periodo de dados)")
print("-" * 70)
print(f"  Drawdown maximo : {dd_i:.2f}%")
print(f"  Pico            : {pico_i:%d/%m/%Y}")
print(f"  Vale            : {vale_i:%d/%m/%Y}")

var_ibov = variacao(ibov_px, pico_c, vale_c)
print("\n" + "-" * 70)
print(f"  IBOVESPA NO INTERVALO EXATO DA SUA CARTEIRA")
print(f"  ({pico_c:%d/%m/%Y} ate {vale_c:%d/%m/%Y})")
print("-" * 70)
trecho_i = ibov_px.loc[str(pico_c.date()):str(vale_c.date())]
print(f"  Variacao        : {var_ibov:+.2f}%")
print(f"  Pontos          : {trecho_i.iloc[0]:,.0f}  ->  {trecho_i.iloc[-1]:,.0f}")

# ─── 4. Decomposicao por ativo ───
print("\n" + "-" * 70)
print("  DECOMPOSICAO: quanto cada acao caiu no intervalo")
print("-" * 70)
peso = 1 / len(tickers_ok)
linhas = []
for t in tickers_ok:
    v = variacao(dados[t]["Close"], pico_c, vale_c)
    linhas.append((t, v, v * peso))

for t, v, contrib in sorted(linhas, key=lambda x: x[1]):
    barra = "#" * min(40, int(abs(v)))
    print(f"  {t:<11} {v:+7.2f}%   contrib: {contrib:+6.2f} p.p.   {barra}")

soma = sum(c for _, _, c in linhas)
print(f"\n  Soma das contribuicoes: {soma:+.2f} p.p.")
print("  (nao bate exatamente com o drawdown por causa da capitalizacao diaria)")

# ─── 5. Diagnostico ───
print("\n" + "=" * 70)
print("  DIAGNOSTICO")
print("=" * 70)

if np.isnan(var_ibov):
    print("  Nao foi possivel comparar com o Ibovespa.")
else:
    razao = dd_c / var_ibov if var_ibov != 0 else float("nan")
    print(f"  Carteira no periodo : {dd_c:+.2f}%")
    print(f"  Ibovespa no periodo : {var_ibov:+.2f}%")
    print(f"  Razao               : {razao:.2f}x o movimento do indice\n")

    if razao > 1.15:
        print("  => A carteira caiu MAIS que o mercado.")
        print("     Parte da queda e sistematica (o mercado inteiro caiu),")
        print("     mas ha um componente ESPECIFICO dos ativos escolhidos.")
        print("     Olhe a decomposicao acima: as acoes no topo da lista")
        print("     sao as que puxaram a carteira para baixo.")
    elif razao < 0.85:
        print("  => A carteira caiu MENOS que o mercado.")
        print("     A diversificacao funcionou: a queda foi majoritariamente")
        print("     sistematica e a carteira amorteceu parte dela.")
    else:
        print("  => A carteira acompanhou o mercado de perto.")
        print("     A queda foi essencialmente SISTEMATICA (risco de mercado),")
        print("     nao um problema dos ativos escolhidos.")

print("\n" + "=" * 70)
print("  Use estes numeros para explicar o drawdown na defesa do TCC.")
print("=" * 70 + "\n")
