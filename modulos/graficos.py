# -*- coding: utf-8 -*-
"""
graficos.py
-----------
Os gráficos do dashboard, todos em Plotly e com o tema de modulos/visual.py.

Regras usadas em todos (para os gráficos parecerem um sistema só)
    - uma escala vertical por gráfico (nada de dois eixos y);
    - significativo = azul cheio; não significativo = cinza (e o p-valor
      aparece escrito ou no balão do mouse, para a cor não ser a única pista);
    - notícias positivas = azul, negativas = âmbar (par validado para
      daltonismo sobre o fundo escuro: ΔE 27);
    - vírgula decimal, como no relatório.
"""
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modulos.visual import FUNDO, FUNDO2, LINHA, MUDO, TINTA, TINTA2

AZUL = "#3987e5"        # significativo / notícias positivas
AMBAR = "#c98500"       # notícias negativas
CINZA = "#5a6271"       # não significativo
FAIXA = "rgba(155,164,178,0.16)"   # faixa do menor efeito detectável


def br(x, casas=3, sinal=False):
    """0.1234 -> '0,123' (com '−' de verdade nos negativos).

    Arredonda "meio para cima" a partir do número escrito (0,0725 -> 0,073), como no
    relatório; o arredondamento do float puro daria 0,072.
    """
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    d = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    if d.is_zero():                      # nada de "−0,00" nem "+0,00"
        return f"{abs(d):.{casas}f}".replace(".", ",")
    s = f"{d:+.{casas}f}" if sinal else f"{d:.{casas}f}"
    return s.replace(".", ",").replace("-", "−")


def _mil(n):
    """4129 -> '4.129'."""
    return f"{int(n):,}".replace(",", ".")


def p_txt(p, rotulo="p"):
    """'p = 0,003' ou 'p < 0,001' (sem o feio 'p = < 0,001')."""
    t = p_br(p)
    return f"{rotulo} {t}" if t.startswith("<") else f"{rotulo} = {t}"


def p_br(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "—"
    if p < 0.001:
        return "< 0,001"
    return br(p, 3 if p < 0.1 else 2)


def _base(fig, altura=360, legenda=True, **kw):
    kw.setdefault("margin", dict(l=10, r=20, t=40 if legenda else 20, b=10))
    # O fundo vai explícito na figura: só no tema, o Streamlit troca pela cor secundária dele.
    kw.setdefault("paper_bgcolor", FUNDO)
    kw.setdefault("plot_bgcolor", FUNDO)
    fig.update_layout(height=altura, separators=",.", showlegend=legenda, **kw)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


# ─────────────────────────────────────────────────────────
# Pergunta 1 — mesmo dia
# ─────────────────────────────────────────────────────────

def por_ativo(tab):
    """Três painéis (D−1, D+0, D+1): r de cada ativo, azul quando p < 0,05."""
    rot = [("dm1", "D−1 (dia anterior)"), ("d0", "D+0 (mesmo pregão)"), ("d1", "D+1 (dia seguinte)")]
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=[r[1] for r in rot])
    ordem = tab.sort_values("r_d0")
    for i, (k, _) in enumerate(rot, start=1):
        sig = ordem[f"p_{k}"] < 0.05
        fig.add_bar(
            x=ordem[f"r_{k}"], y=ordem["ativo"], orientation="h",
            marker=dict(color=np.where(sig, AZUL, CINZA), line=dict(width=0)),
            customdata=np.c_[ordem["empresa"], [p_txt(p) for p in ordem[f"p_{k}"]], ordem["n"]],
            hovertemplate="<b>%{y}</b> · %{customdata[0]}<br>r = %{x:.3f}<br>%{customdata[1]}"
                          "<br>n = %{customdata[2]} pregões<extra></extra>",
            showlegend=False, row=1, col=i)
        fig.add_vline(x=0, line=dict(color=MUDO, width=1), row=1, col=i)
        n_sig = int(sig.sum())
        fig.add_annotation(text=f"{n_sig} de {len(ordem)} com p < 0,05", x=0.5, y=-0.16,
                           xref=f"x{'' if i == 1 else i} domain", yref="paper",
                           showarrow=False, font=dict(size=12, color=TINTA if n_sig else MUDO))
    fig.update_xaxes(range=[-0.06, 0.23], tickformat=".2f", dtick=0.1)
    for a in fig.layout.annotations[:3]:
        a.font = dict(size=13, color=TINTA)
    return _base(fig, 380, legenda=False, bargap=0.35, margin=dict(l=10, r=10, t=40, b=50))


