# -*- coding: utf-8 -*-
"""Início: a pergunta, a resposta em uma frase e o mapa do painel."""
import streamlit as st

from modulos import graficos as G
from modulos import resultados as R
from modulos.interface import cartao, como_ler, fonte, mostrar, numero, pergunta

ng = R.numeros_gerais()

st.caption("SENTIMENTO DE NOTÍCIAS E RETORNO DE AÇÕES: análise de risco de carteiras na bolsa brasileira")
st.markdown("# O tom das notícias acompanha o preço das ações? E quem vem primeiro?")

col_a, col_b = st.columns([1.15, 1], gap="large")
with col_a:
    st.markdown("A pesquisa transformou 18 mil manchetes sobre oito empresas da B3 em números, de −1 "
                "(muito negativa) a +1 (muito positiva), e comparou esses números com o preço das ações, "
                "do dia inteiro até o minuto.")
    st.markdown("<div class='frase'>A manchete chega depois do preço.</div>", unsafe_allow_html=True)
    st.markdown(
        "Notícia e preço andam juntos no mesmo dia, e isso é da própria empresa. Mas, quando dá para ver "
        "a hora exata, o preço se mexe **antes** da publicação, e a notícia não antecipa o movimento "
        "seguinte. É como o relâmpago e o trovão: o relâmpago (o preço) chega primeiro; o trovão (a "
        "manchete) chega depois e conta que houve um relâmpago.")
    st.markdown("Isso é o que prevê a **hipótese de eficiência de mercado** (Fama, 1970): a informação "
                "pública entra no preço rápido, muitas vezes antes de virar matéria de jornal.")
with col_b:
    mostrar(G.perfil_horario(R.perfil_horario()), "hero")
    st.caption("Retorno da ação, hora a hora, em volta das notícias publicadas durante o pregão. "
               "O preço já tinha subido antes das notícias positivas e caído antes das negativas; "
               "depois da publicação, quase nada muda.")
    fonte("etapa E17 do verificador (notícias publicadas no pregão, com horário exato; terços extremos de sentimento).")

st.markdown("")
c1, c2, c3, c4 = st.columns(4)
with c1:
    cartao("notícias analisadas", numero(ng["noticias"]), "8 ações · jan/2024 a set/2026")
with c2:
    cartao("com horário exato", numero(ng["com_horario"]),
           f"{numero(ng['horario_wordpress'])} pelos sites · {numero(ng['horario_google'])} pelo agregador")
with c3:
    cartao("testes registrados", numero(ng["testes_registrados"]), "inclusive os que deram nulo")
with c4:
    cartao("saídas conferidas", f"{ng['verificacao_ok']} de {ng['verificacao_total']}",
           "o verificador refaz tudo e compara")

st.markdown("## As três perguntas, e o que os dados responderam")
p1, p2, p3 = st.columns(3, gap="large")
with p1:
    pergunta("1 · Existe relação?",
             f"Sim, no mesmo pregão: {ng['d0_rejeita']} de {ng['ativos']} ações. No dia seguinte, nenhuma.")
    st.page_link("paginas/mesmo_dia.py", label="Ver o resultado por ação", icon=":material/arrow_forward:")
with p2:
    pergunta("2 · A relação é real?",
             "Sim. Resiste ao desconto do mercado e ao placebo, e se repete em outro período e em ações menores.")
    st.page_link("paginas/robustez.py", label="Ver os cinco controles", icon=":material/arrow_forward:")
with p3:
    pergunta("3 · Quem vem primeiro?",
             "O preço. A notícia acompanha o que já aconteceu e não prevê o que vem depois.")
    st.page_link("paginas/direcao.py", label="Ver os testes de direção", icon=":material/arrow_forward:")

st.markdown("## Como a pesquisa foi feita")
etapas = [
    ("1. Coleta", "Manchetes do Google Notícias e preços do Yahoo Finance: diários, de hora em hora e de minuto em minuto."),
    ("2. Medida", "Cada manchete vira um número de −1 a +1 com um dicionário de 266 termos financeiros."),
    ("3. Alinhamento", "Cada notícia é ligada ao pregão em que poderia ter efeito; 4.998 têm hora e minuto."),
    ("4. Testes", "Correlação de Pearson, p-valor por permutação (10.000 embaralhamentos) e correção de Holm."),
    ("5. Direção", "Compara o preço antes e depois da notícia, do dia inteiro até 1 minuto."),
    ("6. Controles", "Retorno anormal, placebo entre empresas, réplicas em outro período e em ações menores."),
]
cols = st.columns(3)
for i, (t, d) in enumerate(etapas):
    with cols[i % 3]:
        cartao(t, "", d)
        st.markdown("")
st.markdown(
    "Antes de cada rodada de testes, as hipóteses e as regras foram **escritas e datadas** (pré-registro), "
    "para que ninguém, nem os próprios autores, pudesse ajustar a análise depois de ver o resultado. "
    "Os dados foram congelados com impressão digital, e um verificador refaz as 32 etapas da análise "
    "em qualquer computador.")

como_ler(
    "- **Sentimento** é o tom da manchete, de −1 (muito negativa) a +1 (muito positiva).\n"
    "- **Correlação (r)** mede se dois números sobem e descem juntos: 0 é nenhuma relação, 1 é relação perfeita. "
    "Em finanças, r = 0,13 já é um efeito real, mas pequeno: aparece só com milhares de observações.\n"
    "- **p-valor** é a chance de um resultado tão forte aparecer só por acaso. Abaixo de 0,05 (5%), "
    "o resultado é chamado de significativo.\n"
    "- **D+0, D+1, D−1**: o retorno do mesmo pregão da notícia, do dia seguinte e do dia anterior.\n"
    "- **Retorno anormal**: o quanto a ação andou além do que o mercado inteiro (Ibovespa) andou.",
    titulo="Cinco palavras para entender o painel")
