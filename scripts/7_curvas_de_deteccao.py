"""
7_curvas_de_deteccao.py
-----------------------
ANÁLISE DE SENSIBILIDADE do módulo estatístico.

O script 1 responde "o método funciona?" num ÚNICO ponto:
400 dias de amostra e efeito de força 0,010. Resposta: sim, poder de 100%.

Este script responde a pergunta seguinte, que é a que a banca faz:

    "Até ONDE o seu instrumento enxerga?"

Duas curvas:

  CURVA 1 — PODER x FORÇA DO EFEITO   (amostra fixa em 400 dias)
      Reduz o efeito até o teste deixar de detectá-lo.
      Entrega o EFEITO MÍNIMO DETECTÁVEL.

  CURVA 2 — PODER x TAMANHO DA AMOSTRA  (efeito fixo em 0,010)
      Reduz o número de dias até o teste deixar de detectar.
      Entrega o Nº MÍNIMO DE DIAS necessário.
      Inclui o ponto de 20 dias, que é o limite usado hoje no dashboard.

POR QUE ISSO IMPORTA
    Todo instrumento tem limite de resolução. Um multímetro de 3½ dígitos
    não lê microvolts — e isso não é defeito, é especificação. O mesmo vale
    para um teste estatístico: abaixo de certo tamanho de efeito ou de
    amostra, ele simplesmente não tem como distinguir sinal de ruído.

    Sem conhecer esse limite, um resultado NÃO SIGNIFICATIVO é ambíguo:
    não se sabe se o efeito não existe ou se o teste não conseguiu vê-lo.
    Com o limite medido, o resultado nulo vira quantitativo:
    "se existe efeito, ele é menor que X".

VALIDAÇÃO CRUZADA
    Além do poder medido por simulação, o script calcula o poder TEÓRICO
    pela transformação z de Fisher. Se as duas curvas coincidirem, temos
    mais uma confirmação independente de que o módulo está correto.

Como rodar (a partir da pasta InvestAI/):
    venv\\Scripts\\activate
    python scripts\\7_curvas_de_deteccao.py
"""

import sys
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")          # sem janela gráfica: salva direto em arquivo
import matplotlib.pyplot as plt

from modulos.analise.hipotese import (
    montar_serie_diaria, regressao_sentimento_retorno,
)
from modulos.caminhos import PASTA_RESULTADOS


# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────
N_SIMULACOES = 300      # por ponto da curva. EP do poder ~2,9 p.p.
VOLATILIDADE = 0.015    # o mesmo valor do script 1
ALFA = 0.05
META_PODER = 0.80       # convenção da literatura (Cohen, 1988)

# Curva 1: varia a força, amostra fixa
DIAS_FIXO = 400
FORCAS = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008, 0.010, 0.015]

# Curva 2: varia a amostra, força fixa
FORCA_FIXA = 0.010
DIAS = [20, 40, 60, 100, 150, 200, 300, 400, 600, 800]


# ─────────────────────────────────────────────────────────
# GERAÇÃO DOS DADOS SINTÉTICOS
# ─────────────────────────────────────────────────────────
# Reaproveita a MESMA função do script 1, em vez de duplicar a lógica.
# O import normal não funciona porque o nome do arquivo começa com dígito
# ("1_validar...") e não é um identificador Python válido — daí o importlib.

_caminho = Path(__file__).resolve().parent / "1_validar_modulo_estatistico.py"
_spec = importlib.util.spec_from_file_location("validador", _caminho)
_validador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validador)


def gerar(n_dias: int, forca: float, seed: int):
    """Mesma construção do script 1, com n_dias e força parametrizados."""
    np.random.seed(seed)
    datas = pd.bdate_range("2024-01-01", periods=n_dias)
    sentimentos = np.random.uniform(-1, 1, n_dias)
    retornos = np.random.normal(0, VOLATILIDADE, n_dias)
    retornos[1:] += forca * sentimentos[:-1]      # efeito em D+1

    noticias = pd.DataFrame({
        "ticker": "TESTE.SA",
        "data_pregao": datas,
        "score_polaridade": sentimentos,
    })
    return noticias, pd.DataFrame({"TESTE.SA": retornos}, index=datas)