def curva_defasagem(df, ativo="AGRUPADO"):
    d = df[df["ativo"] == ativo].set_index("lag")
    lags = list(range(-5, 6))
    rot = [("D" + (f"{k:+d}" if k else "+0")).replace("-", "−") for k in lags]
    r = [d.loc[k, "r"] if k in d.index else None for k in lags]
    p = [d.loc[k, "p"] if k in d.index else None for k in lags]
    s = [bool(d.loc[k, "sig"]) if k in d.index else False for k in lags]
    comp = [bool(d.loc[k, "complemento"]) if (k in d.index and "complemento" in d) else False for k in lags]
    nota = ["<br><i>calculado depois, fora do pré-registro</i>" if c else "" for c in comp]
    fig = go.Figure(go.Bar(
        x=rot, y=[v if v is not None else 0 for v in r],
        marker=dict(color=[AZUL if x else CINZA for x in s], line=dict(width=[1.5 if c else 0 for c in comp], color=TINTA2),
                    pattern=dict(shape=["/" if c else "" for c in comp], fgcolor=TINTA2, size=6, solidity=0.25)),
        text=[br(v) if (v is not None and sig) else "" for v, sig in zip(r, s)],
        textposition="outside", textfont=dict(color=TINTA, size=12),
        customdata=[(p_txt(x) if x is not None else "não calculado") + n for x, n in zip(p, nota)],
        hovertemplate="<b>%{x}</b><br>r = %{y:.3f}<br>%{customdata}<extra></extra>"))
    for i, v in enumerate(r):
        if v is None:
            fig.add_annotation(x=rot[i], y=0.008, text="não<br>calculado", showarrow=False,
                               font=dict(size=10, color=MUDO))
    fig.add_hline(y=0, line=dict(color=MUDO, width=1))
    fig.update_yaxes(title="correlação (r)", tickformat=".2f")
    return _base(fig, 340, legenda=False, bargap=0.38)


def permutacao(nulos, r_obs, ativo, p):
    fig = go.Figure(go.Histogram(x=nulos, nbinsx=70, marker=dict(color=CINZA, line=dict(width=0)),
                                 hovertemplate="r embaralhado ≈ %{x:.3f}<br>%{y} embaralhamentos<extra></extra>",
                                 name="10.000 embaralhamentos"))
    fig.add_vline(x=r_obs, line=dict(color=AZUL, width=2.5))
    fig.add_annotation(x=r_obs, y=1, yref="paper", text=f"<b>r real = {br(r_obs)}</b><br>{p_txt(p)}",
                       showarrow=False, xanchor="left", xshift=6, yanchor="top",
                       font=dict(color=TINTA, size=12), align="left")
    fig.update_xaxes(title=f"correlação com o sentimento embaralhado — {ativo}", tickformat=".2f")
    fig.update_yaxes(title="quantas vezes")
    return _base(fig, 300, legenda=False, bargap=0.05)


# ─────────────────────────────────────────────────────────
# Pergunta 2 — controles
# ─────────────────────────────────────────────────────────

