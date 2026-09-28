"""
1_validar_modulo_estatistico.py
-------------------------------
VALIDAÇÃO DE INSTRUMENTO — valida o módulo modulos/analise/hipotese.py
usando DADOS SINTÉTICOS, antes de aplicá-lo aos dados reais.

Não testa instalação: testa se o MÉTODO ESTATÍSTICO funciona.
É o equivalente a calibrar um multímetro com uma tensão de referência
conhecida antes de medir um circuito desconhecido.

Por que testar com dados falsos antes dos reais?
    Porque aqui NÓS sabemos a resposta certa. Criamos dois cenários:

      Cenário A: o sentimento REALMENTE influencia o retorno (relação embutida)
                 -> o teste TEM que rejeitar H0 na maioria das simulações

      Cenário B: sentimento e retorno são totalmente aleatórios
                 -> o teste só pode rejeitar H0 em ~5% dos casos
                    (esses 5% são os FALSOS POSITIVOS esperados quando
                     usamos nível de significância de 0,05 — é da natureza
                     do método, não um erro do código)

Por que rodar muitas simulações e não uma?
    Uma única simulação pode dar azar. Rodando muitas, medimos duas
    probabilidades:
      - PODER do teste  = chance de detectar um efeito que existe
      - ERRO TIPO I     = chance de "detectar" um efeito que não existe

    Quantas? O erro padrão de uma proporção p estimada em N repetições
    é sqrt(p(1-p)/N). Para p = 0,05:
        N =  100  ->  EP = 2,18 p.p.  (faixa esperada 0,6% a 9,4%)
        N = 1000  ->  EP = 0,69 p.p.  (faixa esperada 3,6% a 6,4%)
    Com 1000 a estimativa fica precisa o bastante para ser defendida.

VERIFICAÇÃO ANALÍTICA
    Como os parâmetros da simulação são conhecidos, a correlação que o
    teste DEVERIA encontrar pode ser derivada no papel. Para S ~ U(-1,1),
    Var(S) = 1/3, e portanto:

        R² = b²·Var(S) / (b²·Var(S) + sigma²)
           = (0,010²·1/3) / (0,010²·1/3 + 0,015²) = 0,1290
        r  = sqrt(0,1290) = 0,3592

    Se o r medido no Cenário A bater com 0,3592, o módulo não apenas
    detecta o efeito: ele estima a MAGNITUDE corretamente.
"""

import sys
from pathlib import Path
# Permite rodar este script de qualquer lugar: adiciona a raiz do projeto
# (a pasta InvestAI/) ao caminho de busca do Python.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from modulos.analise.hipotese import (
    montar_serie_diaria,
    testar_correlacao_defasada,
    testar_diferenca_medias,
    regressao_sentimento_retorno,
)

N_DIAS = 400
N_SIMULACOES = 1000
FORCA_EFEITO = 0.010   # quanto o sentimento empurra o retorno do dia seguinte
VOLATILIDADE = 0.015   # volatilidade diária típica de uma ação brasileira

# ── Valores TEÓRICOS derivados dos parâmetros acima ──
# Não são chutes: saem da definição de R² para um modelo linear com ruído.
# Servem de gabarito — o teste tem que reencontrar estes números.
VAR_SENTIMENTO = 1 / 3          # variância de uma uniforme em [-1, +1]
_sinal = FORCA_EFEITO ** 2 * VAR_SENTIMENTO
_ruido = VOLATILIDADE ** 2
R2_TEORICO = _sinal / (_sinal + _ruido)
R_TEORICO = R2_TEORICO ** 0.5
ALFA = 0.05                     # nível de significância adotado


def gerar_cenario(com_relacao: bool, seed: int):
    """
    Gera notícias + retornos sintéticos.

    com_relacao=True  -> retorno de D+1 depende do sentimento de D
    com_relacao=False -> tudo aleatório (H0 verdadeira)
    """
    np.random.seed(seed)
    datas = pd.bdate_range("2024-01-01", periods=N_DIAS)

    sentimentos = np.random.uniform(-1, 1, N_DIAS)
    retornos = np.random.normal(0, VOLATILIDADE, N_DIAS)

    if com_relacao:
        # O sentimento do dia D empurra o retorno do dia D+1
        retornos[1:] += FORCA_EFEITO * sentimentos[:-1]

    noticias = pd.DataFrame({
        "ticker": "TESTE.SA",
        "data_pregao": datas,
        "score_polaridade": sentimentos,
    })
    retornos_df = pd.DataFrame({"TESTE.SA": retornos}, index=datas)
    return noticias, retornos_df


