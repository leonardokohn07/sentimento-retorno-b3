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
    Cores escolhidas PARA fundo escuro, não convertidas de um tema claro.
    Verde #199e70 = rejeita H0. Vermelho #e66767 = não rejeita. Azul
    #3987e5 = dado observado. Âmbar #c98500 = tendência e destaque.

Verde e vermelho juntos: quando pode e quando não pode
    Verde contra vermelho é o pior par possível para quem tem deuteranopia
    (separação ΔE 5,3, abaixo do piso de 8). Por isso eles só aparecem
    juntos onde a COR É REDUNDANTE — na coluna do veredito, onde a célula
    já diz "sim" ou "não" por escrito, e nos textos de conclusão.

    Onde a cor é a única informação — as barras do gráfico de defasagem —
    o par é verde contra CINZA NEUTRO, que se distingue por luminosidade e
    não depende de percepção de matiz. O p-valor impresso sobre cada barra
    é a segunda camada de informação.

    O verde escuro do banner (#0c5a4e) não serve como cor de dado: reprova
    em luminosidade e saturação. Fica reservado para uso de marca.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────────────────
TINTA = "#f3f5f9"          # texto principal (títulos, números)
TINTA2 = "#d6dbe4"         # texto corrido
MUDO = "#9ba4b2"           # legendas, eixos, notas
LINHA = "#2c3341"          # bordas e réguas
GRADE = "#252c39"          # grade dos gráficos
FUNDO = "#0f1218"          # fundo da página
FUNDO2 = "#161b24"         # blocos de apoio

SERIE_1 = "#199e70"        # verde: rejeita H0 / significativo
SERIE_2 = "#e66767"        # vermelho: não rejeita / inconclusivo
SERIE_3 = "#3987e5"        # azul: dado observado (pontos, histogramas)
SERIE_4 = "#c98500"        # âmbar: linha de tendência, destaques

NEUTRO = "#6b7484"         # marca sem significado de estado
CATEGORICA = [SERIE_3, SERIE_4, SERIE_1, SERIE_2]

SIGNIFICATIVO = SERIE_1
INCONCLUSIVO = SERIE_2
OBSERVADO = SERIE_3
TENDENCIA = SERIE_4

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
p, li, label, .stMarkdown {{ color: {TINTA2}; font-size: 0.94rem; }}
strong, b {{ color: {TINTA}; }}
code {{ color: {TINTA}; background: {FUNDO2}; }}

/* números das métricas: tipografia de dado, não de texto corrido */
[data-testid="stMetricValue"] {{
    font-family: {SERIF}; font-size: 1.75rem; color: {TINTA};
    font-variant-numeric: tabular-nums;
}}
[data-testid="stMetricLabel"] p {{ font-size: 0.80rem; color: {TINTA2}; }}
[data-testid="stMetric"] {{ border-left: 2px solid {LINHA}; padding: 2px 0 2px 14px; }}

/* réguas finas no lugar de caixas */
hr {{ border-color: {LINHA}; margin: 1.6rem 0 1.2rem; }}
[data-testid="stExpander"] {{ border: 1px solid {LINHA}; border-radius: 4px; }}
[data-testid="stExpander"] summary {{ font-size: 0.88rem; color: {TINTA2}; }}

/* tabelas: números alinhados e cabeçalho discreto */
[data-testid="stDataFrame"] {{ font-variant-numeric: tabular-nums; }}
[data-testid="stTable"] td, [data-testid="stDataFrame"] td {{ color: {TINTA2}; }}
[data-testid="stCaptionContainer"] p {{ color: {MUDO}; font-size: 0.80rem; }}
[data-testid="stDataFrame"] th {{ color: {TINTA}; }}

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