def placebo(mat):
    z = mat.to_numpy()
    lim = float(np.nanmax(np.abs(z)))
    escala = [[0, AMBAR], [0.5, "#232a35"], [1, AZUL]]
    fig = go.Figure(go.Heatmap(
        z=z, x=list(mat.columns), y=list(mat.index), colorscale=escala, zmin=-lim, zmax=lim,
        xgap=2, ygap=2, text=[[br(v, 2) for v in linha] for linha in z], texttemplate="%{text}",
        textfont=dict(size=11, color=TINTA),
        hovertemplate="notícias de <b>%{y}</b><br>retorno anormal de <b>%{x}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(title=dict(text="r", font=dict(color=MUDO)), tickformat=".2f",
                      tickfont=dict(color=MUDO), thickness=10, outlinewidth=0)))
    for i in range(len(mat)):
        fig.add_shape(type="rect", x0=i - 0.5, x1=i + 0.5, y0=i - 0.5, y1=i + 0.5,
                      line=dict(color=TINTA, width=1.5))
    fig.update_xaxes(title="retorno anormal da empresa…", side="bottom", showgrid=False)
    fig.update_yaxes(title="notícias da empresa…", autorange="reversed", showgrid=False)
    return _base(fig, 470, legenda=False, plot_bgcolor=FUNDO)


def barras_relato(rotulos, rs, ns):
    fig = go.Figure(go.Bar(
        x=rs, y=rotulos, orientation="h", marker=dict(color=[CINZA, AZUL, AMBAR], line=dict(width=0)),
        text=[f"r = {br(r)}   (n = {_mil(n)})" for r, n in zip(rs, ns)],
        textposition="outside", textfont=dict(color=TINTA, size=12),
        hovertemplate="%{y}<br>r = %{x:.3f}<extra></extra>"))
    fig.update_xaxes(range=[0, 0.8], title="correlação no mesmo pregão (8 ativos agrupados)", tickformat=".1f")
    fig.update_yaxes(autorange="reversed")
    return _base(fig, 240, legenda=False, bargap=0.45)


def controles(lista):
    nomes = [c["teste"] for c in lista][::-1]
    rs = [c["r"] for c in lista][::-1]
    ps = [c["p_holm"] if c["p_holm"] is not None else c["p"] for c in lista][::-1]
    fig = go.Figure()
    fig.add_scatter(x=rs, y=nomes, mode="markers+text", marker=dict(size=13, color=AZUL, line=dict(color=FUNDO, width=2)),
                    text=[f"  r = {br(r)}" for r in rs], textposition="middle right",
                    textfont=dict(color=TINTA, size=12),
                    customdata=[p_txt(p) for p in ps],
                    hovertemplate="<b>%{y}</b><br>r = %{x:.3f}<br>%{customdata}<extra></extra>")
    fig.add_vline(x=0, line=dict(color=MUDO, width=1))
    fig.update_xaxes(range=[-0.02, 0.3], title="correlação (r) — todos com p < 0,05", tickformat=".2f")
    return _base(fig, 300, legenda=False)


# ─────────────────────────────────────────────────────────
# Pergunta 3 — direção
# ─────────────────────────────────────────────────────────

