# -*- coding: utf-8 -*-
"""Como medimos o sentimento: o léxico ao vivo, o dicionário e a validação da medida."""
import numpy as np
import pandas as pd
import streamlit as st

from modulos import congelados as C
from modulos import graficos as G
from modulos import resultados as R
from modulos.analise.sentimento import (ATENUADORES, INTENSIFICADORES, LEXICO, NEGADORES,
                                        analisar_lexico)
from modulos.graficos import br
from modulos.interface import cartao, como_ler, fonte, mostrar, numero, tabela

st.markdown("# Como transformamos uma manchete em número")
st.markdown(
    "Não dá para calcular correlação com texto. Por isso cada manchete recebe uma nota de **−1** "
    "(muito negativa) a **+1** (muito positiva). A medida principal é um **léxico**: um dicionário de "
    "termos do mercado financeiro, cada um com um peso, mais regras para negação (\"não teve lucro\") "
    "e intensidade (\"forte alta\", \"leve queda\"). A vantagem é a transparência: dá para ver "
    "exatamente quais palavras produziram a nota.")

# ── 1. Ao vivo ──────────────────────────────────────────
st.markdown("## Teste você mesmo")
EXEMPLOS = ["Vale despenca 8%", "Petrobras não teve lucro no trimestre",
            "Magazine Luiza tem leve queda após balanço", "WEG tem forte alta e lucro recorde",
            "Itaú anuncia novo diretor"]
if "manchete" not in st.session_state:
    st.session_state["manchete"] = EXEMPLOS[3]


def _usar_exemplo():
    if st.session_state.get("exemplo"):
        st.session_state["manchete"] = st.session_state["exemplo"]


def _sortear():
    n = C.noticias()
    st.session_state["manchete"] = str(n["manchete"].sample(1).iloc[0])
    st.session_state["exemplo"] = None


st.pills("Exemplos do relatório (Quadro 7):", EXEMPLOS, key="exemplo", on_change=_usar_exemplo)
col_txt, col_bt = st.columns([5, 1.4], vertical_alignment="bottom")
with col_txt:
    texto = st.text_input("Digite uma manchete:", key="manchete")
with col_bt:
    st.button("Sortear manchete real", icon=":material/casino:", on_click=_sortear,
              disabled=not C.fonte(), width="stretch",
              help="Pega uma das 18.463 manchetes do estudo, ao acaso.")

res = analisar_lexico(texto)
s = res["score_polaridade"]
classe = res["classificacao"]

a, b = st.columns([1, 2.2], gap="large")
with a:
    cartao("nota do léxico", br(s, 2, sinal=True) if res["n_termos"] else "0,00",
           f"{classe} · {res['n_termos']} termo(s) encontrado(s)")
    st.markdown("")
    st.caption("Positivo acima de +0,15, negativo abaixo de −0,15, neutro no meio.")
with b:
    if res["n_termos"]:
        mostrar(G.contribuicoes(res["termos_achados"]), "contrib")
    else:
        st.info("Nenhum termo do dicionário nesta manchete: a nota é 0 (neutra). "
                "Isso aconteceu com 62,6% das manchetes do estudo, e é uma das limitações da medida.",
                icon=":material/info:")

if res["n_termos"]:
    with st.expander("Ver a conta passo a passo", expanded=True):
        linhas = []
        for t in res["termos_achados"]:
            regra = []
            if t["multiplicador"] != 1:
                regra.append(f"× {br(t['multiplicador'], 2)} (intensidade)")
            if t["negado"]:
                regra.append("× (−0,8) (negação)")
            bruto = t["peso_base"] * t["multiplicador"] * (-0.8 if t["negado"] else 1)
            if abs(bruto) > 1:
                regra.append(f"daria {br(bruto, 2, sinal=True)}, limitado a ±1")
            linhas.append({"termo": t["termo"], "peso no dicionário": br(t["peso_base"], 2, sinal=True),
                           "regras aplicadas": ", ".join(regra) or "nenhuma",
                           "valor final (v)": br(t["valor_final"], 2, sinal=True)})
        st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")
        v = np.array([t["valor_final"] for t in res["termos_achados"]])
        num = " + ".join(f"({br(x, 2)})·{br(abs(x), 2)}" for x in v)
        den = " + ".join(br(abs(x), 2) for x in v)
        st.markdown("A nota é a média dos valores, ponderada pela força de cada termo, para que o termo "
                    "mais forte domine a manchete (equação 1 do relatório):")
        st.latex(r"s = \frac{\sum_k v_k\,|v_k|}{\sum_k |v_k|}")
        st.markdown(f"s = [{num}] ÷ [{den}] = **{br(s, 2, sinal=True)}**")

