# -*- coding: utf-8 -*-
"""Pergunta 3: quem vem primeiro, a notícia ou o preço?"""
import streamlit as st

from modulos import graficos as G
from modulos import resultados as R
from modulos.graficos import br, p_txt
from modulos.interface import como_ler, fonte, mostrar, numero, pergunta

ng = R.numeros_gerais()
tds = R.testes_direcao()
td = {t["chave"]: t for t in tds}

st.markdown("# 3 · Quem vem primeiro?")
pergunta("A pergunta", "Se notícia e preço andam juntos no mesmo dia, foi a notícia que mexeu no preço, "
                       "ou o preço que virou notícia?")
st.markdown(
    "Com dados diários, não dá para saber: uma notícia das 9h e um movimento das 15h caem no mesmo "
    "\"dia\". Estudos com dados intradiários mostram que o preço reage a notícias em **minutos** "
    "(Busse e Green, 2002). Por isso o estudo buscou a **hora e o minuto** de publicação de "
    f"{numero(ng['com_horario'])} notícias e comparou o preço **antes** e **depois** de cada uma, "
    "em três resoluções.")
mostrar(G.esquema_direcao(), "esquema")
st.caption("Em cada resolução, o trecho azul (antes da notícia) testa se o preço anda antes; o âmbar "
           "(depois) testa se a notícia antecipa o preço. A barra de preço que contém o instante da "
           "publicação fica de fora, porque mistura antes e depois.")

st.markdown("## O resultado dos testes de direção")
medida = st.segmented_control("Medida de sentimento", ["léxico", "FinBERT-PT-BR"], default="léxico") or "léxico"
mostrar(G.direcao(tds, "lexico" if medida == "léxico" else "finbert"), "direcao")
st.caption("● significativo (p < 0,05)  ·  ○ não significativo  ·  faixa cinza: efeitos pequenos demais "
           "para aquele teste enxergar (menor efeito detectável).")
fonte("etapas E16, E17, E19 e E27 do verificador (barras de 1 minuto: 20 pregões, 03/09 a 01/10/2026).")

a, b = st.columns(2, gap="large")
with a:
    pergunta("O preço anda antes da notícia?", "Sim.")
    st.markdown(
        f"- O pregão que acabou de fechar acompanha as notícias publicadas à noite: "
        f"r = {br(td['A1_P3']['r'])}, {p_txt(td['A1_P3']['p_holm'], 'p de Holm')} (n = {numero(td['A1_P3']['n'])}).\n"
        f"- A hora anterior acompanha as notícias publicadas durante o pregão: "
        f"r = {br(td['A1_P5']['r'])}, {p_txt(td['A1_P5']['p_holm'], 'p de Holm')} (n = {numero(td['A1_P5']['n'])}).")
with b:
    pergunta("A notícia antecipa o preço?", "Não, em nenhuma resolução.")
    st.markdown(
        f"- Notícia da noite → abertura seguinte: r = {br(td['A1_P2']['r'])} ({p_txt(td['A1_P2']['p'])}).\n"
        f"- Notícia do pregão → hora seguinte: r = {br(td['A1_P4']['r'])} ({p_txt(td['A1_P4']['p'])}).\n"
        f"- Notícias do dia → abertura seguinte, todas as {numero(td['P1']['n'])}: r = {br(td['P1']['r'])} "
        f"({p_txt(td['P1']['p'])}; menor efeito detectável {br(td['P1']['mde'])}).")
st.markdown(
    "Com barras de **1 e de 5 minutos**, nenhum teste foi significativo, nos dois sentidos. Com só 20 "
    "pregões de dados de minuto, o menor efeito que o teste enxergaria era de cerca de 0,11 a 0,13: "
    "efeitos menores do que isso não podem ser descartados.")

# ── Hora a hora ─────────────────────────────────────────
st.markdown("## Hora a hora em volta da notícia")
col_g, col_t = st.columns([1.35, 1], gap="large")
with col_g:
    mostrar(G.perfil_horario(R.perfil_horario()), "hora")
    fonte("etapa E17 do verificador (notícias publicadas no pregão, terços extremos de sentimento).")
with col_t:
    ex = R.exploratorio_abertura()
    st.markdown(
        "As notícias publicadas durante o pregão foram separadas em mais positivas (terço de cima) e "
        "mais negativas (terço de baixo). O gráfico soma o retorno anormal hora a hora, começando três "
        "horas antes.")
    st.markdown(
        "Antes das notícias positivas o preço **já tinha subido**; antes das negativas, **já tinha caído**. "
        "Depois da publicação, as linhas quase não se mexem.")
    st.markdown(
        f"Numa análise exploratória (decidida depois de ver os resultados, por isso não confirmatória), "
        f"o movimento da abertura até a hora da notícia acompanhou o sentimento (r = {br(ex['antes']['r'])}; "
        f"n = {numero(ex['antes']['n'])}), e o movimento da notícia até o fechamento, não "
        f"(r = {br(ex['depois']['r'])}; {p_txt(ex['depois']['p'])}).")

# ── Minuto a minuto ─────────────────────────────────────
st.markdown("## Minuto a minuto")
col_g2, col_t2 = st.columns([1.35, 1], gap="large")
with col_g2:
    mostrar(G.perfil_minuto(R.perfil_minuto()), "minuto")
    fonte("etapa E27 do verificador (barras de 1 minuto, 20 pregões).")
with col_t2:
    st.markdown(
        "Na escala de minutos, as faixas de incerteza (intervalo de 95%) das notícias positivas e "
        "negativas se sobrepõem o tempo todo: não aparece reação clara nem antes nem depois.")
    st.markdown(
        "Isso combina com a hora a hora: se o preço já tinha andado **horas** antes, não sobra quase nada "
        "para acontecer nos minutos seguintes. Também pode ser que a reação seja mais rápida do que 1 "
        "minuto, a menor resolução disponível.")

# ── Leitura ─────────────────────────────────────────────
st.markdown("## O que isso quer dizer")
st.markdown(
    "Quando a matéria de jornal é publicada, o preço **já se moveu**, e a matéria não antecipa o "
    "movimento seguinte. Três ideias explicam esse padrão:\n\n"
    "1. **Eficiência de mercado** (Fama, 1970): a informação pública entra no preço rapidamente.\n"
    "2. **Quem se informa primeiro negocia primeiro** (Grossman e Stiglitz, 1980): o preço se move pelas "
    "ordens de quem obteve a informação antes de ela virar notícia.\n"
    "3. **A regra da CVM** (Resolução nº 44): a empresa divulga o fato relevante de forma ampla, de "
    "preferência fora do pregão. A matéria jornalística, muitas vezes, repercute uma informação que o "
    "mercado já recebeu.")
st.warning(
    "Limite declarado: com o FinBERT-PT-BR no lugar do léxico, a associação da hora anterior com as "
    f"notícias do pregão não se manteve ({p_txt(td['A1_P5']['p_finbert'])}). A da noite se manteve "
    f"({p_txt(td['A1_P3']['p_finbert'])}). E o estudo é observacional: mostra a ordem no tempo, não "
    "prova causa.", icon=":material/info:")

como_ler(
    "- Cada linha é um teste. A bolinha é a correlação; **cheia** quando p < 0,05, **vazada** quando não.\n"
    "- A **faixa cinza** em volta do zero é o tamanho de efeito pequeno demais para aquele teste enxergar. "
    "Uma bolinha vazada dentro da faixa quer dizer: \"se existir efeito, é menor que isso\".\n"
    "- Troque a medida para FinBERT-PT-BR e veja quais conclusões se mantêm com outra forma de medir o sentimento.")