def direcao(testes, medida="lexico"):
    grupos = [("preco_antes", "O PREÇO ANDA ANTES DA NOTÍCIA?"), ("noticia_antes", "A NOTÍCIA ANTECIPA O PREÇO?")]
    rot = []
    fig = go.Figure()
    y = 0
    for g, titulo in grupos:
        sub = [t for t in testes if t["sentido"] == g]
        rot.append((y, f"<b>{titulo}</b>"))
        y -= 1
        for t in sub:
            r = t["r"] if medida == "lexico" else t["r_finbert"]
            p = t["p"] if medida == "lexico" else t["p_finbert"]
            if r is None:
                y -= 1
                continue
            fig.add_shape(type="rect", x0=-t["mde"], x1=t["mde"], y0=y - 0.28, y1=y + 0.28,
                          fillcolor=FAIXA, line=dict(width=0), layer="below")
            sig = p < 0.05
            fig.add_scatter(x=[r], y=[y], mode="markers",
                            marker=dict(size=13, color=AZUL if sig else FUNDO,
                                        line=dict(color=AZUL if sig else TINTA2, width=2)),
                            hovertemplate=(f"<b>{t['nome']}</b><br>{t['escala']}<br>r = {br(r)}<br>{p_txt(p)}"
                                           f"<br>n = {t['n']}<br>menor efeito detectável = {br(t['mde'], 3)}<extra></extra>"),
                            showlegend=False)
            fig.add_annotation(x=0.215, y=y, text=f"r = {br(r)}   {p_txt(p)}   n = {_mil(t['n'])}",
                               showarrow=False, xanchor="left",
                               font=dict(size=12, color=TINTA if sig else MUDO))
            rot.append((y, t["nome"]))
            y -= 1
        y -= 0.4
    fig.add_vline(x=0, line=dict(color=MUDO, width=1))
    fig.update_yaxes(tickvals=[a for a, _ in rot], ticktext=[b for _, b in rot], showgrid=False,
                     range=[y + 0.6, 0.6])
    fig.update_xaxes(range=[-0.17, 0.42], tickvals=[-0.1, 0, 0.1, 0.2], tickformat=".1f",
                     title="correlação (r)")
    return _base(fig, 470, legenda=False, margin=dict(l=10, r=10, t=10, b=10))


def perfil_horario(df):
    fig = go.Figure()
    fig.add_vrect(x0=0, x1=1, fillcolor="rgba(214,219,228,0.07)", line_width=0)
    fig.add_annotation(x=0.5, y=1, yref="paper", text="hora da<br>publicação", showarrow=False,
                       yanchor="top", font=dict(size=11, color=MUDO))
    for g, cor, nome in (("pos", AZUL, "notícias mais positivas"), ("neg", AMBAR, "notícias mais negativas")):
        d = df[df["grupo"] == g].set_index("hora_relativa")["retorno_medio_pct"]
        xs, ys, acc = [-3], [0.0], 0.0
        for h in range(-3, 4):
            acc += float(d.get(h, 0))
            xs.append(h + 1)
            ys.append(acc)
        fig.add_scatter(x=xs, y=ys, mode="lines+markers", line=dict(color=cor, width=2.5),
                        marker=dict(size=8, color=cor, line=dict(color=FUNDO, width=2)), name=nome,
                        hovertemplate=nome + "<br>%{y:.2f}% acumulado<extra></extra>")
        fig.add_annotation(x=xs[-1], y=ys[-1], text=nome.split()[-1], showarrow=False, xanchor="left",
                           xshift=8, font=dict(color=TINTA2, size=12))
    fig.add_hline(y=0, line=dict(color=MUDO, width=1))
    fig.update_xaxes(tickvals=[-3, -2, -1, 0, 1, 2, 3, 4], range=[-3.3, 5.4],
                     ticktext=["−3 h", "−2 h", "−1 h", "", "", "+1 h", "+2 h", "+3 h"])
    fig.update_yaxes(title="retorno anormal acumulado (%)", tickformat=".2f")
    return _base(fig, 380)


def perfil_minuto(df):
    fig = go.Figure()
    for g, cor, nome, rgba in (("pos", AZUL, "notícias mais positivas", "rgba(57,135,229,0.16)"),
                               ("neg", AMBAR, "notícias mais negativas", "rgba(201,133,0,0.16)")):
        d = df[df["grupo"] == g].sort_values("fronteira_min")
        x = d["fronteira_min"].tolist()
        fig.add_scatter(x=x + x[::-1], y=d["ic95_alto"].tolist() + d["ic95_baixo"].tolist()[::-1],
                        fill="toself", fillcolor=rgba, line=dict(width=0), hoverinfo="skip", showlegend=False)
        fig.add_scatter(x=x, y=d["nivel_pct"], mode="lines", line=dict(color=cor, width=2.2), name=nome,
                        hovertemplate="minuto %{x}<br>%{y:.3f}%<extra>" + nome + "</extra>")
    fig.add_vline(x=0, line=dict(color=TINTA2, width=1, dash="dash"))
    fig.add_annotation(x=0, y=1, yref="paper", text="publicação", showarrow=False, xanchor="left",
                       xshift=4, yanchor="top", font=dict(size=11, color=MUDO))
    fig.add_hline(y=0, line=dict(color=MUDO, width=1))
    fig.update_xaxes(title="minutos em relação à publicação (faixa clara: intervalo de 95%)", dtick=5)
    fig.update_yaxes(title="retorno anormal acumulado (%)", tickformat=".2f")
    return _base(fig, 380)


