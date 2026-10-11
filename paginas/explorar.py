# -*- coding: utf-8 -*-
"""Explorar os dados: as notícias e os preços de cada ativo, com as contas feitas na hora."""
import pandas as pd
import streamlit as st

from modulos import congelados as C
from modulos import graficos as G
from modulos import resultados as R
from modulos.analise.hipotese import regressao_sentimento_retorno
from modulos.analise.sentimento import analisar_lexico
from modulos.graficos import br, p_txt
from modulos.interface import cartao, como_ler, fonte, mostrar, numero, sem_dados

st.markdown("# Explorar os dados")
st.markdown("As notícias e os preços de verdade, ação por ação. Tudo nesta página é calculado na hora, "
            "a partir dos dados do estudo.")

if not C.fonte():
    sem_dados()
    st.stop()

st.caption(f"Lendo: {C.descricao_fonte()}.")

with st.spinner("Carregando 18.463 notícias e os preços…"):
    noticias = C.noticias()
    precos = C.precos_fechamento()

ativo = st.segmented_control("Ação", R.ATIVOS, default="PETR4") or "PETR4"
tk = f"{ativo}.SA"
st.markdown(f"## {ativo} · {R.EMPRESAS[ativo]}")

serie = C.serie_diaria(tk)
nt = noticias[noticias["ativo"] == ativo]
c1, c2, c3, c4 = st.columns(4)
with c1:
    cartao("notícias", numero(len(nt)), "jan/2024 a set/2026")
with c2:
    cartao("pregões com notícia", numero(len(serie)), f"de {numero(len(C.retornos().loc['2024-01-01':]))} pregões no período")
with c3:
    cartao("sentimento médio", br(nt["score_polaridade"].mean(), 2, sinal=True), "de −1 a +1")
with c4:
    cartao("manchetes sem termo do léxico", f"{br(100 * (nt['score_polaridade'] == 0).mean(), 1)}%",
           "nota zero (neutra)")

p = precos[tk].loc["2024-01-01":serie["data"].max()] if tk in precos else pd.Series(dtype=float)
mostrar(G.preco_e_sentimento(p, serie, ativo), "preco")
fonte("Yahoo Finance (preço) e Google Notícias (manchetes), dados congelados em 02/10/2026; sentimento pelo léxico.")

st.markdown("### Sentimento × retorno, pregão a pregão")
lag = st.segmented_control("Comparar o sentimento do pregão D com o retorno de:", [-1, 0, 1], default=0,
                           format_func=lambda k: {-1: "D−1 (dia anterior)", 0: "D+0 (mesmo pregão)",
                                                  1: "D+1 (dia seguinte)"}[k])
lag = 0 if lag is None else lag
reg = regressao_sentimento_retorno(serie, lag=lag)
col_g, col_t = st.columns([1.5, 1], gap="large")
with col_g:
    mostrar(G.dispersao(serie, lag, ativo), "disp")
with col_t:
    sig = reg["p_valor"] < 0.05
    cartao("correlação calculada agora", f"r = {br(reg['r'])}",
           f"{p_txt(reg['p_valor'])} · n = {numero(reg['n_observacoes'])} pregões · "
           + ("significativa" if sig else "não significativa"))
    st.markdown("")
    st.markdown("Cada ponto é um pregão com notícia. A linha âmbar é a reta que melhor passa pelos pontos. "
                "Com correlações do tamanho das deste estudo (0,1 a 0,2), a nuvem parece quase redonda: "
                "o efeito é pequeno e só aparece com centenas de dias.")
    st.caption("É o mesmo número da tabela da página 1 (etapa E03), refeito agora.")

st.markdown("### As manchetes")
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    busca = st.text_input("Procurar palavra na manchete:", placeholder="ex.: lucro, dividendos, queda")
with f2:
    classe = st.selectbox("Classe pelo léxico:", ["todas", "Positivo", "Neutro", "Negativo"])
with f3:
    ordem = st.selectbox("Ordenar por:", ["mais recentes", "mais positivas", "mais negativas"])
v = nt.copy()
if busca:
    v = v[v["manchete"].str.contains(busca, case=False, regex=False)]
if classe != "todas":
    v = v[v["classificacao"] == classe]
v = v.sort_values({"mais recentes": "data", "mais positivas": "score_polaridade",
                   "mais negativas": "score_polaridade"}[ordem], ascending=(ordem == "mais negativas"))
st.caption(f"{numero(len(v))} manchete(s).")
t = v[["data", "data_pregao", "manchete", "fonte", "score_polaridade", "finbert"]].copy()
t["score_polaridade"] = [br(x, 2, sinal=True) for x in t["score_polaridade"]]
t["finbert"] = [br(x, 2, sinal=True) if pd.notna(x) else "—" for x in t["finbert"]]
st.dataframe(
    t.rename(columns={"data": "publicada em", "data_pregao": "pregão", "score_polaridade": "léxico",
                      "finbert": "FinBERT"}),
    hide_index=True, width="stretch", height=380,
    column_config={
        "publicada em": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm", width="medium"),
        "pregão": st.column_config.DateColumn(format="DD/MM/YYYY", width="small"),
        "manchete": st.column_config.TextColumn(width="large"),
        "fonte": st.column_config.TextColumn(width="small"),
        "léxico": st.column_config.TextColumn(width="small"),
        "FinBERT": st.column_config.TextColumn(width="small"),
    })

with st.expander("Por que esta manchete recebeu esta nota?"):
    opcoes = v["manchete"].head(200).tolist()
    if opcoes:
        m = st.selectbox("Escolha uma manchete da lista acima:", opcoes)
        r = analisar_lexico(m)
        if r["termos_achados"]:
            mostrar(G.contribuicoes(r["termos_achados"]), "contrib_exp")
            st.markdown(f"Nota do léxico: **{br(r['score_polaridade'], 2, sinal=True)}** ({r['classificacao']}). "
                        "A conta completa está na página *Como medimos o sentimento*.")
        else:
            st.markdown("Nenhum termo do dicionário nesta manchete: nota 0 (neutra).")

como_ler(
    "- **Publicada em**: data e hora informadas pelo agregador de notícias (às vezes só a data).\n"
    "- **Pregão**: o pregão em que a notícia poderia ter efeito. Notícias publicadas a partir das 17h ou "
    "no fim de semana vão para o dia útil seguinte; as que caem num feriado (dia sem pregão) ficam fora "
    "dos testes diários.\n"
    "- **Léxico** e **FinBERT**: as duas notas, de −1 a +1. A do FinBERT foi calculada no estudo e "
    "serviu de verificação.",
    titulo="O que é cada coluna")
