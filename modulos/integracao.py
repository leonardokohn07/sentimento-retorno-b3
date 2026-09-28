"""
integracao.py
-------------
Junta risco quantitativo e sentimento de notícias NA MESMA TELA,
lado a lado, sem fundir os dois num número só.

HISTÓRICO DESTA DECISÃO (caderno de campo, 15/09/2026)
    Até aqui este módulo calculava um "score final" por ativo:

        score_final = risco * 0,6 + (risco + ajuste_sentimento) * 0,4

    Os pesos 0,6 e 0,4 foram escolhidos por mim, sem nenhuma base.
    Não saíram de literatura, não saíram de calibração contra dado
    nenhum, e não havia como testar se estavam certos — porque não
    existe um "risco verdadeiro" observável para comparar.

    Isso tem três problemas:

    1. O número era arbitrário. Trocar 0,6/0,4 por 0,5/0,5 mudava o
       ranking dos ativos, e eu não tinha argumento para defender uma
       escolha contra a outra.
    2. Somar coisas de naturezas diferentes apaga a informação.
       Volatilidade, Sharpe, VaR e drawdown medem riscos DISTINTOS.
       Um ativo pode ser calmo no dia a dia (vol baixa) e ter tomado
       um tombo enorme uma vez (drawdown alto). Na média isso vira
       "risco médio", que não descreve nem um caso nem o outro.
    3. Misturar sentimento no score contaminava o próprio estudo.
       A hipótese do trabalho é justamente testar SE o sentimento se
       relaciona com o retorno. Embutir o sentimento no indicador de
       risco antes de testar isso é assumir a conclusão.

    Decisão registrada: tirar o score. As métricas passam a aparecer
    separadas, cada uma com sua leitura e sua referência. A carteira
    deixa de ter um número-resumo.

O QUE ESTE MÓDULO FAZ AGORA
    Monta o painel de métricas separadas. Cada métrica carrega junto:
      - como ler (o que valor alto significa)
      - de onde vem (a referência bibliográfica)
    Nada é somado, nada é ponderado, nada vira nota.
"""

import pandas as pd
from typing import Dict, List


# ─────────────────────────────────────────────
# FICHA DE CADA MÉTRICA
# ─────────────────────────────────────────────
# Responde diretamente a pergunta da banca da FEICIT:
# "em que vocês se basearam para usar cada métrica de risco?"