def esquema_direcao():
    """Desenho dos testes de direção: o que é comparado antes e depois da notícia."""
    fig = go.Figure()
    linhas = [
        (2, "Abertura", [("pregão do dia D", -3.0, -1.0, CINZA, "preço → notícia?"),
                         ("noite (bolsa fechada)", -1.0, 1.0, None, ""),
                         ("abertura de D+1", 1.0, 3.0, CINZA, "notícia → preço?")]),
        (1, "60 minutos", [("hora anterior", -2.2, -0.45, CINZA, "preço → notícia?"),
                           ("fica<br>fora", -0.45, 0.45, None, ""),
                           ("hora seguinte", 0.45, 2.2, CINZA, "notícia → preço?")]),
        (0, "1 minuto", [("minutos −5 a −1", -2.2, -0.15, CINZA, "preço → notícia?"),
                         ("", -0.15, 0.15, None, ""),
                         ("minutos +1 a +5", 0.15, 2.2, CINZA, "notícia → preço?")]),
    ]
    for y, nome, blocos in linhas:
        fig.add_annotation(x=-3.35, y=y, text=f"<b>{nome}</b>", showarrow=False, xanchor="right",
                           font=dict(color=TINTA, size=12))
        for rot, x0, x1, cor, pergunta in blocos:
            antes = x1 <= 0.01 and cor
            depois = x0 >= -0.01 and cor
            fill = "rgba(57,135,229,0.22)" if antes else ("rgba(201,133,0,0.22)" if depois else FUNDO2)
            borda = AZUL if antes else (AMBAR if depois else LINHA)
            fig.add_shape(type="rect", x0=x0, x1=x1, y0=y - 0.28, y1=y + 0.28, fillcolor=fill,
                          line=dict(color=borda, width=1))
            if rot:
                fig.add_annotation(x=(x0 + x1) / 2, y=y, text=rot, showarrow=False,
                                   font=dict(size=11, color=TINTA2))
            if pergunta:
                fig.add_annotation(x=(x0 + x1) / 2, y=y + 0.42, text=pergunta, showarrow=False,
                                   font=dict(size=11, color=MUDO))
    fig.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=2.6, line=dict(color=TINTA, width=2))
    fig.add_annotation(x=0, y=2.75, text="<b>notícia</b>", showarrow=False, font=dict(color=TINTA, size=13))
    fig.update_xaxes(visible=False, range=[-4.6, 3.2])
    fig.update_yaxes(visible=False, range=[-0.6, 3.0])
    return _base(fig, 300, legenda=False, margin=dict(l=10, r=10, t=10, b=10))


# ─────────────────────────────────────────────────────────
# Método e medida
# ─────────────────────────────────────────────────────────