fb_pre = C.escores_finbert() if C.fonte() else None
chave = texto.strip()
col1, col2 = st.columns(2)
with col1:
    if fb_pre is not None and chave in fb_pre.index:
        cartao("FinBERT-PT-BR (calculado no estudo)", br(float(fb_pre[chave]), 2, sinal=True),
               "esta manchete faz parte do estudo; escore = P(positivo) − P(negativo)")
with col2:
    if st.toggle("Rodar o FinBERT-PT-BR ao vivo (opcional)",
                 help="Usa o ambiente separado venv_finbert, se existir (criado pelo TESTAR_FINBERT.bat); "
                      "senão, tenta o torch do próprio painel."):
        from modulos import finbert_vivo

        @st.cache_resource(show_spinner="Carregando o FinBERT-PT-BR (na primeira vez pode levar até 1 minuto)…")
        def _modelo():
            return finbert_vivo.carregar()      # se falhar, o erro não fica guardado: dá para tentar de novo

        try:
            mod, erro = _modelo(), None
        except Exception as e:  # noqa: BLE001 — mostrar qualquer motivo na tela
            mod, erro = None, f"{type(e).__name__}: {e}"
        if erro:
            dica = ("" if finbert_vivo.python_do_ambiente_separado() else
                    " Para usar no Windows, rode uma vez o arquivo TESTAR_FINBERT.bat, na pasta do projeto: "
                    "ele cria um ambiente separado só para o FinBERT. Depois, ligue esta opção de novo.")
            st.warning("O modelo não carregou neste computador, então a página segue com o léxico e com os "
                       f"escores do FinBERT já calculados no estudo. Motivo: `{erro[:300]}`.{dica}",
                       icon=":material/warning:")
        else:
            try:
                r = finbert_vivo.pontuar(mod, texto)
                cartao("FinBERT-PT-BR ao vivo", br(r["escore"], 2, sinal=True),
                       f"positivo {br(r['positivo'], 2)} · neutro {br(r['neutro'], 2)} · "
                       f"negativo {br(r['negativo'], 2)}")
                st.caption(finbert_vivo.descricao(mod))
            except Exception as e:  # noqa: BLE001
                _modelo.clear()
                st.warning(f"O FinBERT parou de responder: `{str(e)[:300]}`. Desligue e ligue a opção de novo.",
                           icon=":material/warning:")

# ── 2. O dicionário ─────────────────────────────────────
st.markdown("## O dicionário")
pos = sum(v > 0 for v in LEXICO.values())
neg = sum(v < 0 for v in LEXICO.values())
big = sum(" " in k for k in LEXICO)
c1, c2, c3, c4 = st.columns(4)
with c1:
    cartao("termos", numero(len(LEXICO)), f"{pos} positivos · {neg} negativos · {big} de duas palavras")
with c2:
    cartao("negadores", numero(len(NEGADORES)), "invertem o sinal (× −0,8): não, sem, deixou de…")
with c3:
    cartao("intensificadores", numero(len(INTENSIFICADORES)), "multiplicam o peso (× 1,3 a 1,8): forte, recorde…")
with c4:
    cartao("atenuadores", numero(len(ATENUADORES)), "reduzem o peso (× 0,5 a 0,7): leve, discreto…")
fonte("modulos/analise/sentimento.py, contado agora pelo próprio programa.")