def rodar_simulacoes(com_relacao: bool) -> dict:
    """Roda N simulações e conta quantas vezes H0 foi rejeitada."""
    rejeicoes, r_valores = 0, []

    for seed in range(N_SIMULACOES):
        noticias, retornos = gerar_cenario(com_relacao, seed)
        serie = montar_serie_diaria(noticias, retornos, "TESTE.SA")
        reg = regressao_sentimento_retorno(serie, lag=1)

        if reg.get("significativo_5pct"):
            rejeicoes += 1
        r_valores.append(reg["r"])

    return {
        "taxa_rejeicao": rejeicoes / N_SIMULACOES,
        "r_medio": float(np.mean(r_valores)),
    }


def demonstrar_exemplo(com_relacao: bool, seed: int = 7):
    """Mostra a saída detalhada de UMA simulação, para ilustração."""
    noticias, retornos = gerar_cenario(com_relacao, seed)
    serie = montar_serie_diaria(noticias, retornos, "TESTE.SA")

    corr = testar_correlacao_defasada(serie, lags=[0, 1, 2, 3])
    print("    Correlação por defasagem:")
    for _, r in corr.iterrows():
        marca = "  *** SIGNIFICATIVO" if r["significativo_5pct"] else ""
        print(f"      D+{int(r['lag_dias'])}: r = {r['pearson_r']:+.4f} | "
              f"p = {r['pearson_p']:.4f}{marca}")

    reg = regressao_sentimento_retorno(serie, lag=1)
    print(f"    Regressão D+1: b = {reg['coeficiente_angular_b']:+.6f} | "
          f"R² = {reg['r2']:.4f} | p = {reg['p_valor']:.4f}")

    tm = testar_diferenca_medias(serie, lag=1, limiar=0.2)
    if "erro" not in tm:
        print(f"    Teste t: após notícia boa "
              f"{tm['retorno_medio_apos_noticia_positiva_pct']:+.4f}% vs ruim "
              f"{tm['retorno_medio_apos_noticia_negativa_pct']:+.4f}% | "
              f"p = {tm['p_valor']:.4f}")


if __name__ == "__main__":
    print("\n" + "#" * 68)
    print("#  VALIDAÇÃO DO MÓDULO ESTATÍSTICO")
    print(f"#  {N_SIMULACOES} simulações de {N_DIAS} dias cada")
    print("#" * 68)

    # ---------- CENÁRIO A ----------
    print("\n" + "=" * 68)
    print("  CENÁRIO A — o sentimento REALMENTE influencia o retorno")
    print("=" * 68)
    print("\n  Exemplo de uma simulação:")
    demonstrar_exemplo(True)

    a = rodar_simulacoes(True)
    print(f"\n  Resultado das {N_SIMULACOES} simulações:")
    print(f"    Correlação MEDIDA         : r = {a['r_medio']:+.4f}")
    print(f"    Correlação TEÓRICA        : r = {R_TEORICO:+.4f}"
          f"   <- derivada dos parâmetros")
    print(f"    Diferença                 : {abs(a['r_medio']-R_TEORICO):.4f}")
    print(f"    H0 rejeitada em           : {a['taxa_rejeicao']*100:.1f}% dos casos")
    print(f"    (isto é o PODER do teste — quanto maior, melhor)")
    ok_a = a["taxa_rejeicao"] >= 0.80
    print(f"    >>> {'✓ PASSOU' if ok_a else '✗ FALHOU'} "
          f"(esperado: pelo menos 80%)")

    # ---------- CENÁRIO B ----------
    print("\n" + "=" * 68)
    print("  CENÁRIO B — sentimento e retorno são independentes")
    print("=" * 68)
    print("\n  Exemplo de uma simulação:")
    demonstrar_exemplo(False)

    b = rodar_simulacoes(False)
    # Tolerância calculada, não arbitrária: o erro padrão de uma proporção
    # estimada em N repetições é sqrt(p(1-p)/N). Aceitamos até 3 erros
    # padrão acima de alfa — assim o critério se ajusta sozinho ao N.
    ep = (ALFA * (1 - ALFA) / N_SIMULACOES) ** 0.5
    limite = ALFA + 3 * ep

    print(f"\n  Resultado das {N_SIMULACOES} simulações:")
    print(f"    Correlação média          : r = {b['r_medio']:+.4f}"
          f"   (esperado: ~0)")
    print(f"    H0 rejeitada em           : {b['taxa_rejeicao']*100:.1f}% dos casos")
    print(f"    Valor teórico (alfa)      : {ALFA*100:.1f}%")
    print(f"    (isto é a taxa de FALSO POSITIVO — é da natureza do método)")
    ok_b = b["taxa_rejeicao"] <= limite
    print(f"    >>> {'✓ PASSOU' if ok_b else '✗ FALHOU'} "
          f"(limite: {limite*100:.1f}% = alfa + 3 erros padrão)")

    # ---------- VEREDITO ----------
    print("\n" + "#" * 68)
    if ok_a and ok_b:
        print("#  ✓ MÓDULO VALIDADO")
        print("#    Detecta efeito real e NÃO inventa efeito onde não existe.")
    else:
        print("#  ✗ ATENÇÃO: revisar o módulo")
    print("#" * 68 + "\n")