def curva_poder(curva, r_estudo=None):
    fig = go.Figure()
    fig.add_scatter(x=curva["r"], y=curva["teorico"], mode="lines", line=dict(color=TINTA2, width=2),
                    name="poder teórico (fórmula)", hovertemplate="r = %{x:.3f}<br>%{y:.1f}%<extra>teórico</extra>")
    fig.add_scatter(x=curva["r"], y=curva["medido"], mode="markers",
                    marker=dict(size=10, color=AZUL, line=dict(color=FUNDO, width=2)),
                    name="poder medido (300 simulações por ponto)",
                    hovertemplate="r = %{x:.3f}<br>%{y:.1f}% detectado<extra>medido</extra>")
    fig.add_hline(y=80, line=dict(color=MUDO, width=1, dash="dot"))
    fig.add_annotation(x=0.5, y=80, text="meta: 80%", showarrow=False, xanchor="right", yanchor="bottom",
                       font=dict(color=MUDO, size=11))
    fig.update_xaxes(title="tamanho do efeito (r) — amostra de 400 dias", tickformat=".2f")
    fig.update_yaxes(title="chance de detectar (%)", range=[0, 105])
    return _base(fig, 340)


def mde_por_n(n_marcado):
    from math import sqrt, tanh
    ns = np.arange(20, 5001, 10)
    z = 1.959964 + 0.841621
    mde = np.tanh(z / np.sqrt(ns - 3))
    fig = go.Figure(go.Scatter(x=ns, y=mde, mode="lines", line=dict(color=AZUL, width=2.5),
                               hovertemplate="n = %{x}<br>menor r detectável = %{y:.3f}<extra></extra>"))
    m = tanh(z / sqrt(n_marcado - 3))
    fig.add_scatter(x=[n_marcado], y=[m], mode="markers", marker=dict(size=13, color=TINTA, line=dict(color=FUNDO, width=2)),
                    hoverinfo="skip")
    fig.add_annotation(x=n_marcado, y=m, text=f"n = {_mil(n_marcado)}: r ≥ {br(m)}",
                       showarrow=True, arrowcolor=MUDO, ax=-70, ay=-50, font=dict(color=TINTA, size=12))
    fig.update_xaxes(title="número de observações (n)", type="log", tickvals=[20, 50, 100, 200, 500, 1000, 2000, 5000])
    fig.update_yaxes(title="menor efeito detectável (r)", tickformat=".2f", range=[0, 0.6])
    return _base(fig, 320, legenda=False)


def kappa(val):
    nomes = ["léxico<br>(medida principal)", "FinBERT-PT-BR<br>(modelo de linguagem)"]
    ks = [val["lexico"]["kappa"], val["finbert"]["kappa"]]
    ics = [val["lexico"]["ic"], val["finbert"]["ic"]]
    fig = go.Figure(go.Bar(
        x=nomes, y=ks, marker=dict(color=AZUL, line=dict(width=0)), width=0.45,
        error_y=dict(type="data", symmetric=False, array=[i[1] - k for i, k in zip(ics, ks)],
                     arrayminus=[k - i[0] for i, k in zip(ics, ks)], color=TINTA, thickness=1.5, width=10),
        text=[br(k, 2) for k in ks], textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=15),
        customdata=[f"{br(i[0], 2)} a {br(i[1], 2)}" for i in ics],
        hovertemplate="%{x}<br>kappa = %{y:.3f}<br>intervalo de 95%: %{customdata}<extra></extra>"))
    for y0, y1, nome in ((0.21, 0.40, "razoável"), (0.41, 0.60, "moderada")):
        fig.add_hrect(y0=y0, y1=y1, fillcolor="rgba(214,219,228,0.04)", line_width=0)
        fig.add_annotation(x=1.45, y=(y0 + y1) / 2, text=nome, showarrow=False, xanchor="left",
                           font=dict(color=MUDO, size=11))
    fig.update_yaxes(title="kappa reponderado", range=[0, 0.65], tickformat=".1f")
    fig.update_xaxes(range=[-0.5, 1.9])
    return _base(fig, 340, legenda=False)


