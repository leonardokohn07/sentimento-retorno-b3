"""
12_teste_permutacao.py
----------------------
CONTROLE NEGATIVO — o teste que tenta derrubar o próprio resultado.

A PERGUNTA QUE ESTE SCRIPT RESPONDE
    O p-valor clássico da regressão vem de uma fórmula que assume coisas
    sobre a distribuição dos dados: que os resíduos são normais, que a
    variância é constante, que as observações são independentes. Retorno
    de ação viola as três em maior ou menor grau.

    Então fica a dúvida: a correlação que encontramos é real, ou é um
    artefato de estarmos usando uma fórmula cujas premissas os dados não
    cumprem?

COMO O TESTE FUNCIONA
    Se a relação entre sentimento e retorno for real, ela precisa SUMIR
    quando o pareamento for destruído.

    Embaralhar a coluna de sentimento faz exatamente isso: cada retorno
    passa a ficar ao lado de um sentimento de outro dia, escolhido ao
    acaso. As duas distribuições continuam idênticas — mesma média, mesmo
    desvio, mesmos valores. Só o PAREAMENTO entre elas foi destruído.

    Refazendo a correlação 10.000 vezes com o sentimento embaralhado,
    monta-se a distribuição do que o acaso sozinho produz. O p-valor sai
    empírico: a fração de embaralhamentos que gerou correlação igual ou
    maior, em módulo, que a observada.

POR QUE ISSO VALE MAIS QUE O P-VALOR CLÁSSICO
    Esta versão não assume normalidade nem nada sobre a forma da
    distribuição. A única suposição é que, sob H0, o pareamento entre
    sentimento e retorno é arbitrário — que é literalmente o enunciado
    da hipótese nula.

    Se os dois p-valores baterem, os métodos se corroboram por caminhos
    independentes, e fica demonstrado que o resultado não dependia de uma
    premissa distribucional que os dados não cumprem.

    Se NÃO baterem, o p-valor de permutação é o que vale.

Como rodar (a partir da pasta InvestAI/):
    venv\\Scripts\\activate
    python scripts\\12_teste_permutacao.py

Gera:
    resultados/resultado_permutacao.txt
    resultados/permutacao_<ATIVO>.png          (para o caderno de campo)
    resultados/banner_permutacao_<ATIVO>.png   (596 x 86 mm, slot do banner)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.coleta.precos import baixar_dados, calcular_retornos
from modulos.analise.hipotese import (
    montar_serie_diaria, regressao_sentimento_retorno, MIN_OBSERVACOES,
)
from modulos.caminhos import ARQ_NOTICIAS, PASTA_RESULTADOS, grafico

SEMENTE = 42      # fixa para o resultado ser reprodutível por terceiros
N_PERM = 10000    # 10 mil embaralhamentos por ativo


def permutar(sent, ret, n_perm, rng):
    """
    Devolve o r observado, a distribuição sob embaralhamento e o p empírico.

    A correção +1 no numerador e no denominador evita p-valor igual a
    zero: com 10.000 permutações o menor valor possível passa a ser
    1/10.001, que é o que os dados de fato sustentam. Reportar p = 0
    seria afirmar uma certeza que a simulação não dá.
    """
    r_obs = np.corrcoef(sent, ret)[0, 1]
    nulos = np.empty(n_perm)
    s = sent.copy()
    for i in range(n_perm):
        rng.shuffle(s)
        nulos[i] = np.corrcoef(s, ret)[0, 1]
    p = (np.sum(np.abs(nulos) >= abs(r_obs)) + 1) / (n_perm + 1)
    return r_obs, nulos, p


linhas = []


def out(t=""):
    print(t)
    linhas.append(t)


out("\n" + "=" * 78)
out("  TESTE DE PERMUTAÇÃO — CONTROLE NEGATIVO")
out("=" * 78)

if not ARQ_NOTICIAS.exists():
    print("\n[ERRO] Arquivo de notícias não encontrado.")
    print("       Rode primeiro: python scripts\\2_coletar_e_analisar.py")
    sys.exit(1)

noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
tickers = sorted(noticias["ticker"].dropna().unique())
out(f"\n  Notícias no arquivo : {len(noticias)}")
out(f"  Ativos              : {len(tickers)}")
out(f"  Permutações por ativo: {N_PERM}")
out(f"  Semente             : {SEMENTE}")

print("\n  Baixando preços (histórico 5 anos)...")
dados = baixar_dados(tickers, periodo="5y")
if not dados:
    print("\n[ERRO] Não foi possível baixar preços.")
    sys.exit(1)
retornos = calcular_retornos(dados)

rng = np.random.default_rng(SEMENTE)

out("")
out("=" * 78)
out("  RESULTADO — p clássico (fórmula)  x  p de permutação (empírico)")
out("=" * 78)
out("")
out(f"  {'ativo':<9}{'n':>6}{'r obs.':>10}{'p clássico':>13}"
    f"{'p permut.':>12}{'percentil':>11}  veredito")
out("  " + "-" * 74)

resultados = []
for tk in tickers:
    serie = montar_serie_diaria(noticias, retornos, tk)
    if serie.empty or len(serie) < MIN_OBSERVACOES:
        continue

    # lag=0: mesmo pareamento usado na análise principal
    reg = regressao_sentimento_retorno(serie, lag=0)
    if "erro" in reg:
        continue

    s = serie.dropna(subset=["sentimento", "retorno"])
    sent = s["sentimento"].to_numpy(dtype=float)
    ret = s["retorno"].to_numpy(dtype=float)
    if sent.std() == 0 or ret.std() == 0:
        continue

    r_obs, nulos, p_perm = permutar(sent, ret, N_PERM, rng)
    pct = (np.sum(np.abs(nulos) < abs(r_obs)) / N_PERM) * 100
    p_cla = reg["p_valor"]

    sig_cla = p_cla < 0.05
    sig_per = p_perm < 0.05
    if sig_cla and sig_per:
        veredito = "rejeita H0 nos dois"
    elif not sig_cla and not sig_per:
        veredito = "não rejeita nos dois"
    else:
        veredito = "DIVERGEM — vale o de permutação"

    out(f"  {tk:<9}{len(s):>6}{r_obs:>10.4f}{p_cla:>13.4f}"
        f"{p_perm:>12.4f}{pct:>10.1f}%  {veredito}")
    resultados.append((tk, len(s), r_obs, p_cla, p_perm, nulos))

if not resultados:
    out("\n  Nenhum ativo com amostra suficiente "
        f"(mínimo {MIN_OBSERVACOES} observações).")

out("")
out("  COMO LER")
out("  O p de permutação é a fração dos 10.000 embaralhamentos que produziu")
out("  correlação igual ou maior, em módulo, que a observada. O percentil diz")
out("  onde o r observado caiu dentro da distribuição do acaso.")
out("")
out("  Se as duas colunas de p concordarem, os métodos se corroboram por")
out("  caminhos independentes — e fica demonstrado que o resultado não")
out("  dependia de uma premissa de distribuição que os dados não cumprem.")
out("  Se divergirem, o de permutação é o que vale, porque não assume nada")
out("  sobre a forma da distribuição.")

destino_txt = PASTA_RESULTADOS / "resultado_permutacao.txt"
destino_txt.write_text("\n".join(linhas), encoding="utf-8")
print(f"\n[OK] Resultado salvo em resultados/{destino_txt.name}")

# ─────────────────────────────────────────────────────────
# FIGURAS
# ─────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # --- 1) figura normal, para o caderno de campo e para o TCC ---
    for tk, n, r_obs, p_cla, p_perm, nulos in resultados:
        fig, ax = plt.subplots(figsize=(6, 3.6))
        ax.hist(nulos, bins=60, color="#BBD3CB", edgecolor="white", linewidth=0.4)
        ax.axvline(r_obs, color="#9E3B33", linewidth=2)
        ax.annotate(f"r observado = {r_obs:.4f}",
                    xy=(r_obs, ax.get_ylim()[1] * 0.88),
                    xytext=(8, 0), textcoords="offset points",
                    color="#9E3B33", fontsize=9, fontweight="bold")
        ax.set_title(f"{tk} — distribuição sob embaralhamento "
                     f"(n={n}, p={p_perm:.4f})", fontsize=10)
        ax.set_xlabel("correlação com o sentimento embaralhado")
        ax.set_ylabel("frequência")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(grafico(f"permutacao_{tk}.png"), dpi=200)
        plt.close(fig)

    # --- 2) figura do banner: encaixe exato no slot de 596 x 86 mm ---
    # Tudo dimensionado em mm e convertido para pontos (1 mm = 2,835 pt),
    # para o texto sair legível no tamanho impresso.
    LARG_MM, ALT_MM, DPI = 596, 86, 200
    MM2PT = 72 / 25.4

    for tk, n, r_obs, p_cla, p_perm, nulos in resultados:
        fig, ax = plt.subplots(figsize=(LARG_MM / 25.4, ALT_MM / 25.4))
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")
        ax.hist(nulos, bins=90, color="#BBD3CB", edgecolor="none")

        ax.axvline(r_obs, color="#9E3B33", linewidth=4 * MM2PT / 2.835)
        topo = ax.get_ylim()[1]
        # se a linha cair na metade direita, o rótulo vai para a esquerda
        # dela, senão o texto sai cortado na borda do banner
        x0, x1 = ax.get_xlim()
        a_direita = (r_obs - x0) / (x1 - x0) > 0.55
        ax.annotate(f"r observado = {r_obs:.4f}".replace(".", ","),
                    xy=(r_obs, topo * 0.92),
                    xytext=((-6 if a_direita else 6) * MM2PT, 0),
                    textcoords="offset points",
                    color="#9E3B33", fontsize=13 * MM2PT, fontweight="bold",
                    va="top", ha="right" if a_direita else "left")
        # o nome do ativo vai no rotulo: sem ele, quem olha o banner nao sabe
        # a qual linha da tabela de resultados o grafico corresponde
        ax.annotate(f"{tk.replace('.SA', '')} · 10.000 embaralhamentos",
                    xy=(0.01, 0.92), xycoords="axes fraction",
                    color="#5A6A66", fontsize=11 * MM2PT, va="top", ha="left")

        ax.set_yticks([])   # num histograma a frequência é óbvia pela altura
        ax.tick_params(axis="x", labelsize=11 * MM2PT, colors="#3A4A47",
                       length=3 * MM2PT, width=1 * MM2PT)
        for lado in ["top", "right", "left"]:
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color("#8FA39D")
        ax.spines["bottom"].set_linewidth(1.2 * MM2PT)

        fig.subplots_adjust(left=0.012, right=0.995, top=0.97, bottom=0.30)
        fig.savefig(grafico(f"banner_permutacao_{tk}.png"),
                    dpi=DPI, facecolor="#FFFFFF")
        plt.close(fig)

    print(f"[OK] {len(resultados)} figuras para o caderno "
          f"e {len(resultados)} para o banner em resultados/")
except Exception as e:
    print(f"(figuras não geradas: {e})")

print()
