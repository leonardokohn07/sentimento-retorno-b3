# -*- coding: utf-8 -*-
"""Pergunta 2: a relação é real? Os controles que tentam derrubá-la."""
import streamlit as st

from modulos import graficos as G
from modulos import resultados as R
from modulos.graficos import br, p_txt
from modulos.interface import cartao, como_ler, fonte, mostrar, numero, pergunta, tabela
from modulos.visual import MUDO

st.markdown("# 2 · A relação é real?")
pergunta("A pergunta", "A correlação do mesmo dia pode ser coincidência, ou ter outra explicação. Ela resiste?")
st.markdown(
    "Um bom resultado precisa sobreviver a quem tenta derrubá-lo. Cada controle abaixo foi pensado para "
    "uma explicação alternativa, e todos foram **escritos antes de rodar** (pré-registro). Se qualquer um "
    "falhasse, a conclusão mudaria.")

ctl = R.controles()
mostrar(G.controles(ctl), "controles")
fonte("etapas E12, E13, E14, E16 e E28 do verificador. Réplicas com p corrigido por Holm.")

for c in ctl:
    p_rot = p_txt(c["p_holm"], "p de Holm") if c["p_holm"] is not None else p_txt(c["p"])
    n_txt = f" · n = {numero(c['n'])}" if c["n"] else ""
    with st.container(border=True):
        a, b = st.columns([2.2, 1], vertical_alignment="center")
        with a:
            st.markdown(f"**{c['teste']}**  \n<span style='color:{MUDO}'>{c['pergunta']}</span>",
                        unsafe_allow_html=True)
        with b:
            st.markdown(f"**r = {br(c['r'])}** · {p_rot}{n_txt}  \n✓ {c['leitura']}")

# ── Placebo ─────────────────────────────────────────────
st.markdown("## O placebo: notícia de uma empresa com o preço de outra")
pl = R.placebo()
col_g, col_t = st.columns([1.35, 1], gap="large")
with col_g:
    mostrar(G.placebo(pl["matriz"]), "placebo")
    fonte("etapa E13 do verificador (retorno anormal, mesmo dia).")
with col_t:
    st.markdown(
        "Se a correlação viesse de um \"humor geral\" do mercado (dias de notícias boas para todo mundo), "
        "a notícia da Petrobras também acompanharia o preço da Ambev. O teste cruza as notícias de cada "
        "empresa com o retorno de todas as outras.")
    st.markdown(
        f"- **Diagonal** (notícia e preço da mesma empresa): média **{br(pl['propria'])}**.\n"
        f"- **Fora da diagonal** (54 pares de setores diferentes): média **{br(pl['cruzada'])}**, "
        f"igual a zero ({p_txt(pl['p_cruzada'])}).\n"
        f"- A diferença ({br(pl['diferenca'])}) tem {p_txt(pl['p_diferenca'])}.")
    st.markdown("Conclusão: a relação é da **notícia da própria empresa**. Os pares entre os dois bancos "
                f"(Bradesco e Itaú) ficaram de fora da média, porque são do mesmo setor ({br(pl['bancos'])}).")

# ── Manchetes de preço ──────────────────────────────────
st.markdown("## As manchetes que só relatam o preço")
reg = R.registro_de_testes()
e12 = reg[(reg["etapa"] == "E12") & (reg["teste"] == "AGRUPADO D+0")].reset_index(drop=True)
rot = ["todas as notícias", "sem as que só relatam o preço", "só as que relatam o preço"]
fig = G.barras_relato(rot, e12["r"].tolist(), e12["n"].astype(int).tolist())
mostrar(fig, "relato")
fonte("etapa E12 do verificador. O teste confirmatório é o do meio.")
st.markdown(
    "Manchetes como \"Vale dispara 5%\" descrevem o próprio preço: é claro que acompanham o retorno. "
    "Elas são só 584 das 18.463 notícias, mas têm correlação de 0,57. Sem elas, a associação cai para "
    "0,073 e continua significativa. Ou seja: existe relação também nas notícias que trazem informação "
    "nova, mas parte do resultado vinha de jornal contando o que o preço já tinha feito.")

# ── Réplicas ────────────────────────────────────────────
st.markdown("## As réplicas: o resultado se repete fora da amostra?")
r1, r2 = st.columns(2, gap="large")
rep = next(c for c in ctl if c["chave"] == "replica")
sc = next(c for c in ctl if c["chave"] == "smallcaps")
with r1:
    cartao("outro período · out/2021 a dez/2023", f"r = {br(rep['r'])}",
           f"{p_txt(rep['p_holm'], 'p de Holm')} · n = {numero(rep['n'])} · mesmas 8 ações, dados novos")
with r2:
    cartao("ações menores · 8 small caps", f"r = {br(sc['r'])}",
           f"{p_txt(sc['p_holm'], 'p de Holm')} · n = {numero(sc['n'])} · {', '.join(R.smallcaps_ativos())}")
st.markdown(
    "Muitos resultados de finanças não se repetem quando alguém refaz o estudo com outros dados "
    "(Hou, Xue e Zhang, 2020). Este se repetiu duas vezes, com dados que não tinham sido usados antes. "
    "Nas ações menores a relação é **mais forte**, o que combina com a literatura: empresas pequenas "
    "são mais difíceis de avaliar, e a notícia pesa mais.")

# ── Os nulos ────────────────────────────────────────────
st.markdown("## Os testes que deram nulo (e também contam)")
gr = R.granger()
n1, n2 = st.columns([1, 1.2], gap="large")
with n1:
    st.markdown(
        f"**Causalidade de Granger** (o passado de uma série ajuda a prever a outra?), com 5 dias de "
        f"defasagem: **{int((gr['sent_para_ret'] < 0.05).sum())} de 8** ativos no sentido "
        f"sentimento → retorno e **{int((gr['ret_para_sent'] < 0.05).sum())} de 8** no sentido "
        f"retorno → sentimento. A regra escrita antes exigia 3 de 8.")
    st.markdown(
        "**Notícias de fim de semana** contra o retorno de segunda-feira: nulo também. Nenhuma das "
        "defasagens de dias inteiros mostrou a notícia prevendo o preço.")
    fonte("etapas E09 a E11 e E15 do verificador.")
with n2:
    tabela(gr.rename(columns={"sent_para_ret": "p sentimento → retorno",
                              "ret_para_sent": "p retorno → sentimento"}),
           {"p sentimento → retorno": 4, "p retorno → sentimento": 4})

como_ler(
    "Um teste \"nulo\" não prova que o efeito é zero: prova que, se existir, é menor do que o teste "
    "consegue enxergar. Por isso o estudo informa o **menor efeito detectável** de cada teste e "
    "registra todos eles, inclusive os nulos, na página de verificação.",
    titulo="O que significa um resultado nulo?")
