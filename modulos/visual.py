# -*- coding: utf-8 -*-
"""
visual.py
---------
Identidade visual do projeto, num lugar só.

Por que este arquivo existe
    Até 28/09/2026 cada tela escolhia a sua cor, o seu emoji e o seu
    espaçamento. O resultado era uma interface que parecia montada por
    pessoas diferentes — e a maior parte dos gráficos saía com a paleta
    padrão do Plotly, a mesma de qualquer tutorial.

    Agora a paleta, a tipografia e o estilo dos gráficos vivem aqui, e todo
    o resto do projeto importa daqui. Trocar a identidade inteira é mexer
    num arquivo.

Tema escuro
    O projeto roda em fundo escuro. Cores de dado escolhidas para ESTE fundo
    (e não convertidas de um tema claro): azul #3987e5 para o resultado que
    rejeita H0, vermelho #e66767 para o que não rejeita.

A paleta foi validada para daltonismo e contraste
    O par azul/vermelho sobre o fundo escuro: separação ΔE 19,2 em
    protanopia e 29,0 em visão normal (mínimos de 8 e 15), ambos acima de
    3:1 de contraste com o fundo. O verde escuro do banner (#0c5a4e) não
    serve como cor de dado — reprova em luminosidade e saturação — e fica
    reservado para uso de marca.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────────────────
TINTA = "#e9ecf1"          # texto principal
TINTA2 = "#b9c0cc"         # texto secundário
MUDO = "#8c95a3"           # legendas, eixos, notas
LINHA = "#272d38"          # bordas e réguas
GRADE = "#222836"          # grade dos gráficos
FUNDO = "#0f1218"          # fundo da página
FUNDO2 = "#161b24"         # blocos de apoio

SERIE_1 = "#3987e5"        # rejeita H0
SERIE_2 = "#e66767"        # não rejeita / inconclusivo
SERIE_3 = "#199e70"
SERIE_4 = "#c98500"
CATEGORICA = [SERIE_1, SERIE_2, SERIE_3, SERIE_4]

SIGNIFICATIVO = SERIE_1
INCONCLUSIVO = SERIE_2

SERIF = "Georgia, 'Times New Roman', serif"
SANS = ("system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', "
        "Arial, sans-serif")


# ─────────────────────────────────────────────────────────
# GRÁFICOS (Plotly)
# ─────────────────────────────────────────────────────────

def tema_plotly():
    """Registra o tema do projeto e o deixa como padrão.

    Depois disto, todo go.Figure criado no projeto já nasce com a paleta,
    a tipografia e a grade certas — sem repetir configuração em cada figura.
    """
    import plotly.graph_objects as go
    import plotly.io as pio

    eixo = dict(
        showgrid=True, gridcolor=GRADE, gridwidth=1,
        zeroline=False, linecolor=LINHA, linewidth=1,
        ticks="outside", ticklen=4, tickcolor=LINHA,
        tickfont=dict(size=11, color=MUDO),
        title=dict(font=dict(size=12, color=MUDO)),
    )
    pio.templates["investai"] = go.layout.Template(
        layout=go.Layout(
            colorway=CATEGORICA,
            font=dict(family=SANS, size=12, color=TINTA2),
            paper_bgcolor=FUNDO, plot_bgcolor=FUNDO,
            xaxis=eixo, yaxis=eixo,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11, color=TINTA2)),
            hoverlabel=dict(bgcolor=FUNDO, bordercolor=LINHA,
                            font=dict(family=SANS, size=12, color=TINTA)),
            title=dict(font=dict(family=SERIF, size=16, color=TINTA), x=0),
        )
    )
    pio.templates.default = "investai"


# ─────────────────────────────────────────────────────────
# INTERFACE (Streamlit)
# ─────────────────────────────────────────────────────────

CSS = f"""
<style>
.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }}

h1, h2, h3, h4 {{ font-family: {SERIF}; color: {TINTA}; letter-spacing: -0.01em; }}
h1 {{ font-size: 1.62rem; font-weight: 700; }}
h2 {{ font-size: 1.20rem; padding-top: 0.6rem; }}
h3 {{ font-size: 1.02rem; }}
p, li, label, .stMarkdown {{ color: {TINTA2}; }}

/* números das métricas: tipografia de dado, não de texto corrido */
[data-testid="stMetricValue"] {{
    font-family: {SERIF}; font-size: 1.75rem; color: {TINTA};
    font-variant-numeric: tabular-nums;
}}
[data-testid="stMetricLabel"] p {{ font-size: 0.78rem; color: {MUDO}; }}
[data-testid="stMetric"] {{ border-left: 2px solid {LINHA}; padding: 2px 0 2px 14px; }}

/* réguas finas no lugar de caixas */
hr {{ border-color: {LINHA}; margin: 1.6rem 0 1.2rem; }}
[data-testid="stExpander"] {{ border: 1px solid {LINHA}; border-radius: 4px; }}
[data-testid="stExpander"] summary {{ font-size: 0.86rem; color: {MUDO}; }}

/* tabelas: números alinhados e cabeçalho discreto */
[data-testid="stDataFrame"] {{ font-variant-numeric: tabular-nums; }}
[data-testid="stTable"] td, [data-testid="stDataFrame"] td {{ color: {TINTA2}; }}

[data-testid="stAlert"] {{ border-radius: 4px; font-size: 0.88rem; }}
.stButton button {{ border-radius: 4px; font-weight: 600; }}
.cab-fonte {{ font-size: 0.78rem; color: {MUDO}; margin-top: 0.4rem; }}
</style>
"""


def aplicar_estilo():
    """Chame uma vez, logo depois de st.set_page_config()."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
    tema_plotly()


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    """Cabeçalho da aplicação, com espaço reservado para a logo.

    A logo é opcional: se existir assets/logo.png (ou .svg), aparece à
    esquerda do título. Enquanto não existir, o cabeçalho fica só com a
    tipografia — sem espaço vazio e sem precisar mexer no código depois.
    """
    import streamlit as st

    logo = None
    for nome in ("logo.png", "logo.svg", "logo.jpg"):
        caminho = RAIZ / "assets" / nome
        if caminho.exists():
            logo = str(caminho)
            break

    if logo:
        col_logo, col_txt = st.columns([1, 11], vertical_alignment="center")
        with col_logo:
            st.image(logo, width=54)
        alvo = col_txt
    else:
        alvo = st.container()

    with alvo:
        st.markdown(f"# {titulo}")
        if subtitulo:
            st.markdown(f"<div class='cab-fonte'>{subtitulo}</div>",
                        unsafe_allow_html=True)
    st.markdown("---")
