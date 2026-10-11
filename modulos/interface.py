# -*- coding: utf-8 -*-
"""
interface.py
------------
Pedaços de tela usados por todas as páginas do dashboard.
"""
import pandas as pd
import streamlit as st

from modulos.visual import LINHA, MUDO, TINTA, TINTA2

CSS_EXTRA = f"""
<style>
.cartao {{ border: 1px solid {LINHA}; border-radius: 6px; padding: 14px 16px 12px; min-height: 118px; }}
.cartao .rotulo {{ font-size: 0.78rem; color: {MUDO}; text-transform: uppercase; letter-spacing: .04em; }}
.cartao .valor {{ font-family: Georgia, serif; font-size: 2.0rem; color: {TINTA}; line-height: 1.15;
                  font-variant-numeric: tabular-nums; margin: 4px 0 2px; }}
.cartao .nota {{ font-size: 0.82rem; color: {TINTA2}; }}
.frase {{ font-family: Georgia, serif; font-size: 1.55rem; color: {TINTA}; line-height: 1.3; margin: .2rem 0 .6rem; }}
.pergunta {{ border-left: 3px solid #3987e5; padding: 4px 0 4px 14px; margin: 6px 0 14px; }}
.pergunta .q {{ font-size: 0.80rem; color: {MUDO}; text-transform: uppercase; letter-spacing: .04em; }}
.pergunta .a {{ font-family: Georgia, serif; font-size: 1.18rem; color: {TINTA}; }}
.fonte-num {{ font-size: 0.76rem; color: {MUDO}; margin-top: 4px; }}
.selo {{ display: inline-block; border: 1px solid {LINHA}; border-radius: 999px; padding: 2px 10px;
         font-size: 0.78rem; color: {TINTA2}; margin-right: 6px; }}
</style>
"""


def preparar_pagina():
    st.markdown(CSS_EXTRA, unsafe_allow_html=True)


def mostrar(fig, chave=None):
    """Plotly com o tema do projeto (theme=None impede o Streamlit de trocar as cores)."""
    st.plotly_chart(fig, theme=None, key=chave, config={"displayModeBar": False, "locale": "pt-BR"})


def cartao(rotulo, valor, nota=""):
    st.markdown(f"<div class='cartao'><div class='rotulo'>{rotulo}</div>"
                f"<div class='valor'>{valor}</div><div class='nota'>{nota}</div></div>",
                unsafe_allow_html=True)


def pergunta(q, a):
    st.markdown(f"<div class='pergunta'><div class='q'>{q}</div><div class='a'>{a}</div></div>",
                unsafe_allow_html=True)


def fonte(texto):
    st.markdown(f"<div class='fonte-num'>Fonte: {texto}</div>", unsafe_allow_html=True)


def como_ler(texto, titulo="Como ler este gráfico"):
    with st.expander(titulo):
        st.markdown(texto)


def numero(x, casas=0):
    """18463 -> '18.463'."""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def sem_dados():
    st.info(
        "Esta parte refaz contas com os dados do estudo, e eles não estão neste computador. "
        "O repositório público não traz as notícias e os preços (são conteúdo de terceiros); "
        "o pacote de dados congelados é entregue pelos autores a quem pedir. "
        "As páginas de resultados continuam funcionando, porque leem a referência do verificador.",
        icon=":material/folder_off:")


def tabela(df, decimais=None, **kw):
    """st.dataframe com vírgula decimal (como no relatório) nas colunas indicadas.

    decimais = {"coluna": casas}. Os números viram texto só na tela; os dados não mudam.
    """
    from modulos.graficos import br
    d = df.copy()
    for col, casas in (decimais or {}).items():
        if col in d:
            d[col] = [br(float(v), casas) if pd.notna(v) else "—" for v in d[col]]
    kw.setdefault("hide_index", True)
    kw.setdefault("width", "stretch")
    st.dataframe(d, **kw)