FICHA_METRICAS = {
    "volatilidade_anual_pct": {
        "nome": "Volatilidade anual",
        "unidade": "%",
        "mede": "o quanto o preço oscila em torno da própria média",
        "leitura": "Maior = oscila mais. Não diz se sobe ou desce, só a "
                   "intensidade do balanço.",
        "como": "desvio-padrão dos retornos diários x raiz de 252",
        "referencia": "MARKOWITZ, H. Portfolio Selection. The Journal of "
                      "Finance, v. 7, n. 1, p. 77-91, 1952.",
        "pior_quando": "alto",
    },
    "sharpe": {
        "nome": "Índice de Sharpe",
        "unidade": "",
        "mede": "quanto retorno acima da taxa livre de risco o ativo "
                "entrega por unidade de oscilação",
        "leitura": "Maior = melhor. Negativo significa que rendeu menos "
                   "que a Selic e ainda oscilou.",
        "como": "(retorno anual - Selic) / volatilidade anual",
        "referencia": "SHARPE, W. F. Mutual Fund Performance. The Journal "
                      "of Business, v. 39, n. 1, p. 119-138, 1966.",
        "pior_quando": "baixo",
    },
    "var_95_pct": {
        "nome": "VaR 95% (1 dia)",
        "unidade": "%",
        "mede": "a perda que não é ultrapassada em 95% dos dias",
        "leitura": "Mais negativo = pior. Em 1 dia a cada 20, a perda "
                   "tende a ser maior que esse valor.",
        "como": "percentil 5 da série histórica de retornos diários",
        "referencia": "JORION, P. Value at Risk: the new benchmark for "
                      "managing financial risk. 3. ed. New York: "
                      "McGraw-Hill, 2007.",
        "pior_quando": "baixo",
    },
    "max_drawdown_pct": {
        "nome": "Drawdown máximo",
        "unidade": "%",
        "mede": "a maior queda já sofrida do topo até o fundo seguinte",
        "leitura": "Mais negativo = pior. É o tamanho do pior tombo do "
                   "período, não a oscilação típica.",
        "como": "menor valor de (preço / máximo acumulado até ali) - 1",
        "referencia": "MAGDON-ISMAIL, M.; ATIYA, A. F. Maximum Drawdown. "
                      "Risk Magazine, v. 17, n. 10, p. 99-102, 2004.",
        "pior_quando": "baixo",
    },
    "beta": {
        "nome": "Beta (vs. Ibovespa)",
        "unidade": "",
        "mede": "o quanto o ativo se move quando o mercado inteiro se move",
        "leitura": "Beta 1 = anda junto com o índice. Acima de 1 = "
                   "exagera o movimento. Abaixo de 1 = amortece.",
        "como": "covariância(ativo, Ibovespa) / variância(Ibovespa)",
        "referencia": "SHARPE, W. F. Capital Asset Prices: a theory of "
                      "market equilibrium under conditions of risk. The "
                      "Journal of Finance, v. 19, n. 3, p. 425-442, 1964.",
        "pior_quando": "alto",
    },
    "retorno_anual_pct": {
        "nome": "Retorno anual",
        "unidade": "%",
        "mede": "o retorno médio do período, projetado para um ano",
        "leitura": "Maior = melhor. É desempenho passado, não previsão.",
        "como": "retorno médio diário x 252",
        "referencia": "FAMA, E. F. Efficient Capital Markets: a review of "
                      "theory and empirical work. The Journal of Finance, "
                      "v. 25, n. 2, p. 383-417, 1970.",
        "pior_quando": "baixo",
    },
    "hhi": {
        "nome": "Concentração (HHI)",
        "unidade": "",
        "mede": "o quanto a carteira está apoiada em poucos ativos",
        "leitura": "Vai de 1/n (tudo igual) a 1 (um ativo só). Acima de "
                   "0,25 já é considerada concentrada.",
        "como": "soma dos quadrados dos pesos de cada ativo",
        "referencia": "HIRSCHMAN, A. O. The Paternity of an Index. The "
                      "American Economic Review, v. 54, n. 5, p. 761-762, "
                      "1964.",
        "pior_quando": "alto",
    },
}


def montar_painel_metricas(metricas_individuais: pd.DataFrame) -> pd.DataFrame:
    """
    Devolve a tabela de métricas por ativo, sem nenhuma agregação.

    É de propósito quase uma cópia da entrada: a função existe para
    garantir a ORDEM das colunas e para deixar explícito no código que
    daqui não sai número combinado nenhum.
    """
    ordem = [c for c in FICHA_METRICAS if c in metricas_individuais.columns]
    extras = [c for c in metricas_individuais.columns if c not in ordem]
    return metricas_individuais[ordem + extras].copy()


def tabela_de_referencias(colunas: List[str] = None) -> pd.DataFrame:
    """
    A ficha das métricas em formato de tabela, para exibir na tela.
    É a resposta da banca virando parte do próprio sistema.
    """
    alvo = colunas or list(FICHA_METRICAS.keys())
    linhas = []
    for c in alvo:
        f = FICHA_METRICAS.get(c)
        if not f:
            continue
        linhas.append({
            "Métrica": f["nome"],
            "O que mede": f["mede"],
            "Como ler": f["leitura"],
            "Cálculo": f["como"],
            "Referência": f["referencia"],
        })
    return pd.DataFrame(linhas)


