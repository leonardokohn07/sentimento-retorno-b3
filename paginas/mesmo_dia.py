# -*- coding: utf-8 -*-
"""Pergunta 1: existe relação entre o sentimento das notícias e o retorno da ação?"""
import time

import numpy as np
import streamlit as st

from modulos import congelados as C
from modulos import graficos as G
from modulos import resultados as R
from modulos.graficos import br, p_txt
from modulos.interface import como_ler, fonte, mostrar, numero, pergunta, sem_dados, tabela

tab = R.por_ativo()
ng = R.numeros_gerais()
ag = R.agrupado_d0()

st.markdown("# 1 · Existe relação?")
pergunta("A pergunta", "Nos dias em que as notícias sobre uma empresa são mais positivas, a ação dela sobe mais?")
st.markdown(
    "Para cada ação e cada pregão, calculamos o **sentimento médio** das notícias daquele dia e o "
    "**retorno** da ação (quanto o preço variou). Depois medimos a correlação entre os dois em três "
    "momentos: no mesmo pregão da notícia (**D+0**), no seguinte (**D+1**) e no anterior (**D−1**).")

mostrar(G.por_ativo(tab), "por_ativo")
fonte(f"etapa E03 do verificador · {numero(ng['pregoes_com_noticia'])} pregões com notícia, "
      f"{numero(ng['noticias'])} notícias, jan/2024 a set/2026.")

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    pergunta("Mesmo pregão (D+0)", f"{ng['d0_rejeita']} de 8 ações com relação significativa")
with c2:
    pergunta("Dia seguinte (D+1)", f"{ng['d1_rejeita']} de 8: a notícia não prevê o dia seguinte")
with c3:
    pergunta("Dia anterior (D−1)", f"{ng['dm1_rejeita']} de 8: um primeiro sinal de que o preço vem antes")

st.markdown(
    f"Com os 8 ativos agrupados (todos os pares ação-pregão juntos), a correlação no "
    f"mesmo pregão é **r = {br(ag['r'])}** ({p_txt(ag['p'])}; n = {numero(ag['n'])}). É uma correlação "
    f"**pequena**: o sentimento explica menos de 2% da variação do retorno. Mas é muito difícil que ela "
    f"tenha aparecido por acaso.")

with st.expander("Tabela completa por ação"):
    t = tab.copy()
    tabela(
        t.rename(columns={"r_dm1": "r D−1", "p_dm1": "p D−1", "r_d0": "r D+0", "p_d0": "p D+0",
                          "p_perm_d0": "p D+0 (permutação)", "r_d1": "r D+1", "p_d1": "p D+1",
                          "n": "pregões"}),
        {c: 4 for c in ["r D−1", "p D−1", "r D+0", "p D+0", "p D+0 (permutação)", "r D+1", "p D+1"]})
    st.caption("p clássico: fórmula do teste de Pearson. p de permutação: 10.000 embaralhamentos (etapa E04). "
               "Os dois levam à mesma conclusão em todos os ativos.")

como_ler(
    "- Cada barra é a correlação (r) de uma ação. **Azul** = significativa (p < 0,05); **cinza** = não.\n"
    "- Passe o mouse em cima da barra para ver o p-valor e o número de pregões.\n"
    "- Em D+0, quase todas as barras são azuis; em D+1, nenhuma. A relação acontece **no mesmo dia** e some depois.")

# ── Curva de defasagem ──────────────────────────────────
st.markdown("## Do dia D−5 ao dia D+5")
cd = R.curva_defasagem()
opcoes = ["AGRUPADO"] + R.ATIVOS
sel = st.segmented_control("Ativo", opcoes, default="AGRUPADO",
                           format_func=lambda a: "8 agrupados" if a == "AGRUPADO" else a)
sel = sel or "AGRUPADO"
mostrar(G.curva_defasagem(cd, sel), "curva")
fonte("etapa E06 do verificador (pré-registro de 28/09/2026). D+4 não está na lista de defasagens "
      "do script (scripts/14_curva_de_defasagem.py).")
st.markdown(
    "A correlação tem um pico no mesmo dia, um valor menor no dia anterior e nenhum efeito positivo nos "
    "dias seguintes. Se a notícia antecipasse o preço, as barras de D+1 em diante seriam azuis.")