with st.expander("Procurar no dicionário"):
    busca = st.text_input("Palavra:", key="busca_lex", placeholder="ex.: lucro, queda, rebaixa")
    lex = pd.DataFrame([{"termo": k, "peso": v, "tipo": "positivo" if v > 0 else "negativo",
                         "palavras": 2 if " " in k else 1} for k, v in LEXICO.items()])
    if busca:
        from modulos.analise.sentimento import normalizar
        lex = lex[lex["termo"].str.contains(normalizar(busca), regex=False)]
    st.dataframe(lex.sort_values("peso"), hide_index=True, width="stretch", height=300,
                 column_config={"peso": st.column_config.NumberColumn(format="%+.2f")})

# ── 3. A medida acerta? ─────────────────────────────────
st.markdown("## A medida acerta?")
val = R.validacao_medida()
col_g, col_t = st.columns([1.1, 1], gap="large")
with col_g:
    mostrar(G.kappa(val), "kappa")
    fonte(f"etapa E23 do verificador ({val['n']} manchetes com rótulo de referência; intervalo de 95% por bootstrap).")
with col_t:
    st.markdown(
        f"300 manchetes sorteadas (100 de cada classe do léxico) receberam um rótulo de referência. Nas "
        f"{val['n']} em que as duas rodadas de rotulagem concordaram, a nota de cada medida foi comparada "
        f"com o rótulo pelo **kappa de Cohen**, que desconta os acertos que aconteceriam por acaso "
        f"(0 = acaso, 1 = concordância perfeita).")
    st.markdown(
        f"- Léxico: kappa **{br(val['lexico']['kappa'], 2)}**, concordância *razoável*.\n"
        f"- FinBERT-PT-BR, um modelo de linguagem treinado com notícias financeiras brasileiras: "
        f"**{br(val['finbert']['kappa'], 2)}**, *moderada*.\n"
        f"- A diferença (0,14) tem intervalo de {br(val['diferenca_ic'][0], 2)} a "
        f"{br(val['diferenca_ic'][1], 2)}: inclui o zero, então a regra escrita antes "
        f"(trocar de medida só se o intervalo ficasse inteiro acima de zero) manteve o léxico.")
    st.caption("Os rótulos de referência ainda são preliminares (feitos por um anotador automático); "
               "a rotulagem humana às cegas pelos dois autores está em andamento.")

lf = R.lexico_vs_finbert()
fpa = R.finbert_por_ativo()
st.markdown("### E se a medida fosse o FinBERT?")
st.markdown(
    f"A análise inteira foi refeita com o FinBERT no lugar do léxico. As duas notas concordam só em parte "
    f"(correlação de {br(lf['correlacao'], 2)} manchete a manchete, n = {numero(lf['n'])}), mas a conclusão "
    f"principal se mantém: no mesmo pregão, a associação aparece em "
    f"**{int((fpa[fpa.medida == 'lexico']['p D+0'] < 0.05).sum())} de 8** ativos com o léxico e em "
    f"**{int((fpa[fpa.medida == 'finbert']['p D+0'] < 0.05).sum())} de 8** com o FinBERT; no dia seguinte, "
    f"em nenhum com as duas.")
tab = fpa.pivot(index="ativo", columns="medida", values=["r D+0", "p D+0"])
tab.columns = [f"{m} {c}" for c, m in tab.columns]
tab = tab[["lexico r D+0", "lexico p D+0", "finbert r D+0", "finbert p D+0"]].reset_index()
tab.columns = ["ativo", "r léxico", "p léxico", "r FinBERT", "p FinBERT"]
tabela(tab, {c: 4 for c in tab.columns[1:]})
fonte("etapa E24 do verificador (resultado original refeito com cada medida).")

como_ler(
    "Um modelo de linguagem como o FinBERT lê a frase inteira e acerta mais, mas não diz *por que* deu "
    "aquela nota. O léxico erra mais, mas cada nota pode ser conferida palavra por palavra, como na conta "
    "acima. Por isso o estudo usa o léxico como medida principal e o FinBERT como verificação: se a "
    "conclusão dependesse da medida escolhida, ela não seria confiável.",
    titulo="Por que não usar só o modelo de linguagem?")