def extremos_por_metrica(painel: pd.DataFrame) -> List[Dict]:
    """
    Para cada métrica, diz qual ativo está no pior extremo E qual está
    no melhor — SEM ranquear os ativos entre si.

    A diferença é importante: aqui cada métrica aponta o seu próprio
    ativo. Não existe "o ativo mais arriscado da carteira", existe "o
    mais volátil", "o de maior drawdown", "o de menor Sharpe" — e eles
    frequentemente não são o mesmo ativo. Era exatamente essa
    informação que o score antigo apagava.
    """
    saida = []
    for col, f in FICHA_METRICAS.items():
        if col not in painel.columns:
            continue
        s = painel[col].dropna()
        if s.empty:
            continue
        if f["pior_quando"] == "alto":
            pior, melhor = s.idxmax(), s.idxmin()
        else:
            pior, melhor = s.idxmin(), s.idxmax()
        saida.append({
            "coluna": col,
            "metrica": f["nome"],
            "unidade": f["unidade"],
            "leitura": f["leitura"],
            "referencia": f["referencia"],
            "ativo_pior": pior,
            "valor_pior": float(s.loc[pior]),
            "ativo_melhor": melhor,
            "valor_melhor": float(s.loc[melhor]),
        })
    return saida


def gerar_relatorio_integrado(
    perfil_risco: Dict,
    painel: pd.DataFrame,
    sentimento: pd.DataFrame,
    alertas_risco: List[Dict],
    alertas_sentimento: List[Dict],
) -> Dict:
    """
    Consolida os dados num dicionário de relatório.

    Mudou em 15/09: não devolve mais 'score_carteira' nem
    'score_medio_ativos'. O relatório agora carrega o painel de
    métricas separadas e os extremos de cada uma.
    """
    todos_alertas = alertas_risco + alertas_sentimento
    todos_alertas.sort(key=lambda x: x.get("severidade", "Baixa"), reverse=True)

    extremos = extremos_por_metrica(painel)

    return {
        "perfil_risco": perfil_risco,
        "painel": painel,
        "extremos": extremos,
        "sentimento": sentimento,
        "alertas": todos_alertas,
        "n_alertas": len(todos_alertas),
        "leitura": _gerar_leitura(perfil_risco, extremos, todos_alertas),
    }


def _fmt(v: float, unidade: str) -> str:
    txt = f"{v:.2f}".replace(".", ",")
    return f"{txt}{unidade}"


def _gerar_leitura(perfil: Dict, extremos: List[Dict], alertas: List) -> str:
    """
    Texto de leitura da carteira — por métrica, não por nota.

    Antes esta função escrevia "sua carteira tem score 62/100".
    Agora ela nomeia qual métrica acendeu e em qual ativo, que é o
    que a pessoa consegue de fato usar.
    """
    nivel = perfil.get("nivel", "não classificado")
    pontos = perfil.get("pontos_risco", 0)

    partes = [
        f"A carteira acionou **{pontos} ponto(s)** nos critérios de risco, "
        f"o que a coloca na faixa **{nivel}**. Essa faixa é um resumo dos "
        f"critérios, não uma nota: cada métrica abaixo tem leitura própria."
    ]

    # cada métrica fala do SEU pior ativo, com o verbo certo para o sinal
    VERBO = {
        "volatilidade_anual_pct": "maior volatilidade",
        "max_drawdown_pct": "pior drawdown",
        "sharpe": "menor Sharpe",
        "var_95_pct": "pior VaR 95%",
    }
    destaques = []
    for e in extremos:
        rotulo = VERBO.get(e["coluna"])
        if rotulo:
            destaques.append(
                f"{rotulo} em **{e['ativo_pior']}** "
                f"({_fmt(e['valor_pior'], e['unidade'])})"
            )
    if destaques:
        partes.append("Pelos extremos: " + "; ".join(destaques) + ".")
        partes.append(
            "Repare que esses ativos não precisam ser o mesmo — é por isso "
            "que não faz sentido colapsar tudo num número só."
        )

    if alertas:
        partes.append(f"Há **{len(alertas)} alerta(s)** abertos na aba Alertas.")

    return " ".join(partes)