with st.expander("O dia anterior (D−1) é só arrasto do mesmo dia?"):
    w = R.williams()
    st.markdown(
        "Se o retorno de hoje se parece com o de ontem (autocorrelação), uma relação real em D+0 aparece "
        "\"de arrasto\" em D−1. O **teste de Williams** compara as duas correlações levando isso em conta. "
        f"Resultado: D+0 foi estatisticamente maior que D−1 em só **{int((w['williams_p'] < 0.05).sum())} de 8** "
        "ativos (VALE3). Ou seja, os dados não separam bem o dia anterior do mesmo dia, e por isso a direção "
        "foi investigada com o horário exato das notícias (página 3).")
    tabela(w[["ativo", "n", "r_dm1", "r_d0", "autocorr", "williams_t", "williams_p"]].rename(
        columns={"r_dm1": "r D−1", "r_d0": "r D+0", "autocorr": "autocorrelação", "williams_t": "t de Williams",
                 "williams_p": "p"}), {"r D−1": 4, "r D+0": 4, "autocorrelação": 4, "t de Williams": 3, "p": 4})
    fonte("etapa E05 do verificador.")

# ── Refazer ao vivo ─────────────────────────────────────
st.markdown("## Refaça a conta agora")
if not C.fonte():
    sem_dados()
else:
    st.markdown(
        f"O botão abaixo refaz, neste computador e agora, as etapas E03 e E04 a partir do "
        f"**{C.descricao_fonte()}**: monta a série de cada ação, calcula as correlações e faz os "
        f"80.000 embaralhamentos do teste de permutação (10.000 por ação, semente 42). Depois compara "
        f"cada número com a referência do relatório.")
    if st.button("Refazer os testes do mesmo dia", type="primary", icon=":material/play_arrow:"):
        barra = st.progress(0.0, text="Montando as séries diárias…")
        t0 = time.time()
        novo = C.refazer_resultado_original()

        def avancar(fr, ativo):
            barra.progress(min(fr, 1.0), text=f"Embaralhando o sentimento… {ativo}")

        perm = C.refazer_permutacoes(avancar)
        barra.empty()
        st.session_state["refeito"] = (novo, perm, time.time() - t0)

    if "refeito" in st.session_state:
        novo, perm, seg = st.session_state["refeito"]
        comp = tab[["ativo", "r_d0", "p_d0", "p_perm_d0"]].merge(novo[["ativo", "r_d0", "p_d0"]],
                                                                  on="ativo", suffixes=("_ref", "_agora"))
        comp["p_perm_agora"] = comp["ativo"].map({k: v["p"] for k, v in perm.items()})
        iguais = (np.isclose(comp["r_d0_ref"], comp["r_d0_agora"].round(4))
                  & np.isclose(comp["p_d0_ref"], comp["p_d0_agora"].round(4))
                  & np.isclose(comp["p_perm_d0"], comp["p_perm_agora"].round(4)))
        comp["confere"] = np.where(iguais, "✓ igual", "✗ diferente")
        if iguais.all():
            st.success(f"Refeito em {br(seg, 1)} s: os {len(comp)} ativos deram exatamente os números do relatório.",
                       icon=":material/check_circle:")
        else:
            st.warning("Algum número saiu diferente da referência. Com a pasta dados/ (e não o pacote congelado), "
                       "isso é esperado, porque os preços foram atualizados.", icon=":material/warning:")
        tabela(comp.rename(columns={
            "r_d0_ref": "r D+0 (relatório)", "r_d0_agora": "r D+0 (agora)", "p_d0_ref": "p (relatório)",
            "p_d0_agora": "p (agora)", "p_perm_d0": "p permutação (relatório)", "p_perm_agora": "p permutação (agora)"}),
            {c: 4 for c in ["r D+0 (relatório)", "r D+0 (agora)", "p (relatório)", "p (agora)",
                            "p permutação (relatório)", "p permutação (agora)"]})
        at = st.segmented_control("Ver os embaralhamentos de:", list(perm), default="VALE3", key="perm_at") or "VALE3"
        mostrar(G.permutacao(perm[at]["nulos"], perm[at]["r"], at, perm[at]["p"]), "perm_hist")
        st.caption("Cada barra cinza conta quantos dos 10.000 embaralhamentos deram aquela correlação. "
                   "A linha azul é a correlação verdadeira: quanto mais longe do monte, menos provável que "
                   "seja acaso.")