def medir_poder(n_dias: int, forca: float) -> float:
    """Fração das simulações em que H0 foi corretamente rejeitada."""
    acertos = 0
    for seed in range(N_SIMULACOES):
        noticias, retornos = gerar(n_dias, forca, seed)
        serie = montar_serie_diaria(noticias, retornos, "TESTE.SA")
        reg = regressao_sentimento_retorno(serie, lag=1)
        if reg.get("significativo_5pct"):
            acertos += 1
    return acertos / N_SIMULACOES


# ─────────────────────────────────────────────────────────
# PODER TEÓRICO (transformação z de Fisher)
# ─────────────────────────────────────────────────────────

def r_esperado(forca: float) -> float:
    """
    Correlação que os parâmetros implicam.
        R² = b²·Var(S) / (b²·Var(S) + sigma²),  com Var(S) = 1/3
    """
    sinal = forca ** 2 * (1 / 3)
    ruido = VOLATILIDADE ** 2
    return float(np.sqrt(sinal / (sinal + ruido)))


def poder_teorico(n_dias: int, forca: float) -> float:
    """
    Poder analítico do teste de correlação de Pearson.

    A transformação z de Fisher, z = arctanh(r), é aproximadamente normal
    com média arctanh(rho) e desvio 1/sqrt(n-3). O teste bilateral rejeita
    H0 quando |z| ultrapassa o valor crítico, então:

        poder = P(Z > z_c - arctanh(rho)*sqrt(n-3))
              + P(Z < -z_c - arctanh(rho)*sqrt(n-3))
    """
    n = n_dias - 1                      # perde-se 1 observação pelo lag D+1
    if n <= 4:
        return float("nan")
    rho = r_esperado(forca)
    z_rho = np.arctanh(rho) * np.sqrt(n - 3)
    z_c = stats.norm.ppf(1 - ALFA / 2)
    return float(stats.norm.sf(z_c - z_rho) + stats.norm.cdf(-z_c - z_rho))


def cruzamento(xs, ys, meta=META_PODER):
    """Interpola em que x a curva de poder cruza a meta (ex.: 80%)."""
    for i in range(1, len(ys)):
        if ys[i - 1] < meta <= ys[i]:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            return x0 + (meta - y0) * (x1 - x0) / (y1 - y0)
    return None