def contribuicoes(termos):
    """Barras do valor final de cada termo encontrado na manchete digitada."""
    nomes = [t["termo"] for t in termos]
    vals = [t["valor_final"] for t in termos]
    fig = go.Figure(go.Bar(x=vals, y=nomes, orientation="h",
                           marker=dict(color=[AZUL if v > 0 else AMBAR for v in vals], line=dict(width=0)),
                           text=[br(v, 2, sinal=True) for v in vals], textposition="outside",
                           textfont=dict(color=TINTA, size=12),
                           hovertemplate="%{y}: %{x:+.2f}<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=MUDO, width=1))
    fig.update_xaxes(range=[-1.25, 1.25], title="contribuição de cada termo (−1 a +1)", tickformat=".1f")
    fig.update_yaxes(autorange="reversed")
    return _base(fig, 90 + 42 * len(termos), legenda=False, bargap=0.4)


def simulacao(x, y, r):
    fig = go.Figure(go.Scatter(x=x, y=y, mode="markers", marker=dict(size=6, color=AZUL, opacity=0.55),
                               hoverinfo="skip"))
    a, b = np.polyfit(x, y, 1)
    xs = np.array([x.min(), x.max()])
    fig.add_scatter(x=xs, y=a * xs + b, mode="lines", line=dict(color=AMBAR, width=2), hoverinfo="skip")
    fig.update_xaxes(title="sentimento simulado (padronizado)")
    fig.update_yaxes(title="retorno simulado (padronizado)")
    return _base(fig, 320, legenda=False)


# ─────────────────────────────────────────────────────────
# Dados
# ─────────────────────────────────────────────────────────

def preco_e_sentimento(precos, serie, ativo):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.62, 0.38],
                        subplot_titles=[f"Preço de fechamento de {ativo} (R$)", "Sentimento médio das notícias do pregão"])
    fig.add_scatter(x=precos.index, y=precos.values, mode="lines", line=dict(color=TINTA2, width=1.6),
                    hovertemplate="%{x|%d/%m/%Y}<br>R$ %{y:.2f}<extra></extra>", row=1, col=1)
    s = serie.dropna(subset=["sentimento"])
    fig.add_bar(x=s["data"], y=s["sentimento"],
                marker=dict(color=np.where(s["sentimento"] >= 0, AZUL, AMBAR), line=dict(width=0)),
                customdata=s["n_noticias"],
                hovertemplate="%{x|%d/%m/%Y}<br>sentimento médio %{y:+.2f}<br>%{customdata} notícia(s)<extra></extra>",
                row=2, col=1)
    fig.update_yaxes(range=[-1.05, 1.05], tickformat=".1f", row=2, col=1)
    for a in fig.layout.annotations:
        a.font = dict(size=12, color=TINTA)
        a.x = 0
        a.xanchor = "left"
    return _base(fig, 520, legenda=False, bargap=0)


def dispersao(serie, lag, ativo):
    col = "retorno" if lag == 0 else f"retorno_lag_{lag}"
    s = serie.dropna(subset=["sentimento", col])
    x, y = s["sentimento"].to_numpy(), 100 * s[col].to_numpy()
    fig = go.Figure(go.Scatter(x=x, y=y, mode="markers",
                               marker=dict(size=7, color=AZUL, opacity=0.5, line=dict(width=0)),
                               customdata=np.c_[s["data"].dt.strftime("%d/%m/%Y"), s["n_noticias"]],
                               hovertemplate="%{customdata[0]}<br>sentimento %{x:+.2f}<br>retorno %{y:+.2f}%"
                                             "<br>%{customdata[1]} notícia(s)<extra></extra>"))
    if len(s) > 2:
        a, b = np.polyfit(x, y, 1)
        xs = np.array([-1, 1])
        fig.add_scatter(x=xs, y=a * xs + b, mode="lines", line=dict(color=AMBAR, width=2.5), hoverinfo="skip")
    rot = ("D" + (f"{lag:+d}" if lag else "+0")).replace("-", "−")
    fig.update_xaxes(title="sentimento médio das notícias do pregão D", range=[-1.05, 1.05], tickformat=".1f")
    fig.update_yaxes(title=f"retorno de {ativo} em {rot} (%)", tickformat=".1f")
    return _base(fig, 400, legenda=False)