# ─────────────────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("#  CURVAS DE DETECÇÃO — até onde o instrumento enxerga")
    print(f"#  {N_SIMULACOES} simulações por ponto | alfa = {ALFA} | meta de poder = {META_PODER:.0%}")
    print("#" * 70)

    # ══════════ CURVA 1 ══════════
    print("\n" + "=" * 70)
    print(f"  CURVA 1 — PODER x FORÇA DO EFEITO   (amostra fixa: {DIAS_FIXO} dias)")
    print("=" * 70)
    print(f"\n  {'força b':>9} | {'r implícito':>11} | {'poder medido':>12} | "
          f"{'poder teórico':>13} | gráfico")
    print("  " + "-" * 66)

    poder_f, teorico_f = [], []
    for f in FORCAS:
        p = medir_poder(DIAS_FIXO, f)
        t = poder_teorico(DIAS_FIXO, f)
        poder_f.append(p); teorico_f.append(t)
        barra = "#" * int(p * 30)
        print(f"  {f:>9.4f} | {r_esperado(f):>11.4f} | {p:>11.1%} | "
              f"{t:>12.1%} | {barra}")

    f_min = cruzamento(FORCAS, poder_f)
    print()
    if f_min:
        print(f"  >>> EFEITO MÍNIMO DETECTÁVEL: b ≈ {f_min:.4f}"
              f"  (r ≈ {r_esperado(f_min):.3f})")
        print(f"      Abaixo disso o teste tem menos de {META_PODER:.0%} de chance de detectar.")
    else:
        print("  >>> A curva não cruzou a meta na faixa testada.")

    # ══════════ CURVA 2 ══════════
    print("\n" + "=" * 70)
    print(f"  CURVA 2 — PODER x TAMANHO DA AMOSTRA   (força fixa: {FORCA_FIXA})")
    print("=" * 70)
    print(f"\n  {'dias':>6} | {'poder medido':>12} | {'poder teórico':>13} | gráfico")
    print("  " + "-" * 66)

    poder_d, teorico_d = [], []
    for d in DIAS:
        p = medir_poder(d, FORCA_FIXA)
        t = poder_teorico(d, FORCA_FIXA)
        poder_d.append(p); teorico_d.append(t)
        marca = "  <- limite atual do dashboard" if d == 20 else ""
        barra = "#" * int(p * 30)
        print(f"  {d:>6} | {p:>11.1%} | {t:>12.1%} | {barra}{marca}")

    d_min = cruzamento(DIAS, poder_d)
    print()
    if d_min:
        print(f"  >>> AMOSTRA MÍNIMA: ≈ {d_min:.0f} dias com notícia")
        print(f"      para {META_PODER:.0%} de poder com efeito de força {FORCA_FIXA}.")
    else:
        print("  >>> A curva não cruzou a meta na faixa testada.")

    print(f"\n  >>> Com os 20 dias exigidos hoje pelo dashboard, "
          f"o poder é de apenas {poder_d[0]:.1%}.")

    # ══════════ GRÁFICOS ══════════
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot([f * 1000 for f in FORCAS], [p * 100 for p in poder_f],
             "o-", color="#1D9E75", lw=2, label="Poder medido (simulação)")
    ax1.plot([f * 1000 for f in FORCAS], [t * 100 for t in teorico_f],
             "s--", color="#2E75B6", lw=1.5, alpha=.8, label="Poder teórico (Fisher)")
    ax1.axhline(META_PODER * 100, color="#E24B4A", ls=":", label="Meta de 80%")
    ax1.set_xlabel("Força do efeito  b  (× 1000)")
    ax1.set_ylabel("Poder do teste (%)")
    ax1.set_title(f"Poder x Força do efeito\n(amostra fixa: {DIAS_FIXO} dias)")
    ax1.grid(alpha=.3); ax1.legend(); ax1.set_ylim(-5, 105)

    ax2.plot(DIAS, [p * 100 for p in poder_d],
             "o-", color="#1D9E75", lw=2, label="Poder medido (simulação)")
    ax2.plot(DIAS, [t * 100 for t in teorico_d],
             "s--", color="#2E75B6", lw=1.5, alpha=.8, label="Poder teórico (Fisher)")
    ax2.axhline(META_PODER * 100, color="#E24B4A", ls=":", label="Meta de 80%")
    ax2.axvline(20, color="#EF9F27", ls="-.", label="Limite atual (20 dias)")
    ax2.set_xlabel("Dias com notícia na amostra")
    ax2.set_ylabel("Poder do teste (%)")
    ax2.set_title(f"Poder x Tamanho da amostra\n(força fixa: {FORCA_FIXA})")
    ax2.grid(alpha=.3); ax2.legend(); ax2.set_ylim(-5, 105)

    plt.tight_layout()
    saida = PASTA_RESULTADOS / "curvas_de_deteccao.png"
    plt.savefig(saida, dpi=150)
    print(f"\n  Gráfico salvo em: resultados/{saida.name}")

    print("\n" + "#" * 70)
    print("#  Se as curvas medida e teórica coincidem, o módulo está correto")
    print("#  E VOCÊ AGORA CONHECE O LIMITE DE RESOLUÇÃO DO SEU INSTRUMENTO.")
    print("#" * 70 + "\n")
